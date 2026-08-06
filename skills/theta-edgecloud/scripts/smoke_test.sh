#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

cd "$(dirname "$0")/.."

python3 -m py_compile scripts/theta_edgecloud.py
python3 scripts/theta_edgecloud.py setup >/tmp/theta_edgecloud_setup.out
python3 scripts/theta_edgecloud.py capabilities >/tmp/theta_edgecloud_capabilities.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-chat \
  --service qwen3 \
  --message 'Hermes Theta EdgeCloud smoke test' \
  --json >/tmp/theta_edgecloud_ondemand_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-chat \
  --service glm_5_2 \
  --message 'Hermes Theta EdgeCloud GLM-5.2 smoke test' \
  --max-tokens 128 \
  --temperature 0.3 \
  --top-p 0.7 \
  --enable-thinking \
  --json >/tmp/theta_edgecloud_glm_5_2_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py dedicated-chat \
  --model default \
  --message 'Hermes Theta EdgeCloud dedicated smoke test' \
  --json >/tmp/theta_edgecloud_dedicated_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-infer \
  --service stable_diffusion_xl_turbo \
  --prediction predict \
  --payload-json '{"input":{"prompt":"Hermes Theta EdgeCloud smoke test","steps":2}}' \
  --poll >/tmp/theta_edgecloud_ondemand_infer_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ondemand-upload-url \
  --service whisper \
  --input-field audio_filename \
  >/tmp/theta_edgecloud_upload_url_dry_run.json

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

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py controller-validate-disposable \
  --probe openai \
  --org-id org_demo \
  --payload-json '{"project_id":"prj_demo","deployment_template_id":"img_demo","auth_password":"validatorsecret"}' \
  >/tmp/theta_disposable_validate_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py controller-lifecycle-deployment \
  --action stop \
  --deployment-id base_demo \
  --project-id prj_demo \
  >/tmp/theta_lifecycle_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py video-upload-url \
  >/tmp/theta_video_upload_url_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py video-create \
  --source-uri 'https://example.com/video.mp4' \
  --payload-json '{"metadata":{"secret_note":"should_redact","public_note":"ok"}}' \
  >/tmp/theta_video_create_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py stream-create \
  --name demo \
  >/tmp/theta_stream_create_dry_run.json

THETA_DRY_RUN=1 python3 scripts/theta_edgecloud.py ingestor-select \
  --ingestor-id ingestor_demo \
  --stream-id stream_demo \
  >/tmp/theta_ingestor_select_dry_run.json

python3 - <<'PY'
import json
from pathlib import Path
for path in [
    '/tmp/theta_edgecloud_capabilities.json',
    '/tmp/theta_edgecloud_ondemand_dry_run.json',
    '/tmp/theta_edgecloud_glm_5_2_dry_run.json',
    '/tmp/theta_edgecloud_dedicated_dry_run.json',
    '/tmp/theta_edgecloud_ondemand_infer_dry_run.json',
    '/tmp/theta_edgecloud_upload_url_dry_run.json',
    '/tmp/theta_edgecloud_vm_types.json',
    '/tmp/theta_create_redacted.json',
    '/tmp/theta_disposable_validate_dry_run.json',
    '/tmp/theta_lifecycle_dry_run.json',
    '/tmp/theta_video_upload_url_dry_run.json',
    '/tmp/theta_video_create_dry_run.json',
    '/tmp/theta_stream_create_dry_run.json',
    '/tmp/theta_ingestor_select_dry_run.json',
]:
    json.loads(Path(path).read_text())
glm = json.loads(Path('/tmp/theta_edgecloud_glm_5_2_dry_run.json').read_text())
if glm.get('service') != 'glm_5_2':
    raise SystemExit('GLM-5.2 dry-run did not preserve canonical service alias')
glm_input = glm.get('payload', {}).get('input', {})
expected_glm = {
    'stream': False,
    'max_tokens': 128,
    'temperature': 0.3,
    'top_p': 0.7,
    'enable_thinking': True,
}
for key, value in expected_glm.items():
    if glm_input.get(key) != value:
        raise SystemExit(f'GLM-5.2 dry-run payload mismatch for {key}: {glm_input.get(key)!r}')
redacted = ''.join(Path(path).read_text() for path in [
    '/tmp/theta_create_redacted.json',
    '/tmp/theta_disposable_validate_dry_run.json',
    '/tmp/theta_video_create_dry_run.json',
])
for leaked in ['supersecret', 'regsecret', 'toksecret', 'validatorsecret', 'should_redact']:
    if leaked in redacted:
        raise SystemExit(f'secret leaked in dry-run output: {leaked}')

from scripts.theta_edgecloud import redact, redact_text_value
sample = {
    'upload_url': 'https://uploads.example/path?token=urlsecret&ok=1',
    'source_uri': 'https://cdn.example/video.mp4?X-Amz-Signature=sigsecret&public=ok',
    'stream_key': 'streamsecret',
    'message': 'plain text with https://user:pass@example.com/a?api_key=keysecret&safe=ok',
}
redacted_sample = json.dumps(redact(sample)) + redact_text_value('error token live_secret https://host/path?signature=sigsecret')
for leaked in ['urlsecret', 'sigsecret', 'streamsecret', 'keysecret']:
    if leaked in redacted_sample:
        raise SystemExit(f'secret-like URL material leaked in redaction helper: {leaked}')
if 'public=ok' not in redacted_sample and 'public\\": \\"ok' not in redacted_sample:
    raise SystemExit('expected non-sensitive URL/query material to remain visible')
print('Smoke test passed: syntax, setup, capabilities, dry-runs, video dry-runs, negative validation, redaction, controller VM catalog')
PY

rm -rf scripts/__pycache__
