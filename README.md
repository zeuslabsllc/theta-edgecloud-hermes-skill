# Theta EdgeCloud Hermes Skill

Public Hermes skill draft adapted from the Zeus Labs OpenClaw Theta EdgeCloud skill.

## Install locally

For local development, copy the skill directory into your Hermes skills folder:

```bash
mkdir -p ~/.hermes/skills/theta-edgecloud
cp -R /home/hermes/theta-edgecloud-hermes-skill/* ~/.hermes/skills/theta-edgecloud/
```

For public use, publish first and have users install by registry id or direct `SKILL.md` URL.

## Validate helper script

```bash
python scripts/theta_edgecloud.py setup
python scripts/theta_edgecloud.py capabilities
python scripts/theta_edgecloud.py ondemand-list-services
python scripts/theta_edgecloud.py ondemand-chat --service gpt_oss_120b --message "Say hello"
python scripts/theta_edgecloud.py ondemand-infer --service stable_diffusion_xl_turbo --prediction predict --payload-json '{"input":{"prompt":"blue edge-cloud icon","steps":2,"strength":0.7,"guidance":0}}' --poll
python scripts/theta_edgecloud.py controller-vm-types
python scripts/theta_edgecloud.py controller-standard-templates --category serving
```

## Live validation notes

2026-06-09 live tests confirmed on-demand service discovery, `gpt_oss_120b` chat, and `stable_diffusion_xl_turbo` image generation. Qwen3 returned a temporary capacity error (`409 No instances available`). Controller catalog APIs work with a browser-like user-agent; project deployment listing requires a valid project API key with permission.

Dedicated inference note: a project API key can create a disposable serving deployment if quota/plan permissions allow it. That flow can generate temporary Basic Auth credentials in the deployment payload, discover the endpoint/auth from the create/list response, test `/v1/models` and `/v1/chat/completions`, then delete the deployment. `THETA_INFERENCE_AUTH_TOKEN` is not required for that Basic Auth path.

## Publish options

For Hermes users, the preferred publishing path is a public GitHub repo published through the Hermes skills workflow. ClawHub can also be used for cross-agent/OpenClaw distribution.

```bash
hermes skills publish --to github --repo OWNER/REPO /home/hermes/theta-edgecloud-hermes-skill
```

Current Hermes CLI support for ClawHub publishing prints a manual-submit notice, so submit the release package manually at `https://clawhub.ai/submit` if ClawHub accepts this Hermes-targeted port.

Users can install from the published source with:

```bash
hermes skills install <id-or-url>
```

## Release smoke test

```bash
scripts/smoke_test.sh
```

## Notes

This first Hermes version is a skill + helper script. A future Hermes plugin/MCP server would expose first-class Theta tool calls directly in Hermes.
