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
THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-infer \
  --service stable_diffusion_xl_turbo \
  --prediction predict \
  --payload-json '{"input":{"prompt":"Hermes Theta EdgeCloud smoke test","steps":2}}' \
  --poll >/tmp/theta_edgecloud_ondemand_infer_dry_run.json
python3 scripts/theta_edgecloud.py controller-vm-types >/tmp/theta_edgecloud_vm_types.json

python3 - <<'PY'
import json
from pathlib import Path
for path in [
    '/tmp/theta_edgecloud_capabilities.json',
    '/tmp/theta_edgecloud_ondemand_dry_run.json',
    '/tmp/theta_edgecloud_dedicated_dry_run.json',
    '/tmp/theta_edgecloud_ondemand_infer_dry_run.json',
    '/tmp/theta_edgecloud_vm_types.json',
]:
    json.loads(Path(path).read_text())
print('Smoke test passed: syntax, setup, capabilities, on-demand chat dry-run, dedicated dry-run, generic infer dry-run, controller VM catalog')
PY
