#!/usr/bin/env python3
"""Build an elegant static site from reports/YYYY-MM-DD.md into _site/.

Requires: pip install markdown
"""
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
  --bg:#f7f7f5; --surface:#ffffff; --ink:#191919; --muted:#6b6b66;
  --line:#e7e5e0; --accent:#4f46e5; --accent-soft:#eef2ff;
  --chip:#f1f0ec; --shadow:0 1px 2px rgba(16,16,20,.04),0 8px 24px rgba(16,16,20,.06);
  --radius:14px;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0e0f12; --surface:#16181d; --ink:#eceae6; --muted:#9b9a94;
    --line:#26282f; --accent:#a5b4fc; --accent-soft:#1e2030; --chip:#1c1e24;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35); }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif;
  line-height:1.75;font-size:16px;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:20;backdrop-filter:blur(10px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}
header.top .bar{max-width:920px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:14px}
.logo{width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
  color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex:none}
header.top .name{font-weight:650;letter-spacing:.2px}
header.top .sub{color:var(--muted);font-size:12.5px;margin-left:auto;text-align:right}
main{max-width:920px;margin:0 auto;padding:28px 20px 72px}
.hero{padding:26px 4px 8px}
.hero h1{font-family:Georgia,"Songti SC","Noto Serif SC",serif;font-size:34px;line-height:1.3;margin:0 0 8px;font-weight:700}
.hero p{color:var(--muted);margin:0;font-size:15px}
.search{margin:22px 0 6px;position:relative}
.search input{width:100%;padding:13px 16px 13px 42px;font-size:15.5px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:999px;box-shadow:var(--shadow);outline:none}
.search input:focus{border-color:var(--accent)}
.search svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);opacity:.45}
nav.sections{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 4px}
nav.sections a{font-size:13.5px;color:var(--ink);background:var(--chip);
  padding:6px 13px;border-radius:999px;border:1px solid var(--line)}
nav.sections a:hover{background:var(--accent-soft);text-decoration:none}
.archive{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:18px 0 2px}
.archive span{color:var(--muted);font-size:13.5px}
.archive a{font-size:13.5px;background:var(--surface);border:1px solid var(--line);
  padding:5px 12px;border-radius:999px;color:var(--ink);box-shadow:var(--shadow)}
.archive a.cur{border-color:var(--accent);color:var(--accent);font-weight:600}
article{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:10px 30px 30px;margin-top:18px}
article h1{font-family:Georgia,"Songti SC","Noto Serif SC",serif;font-size:27px;line-height:1.4;margin:22px 0 10px}
article h2{font-size:20.5px;margin:38px 0 12px;padding-top:22px;border-top:1px solid var(--line);
  display:flex;align-items:center;gap:9px;scroll-margin-top:76px}
article h2:first-of-type{border-top:none;padding-top:4px}
article h3{font-size:18px;margin:30px 0 10px;padding:9px 14px;background:var(--chip);
  border-left:3.5px solid var(--accent);border-radius:0 10px 10px 0;scroll-margin-top:76px}
article p{margin:9px 0}
article ul,article ol{padding-left:22px}
article li{margin:5px 0}
article blockquote{margin:14px 0;padding:12px 16px;background:var(--accent-soft);
  border-left:3px solid var(--accent);border-radius:0 10px 10px 0;color:var(--ink)}
article blockquote p{margin:4px 0}
article code{background:var(--chip);padding:1.5px 6px;border-radius:6px;font-size:.88em;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
article pre{background:var(--chip);padding:14px 16px;border-radius:10px;overflow-x:auto}
article pre code{background:none;padding:0}
article hr{border:none;border-top:1px solid var(--line);margin:28px 0}
article table{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;line-height:1.65;
  display:block;overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:14px 0}
article th{background:var(--chip);font-weight:650;text-align:left;padding:10px 12px;white-space:nowrap}
article td{padding:10px 12px;vertical-align:top;border-top:1px solid var(--line)}
article tr:first-child td{border-top:none}
footer{max-width:920px;margin:0 auto;padding:0 20px 40px;color:var(--muted);font-size:13px}
.back{display:inline-block;margin:20px 0 0;font-size:14px}
@media (max-width:640px){
  .hero h1{font-size:27px} article{padding:6px 18px 24px} article h1{font-size:23px}
  header.top .sub{display:none}
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
  document.querySelectorAll('article table tbody tr, article li, article > p').forEach(function(el){
    el.style.display = (!q || el.textContent.toLowerCase().includes(q)) ? '' : 'none';
  });
}
</script>
"""


def render_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    body = md.convert(text)
    flat = []

    def walk(tokens):
        for tok in tokens:
            flat.append(tok)
            walk(tok.get("children", []))

    walk(getattr(md, "toc_tokens", []))

    def clean(name):
        m = re.search(r"（([^）]+)）", name)
        if m:
            return m.group(1).split("/")[0].strip()
        return re.sub(r"^\d+\)\s*", "", name).strip()

    sections = [(t["id"], clean(t["name"])) for t in flat if t["level"] == 3]
    if not sections:
        sections = [(t["id"], clean(t["name"])) for t in flat if t["level"] == 2]
    return body, sections


def nav_html(sections, prefix=""):
    if not sections:
        return ""
    links = "".join(f'<a href="{prefix}#{sid}">{name}</a>' for sid, name in sections)
    return f'<nav class="sections">{links}</nav>'


def archive_html(dates, current):
    links = "".join(
        f'<a class="{"cur" if d == current else ""}" href="reports/{d}.html">{d}</a>'
        for d in dates
    )
    return f'<div class="archive"><span>往期归档</span>{links}</div>'


def main():
    os.makedirs(os.path.join(OUT, "reports"), exist_ok=True)
    dates = sorted(
        (fn[:-3] for fn in os.listdir(REPORTS) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", fn)),
        reverse=True,
    )
    if not dates:
        sys.exit("no reports found")
    rendered = {d: render_md(os.path.join(REPORTS, f"{d}.md")) for d in dates}

    for d in dates:
        body, sections = rendered[d]
        main_html = (
            f'<a class="back" href="../index.html">← 返回首页</a>'
            f"{nav_html(sections)}"
            f"<article>{body}</article>"
        )
        page = PAGE.format(title=f"LLM Infrastructure 日报 · {d}", css=CSS, main=main_html)
        with open(os.path.join(OUT, "reports", f"{d}.html"), "w", encoding="utf-8") as f:
            f.write(page)

    latest = dates[0]
    body, sections = rendered[latest]
    index_main = (
        f'<section class="hero"><h1>LLM Infrastructure 日报</h1>'
        f"<p>训练与推理系统、serving 框架、硬件与集群的每日精选 · 最新一期：{latest}</p></section>"
        f'<div class="search">{SEARCH_SVG}<input type="search" placeholder="搜索本期内容：公司、论文、框架…" '
        f"oninput=\"applyFilter(this.value)\"></div>"
        f"{nav_html(sections)}"
        f"{archive_html(dates, latest)}"
        f"<article>{body}</article>"
        f"{FILTER_JS}"
    )
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGE.format(title="LLM Infrastructure 日报", css=CSS, main=index_main))
    print(f"built {len(dates)} report(s), latest {latest}")


if __name__ == "__main__":
    main()
