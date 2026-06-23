# Security Policy — Theta EdgeCloud Hermes Skill

## Credential handling

This project must never contain real Theta credentials.

Supported env vars may include:

- `THETA_EC_API_KEY`
- `THETA_EC_PROJECT_ID`
- `THETA_ORG_ID`
- `THETA_ONDEMAND_API_TOKEN`
- `THETA_ONDEMAND_API_KEY`
- `THETA_API_KEY`
- `THETA_INFERENCE_ENDPOINT`
- `THETA_INFERENCE_AUTH_TOKEN`
- `THETA_INFERENCE_AUTH_USER`
- `THETA_INFERENCE_AUTH_PASS`
- `THETA_VIDEO_SA_ID`
- `THETA_VIDEO_SA_SECRET`
- `THETA_DRY_RUN`

Rules:

1. Never commit real secret values.
2. Never print raw secret values.
3. Error messages should name missing env vars but not echo configured values.
4. Keep helper scripts dependency-light; currently stdlib-only.
5. Mutating/paid operations must support dry-run behavior or explicit confirmation.
6. Local file upload/read behavior must be explicit, documented, and opt-in only.
7. Avoid local shell execution inside runtime helpers.

## Security review checklist

Run before public release and monthly afterward:

```bash
cd /home/hermes/theta-edgecloud-hermes-skill
python scripts/theta_edgecloud.py setup
python scripts/theta_edgecloud.py capabilities
python -m py_compile scripts/theta_edgecloud.py
scripts/smoke_test.sh
git ls-files -z | xargs -0 python3 scripts/secret_scan.py
git log --all -p -- . ':(exclude)pr-materials/**' | python3 scripts/secret_scan.py
git grep -nE '(api[_-]?key|token|secret|password|bearer|authorization)' -- ':!*.png' ':!*.jpg' ':!*.mp4' ':!*.ogg' ':!*.mp3'
```

Manual review of grep output:
- placeholder env var names are OK
- docs mentioning secret concepts are OK
- real values are not OK

If dependencies are added later, add dependency vulnerability scanning to this file.

## Reporting

For now, report issues directly to the project maintainer before public release. Add public contact/security-report instructions once the public repo exists.
