#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m py_compile scripts/theta_edgecloud.py
python3 scripts/theta_edgecloud.py setup >/tmp/theta_edgecloud_setup.out
python3 scripts/theta_edgecloud.py capabilities >/tmp/theta_edgecloud_capabilities.json
THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-chat \
  --service qwen3 \
  --message 'Hermes Theta EdgeCloud smoke test' \
  --json >/tmp/theta_edgecloud_ondemand_dry_run.json
THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py dedicated-chat \
  --model default \
  --message 'Hermes Theta EdgeCloud dedicated smoke test' \
  --json >/tmp/theta_edgecloud_dedicated_dry_run.json

python3 - <<'PY'
import json
from pathlib import Path
for path in [
    '/tmp/theta_edgecloud_capabilities.json',
    '/tmp/theta_edgecloud_ondemand_dry_run.json',
    '/tmp/theta_edgecloud_dedicated_dry_run.json',
]:
    json.loads(Path(path).read_text())
print('Smoke test passed: syntax, setup, capabilities, on-demand dry-run, dedicated dry-run')
PY
