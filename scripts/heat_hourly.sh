#!/usr/bin/env bash
# Hourly heat run. Optional $1 = raw x.search_news output file (Bot routine writes it first). No git push here.
set -euo pipefail; cd "$(dirname "$0")/.."; mkdir -p out
X=${1:-}; LOG=out/heat-hourly.log
{ date -u +%FT%TZ; if [ -n "$X" ] && [ -s "$X" ]; then python3 scripts/heat_collect.py --x "$X"; else python3 scripts/heat_collect.py; fi
  python3 scripts/heat_build.py 2>&1 | grep -v WARNING; } | tee -a "$LOG"
