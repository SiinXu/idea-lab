# Idea Lab
Private idea lab for XU SIYIN (noindex). 37 ideas, each with a full detail page at `/idea/<id>/`:
Business Model Canvas, pricing & unit economics, expected revenue (conservative/base/optimistic, all [assumption]),
risks + kill criteria, D1–D30 operating plan, automation pipeline, copyable prompt pack, evidence links.

Data: `scripts/ideas.py` + `scripts/green.py` (zh) + `scripts/params.py` (assumed business parameters)
→ `scripts/detail.py` (detail generator) → `python3 scripts/build.py` → `docs/data.js`, `docs/d/<id>.json`, `docs/idea/<id>/index.html`.
Non-Chinese text is machine-translated (Argos) and labeled. Top-3 deep playbooks come from biz-greenfield/top3-detailed.md (Chinese only).
