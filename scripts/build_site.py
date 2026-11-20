#!/usr/bin/env python3
"""Build the daily site from reports/YYYY-MM-DD.md into _site/.

Parses each report's category tables into item cards for an elegant,
editorial layout. Falls back to plain markdown rendering when a report
has no parseable tables.

Requires: pip install markdown
"""
import html
import os
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("missing dependency: pip install markdown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
OUT = os.path.join(ROOT, "_site")

CSS = """
:root{
  --bg:#f6f6f4; --surface:#fff; --ink:#1b1b18; --muted:#71716a; --line:#e8e6e1;
  --accent:#4f46e5; --accent2:#8b5cf6; --soft:#eef2ff; --chip:#f3f2ee;
  --shadow:0 1px 2px rgba(20,20,30,.05),0 10px 30px rgba(20,20,30,.06);
  --shadow-lg:0 2px 4px rgba(20,20,30,.06),0 18px 44px rgba(20,20,30,.10);
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0d0e11; --surface:#15171c; --ink:#edece8; --muted:#a0a099; --line:#26282f;
    --accent:#a5b4fc; --accent2:#c4b5fd; --soft:#1e2033; --chip:#1d1f26;
    --shadow:0 1px 2px rgba(0,0,0,.35),0 10px 30px rgba(0,0,0,.35);
    --shadow-lg:0 2px 4px rgba(0,0,0,.4),0 18px 44px rgba(0,0,0,.45); }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif;
  line-height:1.75;font-size:16px;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
header.top{position:sticky;top:0;z-index:30;backdrop-filter:blur(12px);
  background:color-mix(in srgb,var(--bg) 84%,transparent);border-bottom:1px solid var(--line)}
header.top .bar{max-width:960px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:12px}
.logo{width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;flex:none}
header.top .name{font-weight:700}
header.top .sub{color:var(--muted);font-size:12.5px;margin-left:auto}
main{max-width:960px;margin:0 auto;padding:30px 20px 70px}
.hero{padding:14px 2px 4px}
.hero .kicker{font-size:12.5px;letter-spacing:.16em;color:var(--accent);font-weight:700;text-transform:uppercase}
.hero h1{font-family:Georgia,"Songti SC","Noto Serif SC",serif;font-size:36px;line-height:1.28;margin:8px 0 10px}
.hero p.lede{color:var(--muted);font-size:16px;margin:0;max-width:46em}
.summary{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);
  padding:20px 24px;margin:24px 0 6px;font-size:15.3px}
.summary .tag{display:inline-block;font-size:12px;font-weight:700;color:var(--accent);
  background:var(--soft);padding:3px 10px;border-radius:999px;margin-bottom:8px}
.summary p{margin:6px 0}
.search{margin:20px 0 4px;position:relative}
.search input{width:100%;padding:13px 16px 13px 42px;font-size:15.5px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:999px;box-shadow:var(--shadow);outline:none}
.search input:focus{border-color:var(--accent)}
.search svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);opacity:.45}
nav.sections{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 6px;position:sticky;top:57px;z-index:20;
  padding:8px 0;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px)}
nav.sections a{font-size:13.5px;color:var(--ink);background:var(--surface);border:1px solid var(--line);
  padding:6px 14px;border-radius:999px;box-shadow:var(--shadow)}
nav.sections a:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
nav.sections a b{color:var(--accent);font-weight:700}
section.cat{margin-top:40px;scroll-margin-top:130px}
section.cat>h2{font-family:Georgia,"Songti SC","Noto Serif SC",serif;font-size:23px;margin:0 0 4px;
  display:flex;align-items:baseline;gap:10px}
section.cat>h2 .n{font-size:13px;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));
  width:24px;height:24px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;
  font-family:inherit;transform:translateY(-2px);flex:none}
section.cat>.note{color:var(--muted);font-size:14.5px;margin:6px 0 12px}
.cards{display:grid;gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);
  padding:18px 22px;transition:box-shadow .18s ease,transform .18s ease}
.card:hover{box-shadow:var(--shadow-lg);transform:translateY(-1px)}
.card h3{font-size:17.5px;line-height:1.5;margin:0 0 8px}
.card h3 a{color:var(--ink)}
.card h3 a:hover{color:var(--accent);text-decoration:none}
.meta{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 9px}
.badge{font-size:12.3px;padding:2.5px 10px;border-radius:999px;background:var(--chip);color:var(--muted)}
.badge.src{background:var(--soft);color:var(--accent);font-weight:600}
.card p{margin:5px 0;font-size:15px}
.card .more{margin-top:10px;font-size:14px}
.card .more a{font-weight:600}
.card details{margin-top:8px;font-size:14px;color:var(--muted)}
.card details summary{cursor:pointer;color:var(--accent);font-size:13.5px}
.plain{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);
  padding:8px 26px 22px;margin-top:16px;font-size:15px}
.plain h2{font-size:20px;margin:24px 0 8px}
.plain h3{font-size:16.5px;margin:20px 0 6px}
details.notes{margin-top:38px;background:var(--surface);border:1px solid var(--line);border-radius:16px;
  box-shadow:var(--shadow);padding:16px 24px;font-size:14.3px;color:var(--muted)}
details.notes summary{cursor:pointer;font-weight:650;color:var(--ink);font-size:15px}
details.notes h2{font-size:16.5px;color:var(--ink)}
details.notes table{display:block;overflow-x:auto;border-collapse:collapse;font-size:13.3px}
details.notes th,details.notes td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.archive{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:20px 0 0}
.archive span{color:var(--muted);font-size:13.5px}
.archive a{font-size:13.5px;background:var(--surface);border:1px solid var(--line);
  padding:5px 12px;border-radius:999px;color:var(--ink);box-shadow:var(--shadow)}
.archive a.cur{border-color:var(--accent);color:var(--accent);font-weight:650}
footer{max-width:960px;margin:0 auto;padding:0 20px 42px;color:var(--muted);font-size:13px}
.back{display:inline-block;margin:4px 0 10px;font-size:14px}
@media (max-width:640px){
  .hero h1{font-size:28px} .card{padding:16px 18px} .summary{padding:16px 18px}
  header.top .sub{display:none} nav.sections{top:57px}
}
"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body>
<header class="top"><div class="bar">
<div class="logo">L</div><div class="name">LLM Infrastructure 日报</div>
<div class="sub">每天 09:00 · Asia/Shanghai 更新</div>
</div></header>
<main>{main}</main>
<footer>内容由每日定时研究汇总生成 · 每条均附原文链接 · 无法核实的信息会明确标注，不编造</footer>
</body></html>
"""

SEARCH_SVG = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/>'
              '<path d="m20 20-3.8-3.8"/></svg>')

