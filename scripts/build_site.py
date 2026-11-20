#!/usr/bin/env python3
"""Build a static site from reports/YYYY-MM-DD.md into _site/.

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
body{font-family:-apple-system,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;max-width:860px;margin:0 auto;padding:24px 16px 64px;color:#1a1a1a;line-height:1.7}
a{color:#0969da;text-decoration:none} a:hover{text-decoration:underline}
h1{font-size:28px} h2{margin-top:36px;border-bottom:1px solid #ddd;padding-bottom:6px}
table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto}
th,td{border:1px solid #ddd;padding:6px 8px;vertical-align:top;text-align:left}
input#q{width:100%;padding:10px;font-size:16px;border:1px solid #ccc;border-radius:8px;margin:16px 0}
.meta{color:#666;font-size:14px}
@media (prefers-color-scheme: dark){body{background:#0d1117;color:#e6edf3} th,td{border-color:#333} h2{border-color:#333}}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body>{body}</body></html>
"""


def render_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def main():
    os.makedirs(os.path.join(OUT, "reports"), exist_ok=True)
    dates = sorted(
        (fn[:-3] for fn in os.listdir(REPORTS) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", fn)),
        reverse=True,
    )
    if not dates:
        sys.exit("no reports found")
    for d in dates:
        body = render_md(os.path.join(REPORTS, f"{d}.md"))
        page = TEMPLATE.format(title=f"LLM Infrastructure 日报 · {d}", css=CSS, body=body)
        with open(os.path.join(OUT, "reports", f"{d}.html"), "w", encoding="utf-8") as f:
            f.write(page)
    latest = dates[0]
    items = "\n".join(
        f'<li><a href="reports/{d}.html">{d}</a></li>' for d in dates
    )
    latest_body = render_md(os.path.join(REPORTS, f"{latest}.md"))
    index_body = (
        f"<h1>LLM Infrastructure 日报</h1>"
        f'<p class="meta">每天早上 9:00（Asia/Shanghai）更新 · 最新一期：{latest}</p>'
        f'<input id="q" type="search" placeholder="搜索本期内容…" oninput="filter(this.value)">'
        f"<h2>往期归档</h2><ul>{items}</ul><hr>"
        f'<div id="latest">{latest_body}</div>'
        f"<script>function filter(q){{document.querySelectorAll('#latest table tr, #latest li, #latest p').forEach(el=>{{el.style.display=!q||el.textContent.toLowerCase().includes(q.toLowerCase())?'':'none'}})}}</script>"
    )
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(title="LLM Infrastructure 日报", css=CSS, body=index_body))
    print(f"built {len(dates)} report(s), latest {latest}")


if __name__ == "__main__":
    main()
