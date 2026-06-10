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
THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py controller-balance --org-id org_placeholder >/tmp/theta_edgecloud_balance_missing_key.txt 2>&1 || true

# Negative/safety checks: invalid dry-run payloads should fail and dry-run output should redact secrets.
if THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-infer --service x --payload-json '{bad' >/tmp/theta_bad_json.out 2>&1; then
  echo 'Expected invalid ondemand-infer JSON to fail'
  exit 1
fi

if python3 scripts/theta_edgecloud.py controller-delete-deployment --dry-run >/tmp/theta_delete_no_target.out 2>&1; then
  echo 'Expected delete dry-run without target to fail'
  exit 1
fi

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py controller-create-deployment \
  --payload-json '{"project_id":"prj_demo","deployment_template_id":"img_demo","auth_username":"user","auth_password":"supersecret","registry_password":"regsecret","env_vars":{"API_TOKEN":"toksecret","SAFE_VALUE":"ok"}}' \
  >/tmp/theta_create_redacted.json

python3 - <<'PY'
import json
from pathlib import Path
for path in [
    '/tmp/theta_edgecloud_capabilities.json',
    '/tmp/theta_edgecloud_ondemand_dry_run.json',
    '/tmp/theta_edgecloud_dedicated_dry_run.json',
    '/tmp/theta_edgecloud_ondemand_infer_dry_run.json',
    '/tmp/theta_edgecloud_vm_types.json',
    '/tmp/theta_create_redacted.json',
]:
    json.loads(Path(path).read_text())
redacted = Path('/tmp/theta_create_redacted.json').read_text()
for leaked in ['supersecret', 'regsecret', 'toksecret']:
    if leaked in redacted:
        raise SystemExit(f'secret leaked in dry-run output: {leaked}')
print('Smoke test passed: syntax, setup, capabilities, dry-runs, negative validation, redaction, controller VM catalog')
PY