FILTER_JS = """
<script>
function applyFilter(q){
  q=(q||'').trim().toLowerCase();
  document.querySelectorAll('.card').forEach(function(el){
    el.style.display = (!q || el.textContent.toLowerCase().includes(q)) ? '' : 'none';
  });
  document.querySelectorAll('section.cat').forEach(function(sec){
    var any=false;
    sec.querySelectorAll('.card').forEach(function(c){ if(c.style.display!=='none') any=true; });
    sec.style.display = any ? '' : 'none';
  });
}
</script>
"""

URL_RE = re.compile(r"https?://[^\s)\]]+")


def inline(text):
    """Render inline markdown to HTML (no surrounding <p>)."""
    out = markdown.markdown(text.strip(), extensions=["tables"])
    out = re.sub(r"^\s*<p>", "", out)
    out = re.sub(r"</p>\s*$", "", out)
    return out


def plain(text):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = t.replace("**", "").replace("`", "")
    return html.escape(t.strip())


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep_row(cells):
    return all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c != "") and cells


def parse_report(text):
    """Return dict with title, intro lines, sections: [(level, heading, [blocks])].
    Blocks are ('p', text) or ('table', header, rows)."""
    lines = text.splitlines()
    title = ""
    intro = []
    sections = []
    cur = None  # (level, heading, blocks)
    buf = []

    def flush_para():
        nonlocal buf
        if buf:
            txt = "\n".join(buf).strip()
            if txt:
                if cur is None:
                    intro.append(txt)
                else:
                    cur[2].append(("p", txt))
            buf = []

    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            heading = m.group(2).strip()
            if level == 1 and not title:
                title = heading
                cur = None
            else:
                cur = (level, heading, [])
                sections.append(cur)
            i += 1
            continue
        if line.strip().startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            flush_para()
            header = split_row(line)
            rows = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = split_row(lines[i])
                if not is_sep_row(cells):
                    rows.append(cells)
                i += 1
            if cur is None:
                intro.append("")
                cur = (2, "", [])
                sections.append(cur)
            cur[2].append(("table", header, rows))
            continue
        if line.strip() in ("---", "***", ""):
            flush_para()
            i += 1
            continue
        buf.append(line)
        i += 1
    flush_para()
    return {"title": title, "intro": intro, "sections": sections}


def col_index(header, *keywords):
    for idx, h in enumerate(header):
        for kw in keywords:
            if kw in h:
                return idx
    return None


def render_card(header, row):
    def cell(idx):
        return row[idx] if idx is not None and idx < len(row) else ""

    ti = col_index(header, "标题", "Title", "作者")
    si = col_index(header, "来源", "Source")
    tmi = col_index(header, "时间", "Time")
    wi = col_index(header, "takeaway", "摘要", "内容")
    li = col_index(header, "链接", "Link")
    vi = col_index(header, "核实", "状态")

    title_html = inline(cell(ti)) if ti is not None else "（无标题）"
    link = ""
    link_cell = cell(li)
    m = URL_RE.search(link_cell or "")
    if m:
        link = m.group(0)
    if not link:
        m2 = URL_RE.search(cell(ti) or "")
        if m2:
            link = m2.group(0)
    title_out = f'<a href="{html.escape(link)}" target="_blank" rel="noopener">{title_html}</a>' if link else title_html

    badges = ""
    if si is not None and cell(si):
        badges += f'<span class="badge src">{inline(cell(si))}</span>'
    if tmi is not None and cell(tmi):
        t = plain(cell(tmi))
        t = re.sub(r"\s+", " ", t)[:80]
        badges += f'<span class="badge">{html.escape(t)}</span>'
    if vi is not None and cell(vi):
        badges += f'<span class="badge">{inline(cell(vi))}</span>'

    takeaway = inline(cell(wi)) if wi is not None and cell(wi) else ""
    more = f'<div class="more"><a href="{html.escape(link)}" target="_blank" rel="noopener">原文链接 →</a></div>' if link else ""
    return (
        f'<div class="card"><h3>{title_out}</h3>'
        f'<div class="meta">{badges}</div>'
        f"<p>{takeaway}</p>{more}</div>"
    )


