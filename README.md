# llm-infra-daily

网站：https://four1er.github.io/llm-infra-daily/

LLM infrastructure 每日汇总网站：每天早上 9:00（Asia/Shanghai）汇总最近 24 小时内的最新内容，覆盖

1. 技术报告（实验室/公司工程博客、系统报告）
2. 最新研究与论文（arXiv 等）
3. 行业新闻动态
4. X（Twitter）上有实质内容或热点价值的研究动态与讨论
5. 热点新闻（出圈话题、争议、融资/公司动向、开源发布、硬件与算力大新闻）

主题聚焦训练与推理系统、分布式训练、并行策略、显存优化、KV cache、推理加速与 serving 框架（vLLM、SGLang、TensorRT-LLM）、compiler/算子、GPU/加速器硬件与集群、调度、量化压缩、长上下文与 MoE 工程、性能 benchmark。

## 网站如何更新

- 日报原文放在 `reports/YYYY-MM-DD.md`，新一期由 Muse 的每日定时任务生成并推送到本仓库
- `.github/workflows/pages.yml` 在每次推送到 `main` 时自动运行 `scripts/build_site.py`，把 Markdown 渲染成静态页面并部署到 GitHub Pages
- 每条内容都给出标题、来源、发布时间、一句话要点和原文链接；没有值得关注的新内容时会如实说明，不编造；X 类别无法取得可验证原帖链接时会明确标注缺口
