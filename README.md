# Idea Lab
Private idea lab by Incidental AI (noindex). 37 ideas, each with a full detail page at `/idea/<id>/`:
Business Model Canvas, pricing & unit economics, expected revenue (conservative/base/optimistic, all [assumption]),
risks + kill criteria, D1–D30 operating plan, automation pipeline, copyable prompt pack, evidence links.

Data: `scripts/ideas.py` + `scripts/green.py` (zh) + `scripts/params.py` (assumed business parameters)
→ `scripts/detail.py` (detail generator) → `python3 scripts/build.py` → `docs/data.js`, `docs/d/<id>.json`, `docs/idea/<id>/index.html`.
Non-Chinese text is machine-translated (Argos) and labeled. Top-3 deep playbooks come from biz-greenfield/top3-detailed.md (Chinese only).

## 更新机制（热点）

- 生产者：共享电脑上的 Grok Bot 定时任务「Idea Lab 热点每 15 分钟更新」。它筛选热点、写摘要（需要 LLM），再运行 `python3 scripts/hotspots_update.py new.json`，脚本合并数据、重建 `docs/hotspots/data.js`，然后 commit 并 push。GitHub Pages 自动部署。
- 守护：`.github/workflows/freshness.yml` 每小时检查线上 `lastUpdated`。超过 2 小时没更新时，这次运行会失败，并开一个带 `stale-data` 标签的 issue；数据恢复后 issue 自动关闭。它不生成内容。
- 注意：没有新热点时脚本不会 push，所以很安静的时段也可能触发告警。