def render_report(text, date, dates, is_index):
    rep = parse_report(text)
    cats = []          # (anchor, label, count, html)
    notes_html = []    # trailing sections rendered in a collapsible block
    summary_html = ""
    pending_h2 = None

    def cat_label(heading):
        m = re.search(r"（([^）]+)）", heading)
        if m:
            return m.group(1).split("/")[0].strip()
        return re.sub(r"^\d+\)\s*", "", heading).strip()

    idx = 0
    for level, heading, blocks in rep["sections"]:
        if level == 2 and heading.lower().startswith("summary"):
            body = "".join(f"<p>{inline(b[1])}</p>" for b in blocks if b[0] == "p")
            summary_html = f'<div class="summary"><span class="tag">本期摘要</span>{body}</div>'
            continue
        if level == 3:
            idx += 1
            anchor = f"cat{idx}"
            label = cat_label(heading)
            parts = []
            count = 0
            for b in blocks:
                if b[0] == "p":
                    if b[1].strip():
                        parts.append(f'<div class="note">{inline(b[1])}</div>')
                else:
                    count += len(b[2])
                    cards = "".join(render_card(b[1], r) for r in b[2])
                    parts.append(f'<div class="cards">{cards}</div>')
            cats.append((anchor, label, count,
                         f'<section class="cat" id="{anchor}"><h2><span class="n">{idx}</span>{html.escape(label)}</h2>'
                         + "".join(parts) + "</section>"))
            continue
        # other h2 sections (verification notes, excluded list, sources) -> collapsible
        if level == 2 and heading:
            inner = []
            for b in blocks:
                if b[0] == "p":
                    inner.append(markdown.markdown(b[1], extensions=["tables"]))
                else:
                    tbl = [b[1]] + b[2]
                    md_tbl = "\n".join("| " + " | ".join(r) + " |" for r in tbl)
                    inner.append(markdown.markdown(md_tbl, extensions=["tables"]))
            notes_html.append(f"<h2>{html.escape(heading)}</h2>" + "".join(inner))

    if not cats:
        # fallback: plain markdown in a card container
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "toc"])
        return f'<div class="plain">{body}</div>'

    nav = "".join(
        f'<a href="#{a}">{html.escape(l)} <b>{c}</b></a>' for a, l, c, _ in cats
    )
    hero_title = rep["title"] or "LLM 基础设施最新动态"
    main = (
        f'<section class="hero"><div class="kicker">Daily Briefing · {date}</div>'
        f"<h1>{html.escape(hero_title)}</h1>"
        f'<p class="lede">过去 24 小时 LLM infrastructure 领域的可验证新内容：技术报告、论文、行业新闻、X 动态与热点。</p></section>'
        f"{summary_html}"
        f'<div class="search">{SEARCH_SVG}<input type="search" placeholder="搜索本期内容：公司、论文、框架…" oninput="applyFilter(this.value)"></div>'
        f'<nav class="sections">{nav}</nav>'
        + "".join(c[3] for c in cats)
    )
    if notes_html:
        main += ('<details class="notes"><summary>核验说明、缺口与来源清单</summary>'
                 + "".join(notes_html) + "</details>")
    if is_index:
        links = "".join(
            f'<a class="{"cur" if d == date else ""}" href="reports/{d}.html">{d}</a>' for d in dates
        )
        main += f'<div class="archive"><span>往期归档</span>{links}</div>'
    main += FILTER_JS
    return main


def main():
    os.makedirs(os.path.join(OUT, "reports"), exist_ok=True)
    dates = sorted(
        (fn[:-3] for fn in os.listdir(REPORTS) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", fn)),
        reverse=True,
    )
    if not dates:
        sys.exit("no reports found")
    texts = {}
    for d in dates:
        with open(os.path.join(REPORTS, f"{d}.md"), encoding="utf-8") as f:
            texts[d] = f.read()
    for d in dates:
        body = render_report(texts[d], d, dates, is_index=False)
        body = f'<a class="back" href="../index.html">← 返回首页</a>' + body
        page = PAGE.format(title=f"LLM Infrastructure 日报 · {d}", css=CSS, main=body)
        with open(os.path.join(OUT, "reports", f"{d}.html"), "w", encoding="utf-8") as f:
            f.write(page)
    latest = dates[0]
    body = render_report(texts[latest], latest, dates, is_index=True)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGE.format(title="LLM Infrastructure 日报", css=CSS, main=body))
    print(f"built {len(dates)} report(s), latest {latest}")


if __name__ == "__main__":
    main()
