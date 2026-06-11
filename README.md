# Theta EdgeCloud Hermes Skill

Public Hermes skill draft adapted from the Zeus Labs OpenClaw Theta EdgeCloud skill.

## Install locally

For local development, copy the skill directory into your Hermes skills folder:

```bash
mkdir -p ~/.hermes/skills/theta-edgecloud
cp -R /path/to/theta-edgecloud-hermes-skill/. ~/.hermes/skills/theta-edgecloud/
```

For public use with the helper script, install from the GitHub release archive or clone this repository. Installing a raw `SKILL.md` URL is useful for previewing skill metadata, but it only installs that single file and not bundled support files under `scripts/`.

## Validate helper script

```bash
python scripts/theta_edgecloud.py setup
python scripts/theta_edgecloud.py capabilities
python scripts/theta_edgecloud.py ondemand-list-services
python scripts/theta_edgecloud.py ondemand-chat --service gpt_oss_120b --message "Say hello"
python scripts/theta_edgecloud.py ondemand-infer --service stable_diffusion_xl_turbo --prediction predict --payload-json '{"input":{"prompt":"blue edge-cloud icon","steps":2,"strength":0.7,"guidance":0}}' --poll
python scripts/theta_edgecloud.py controller-vm-types
python scripts/theta_edgecloud.py controller-balance
python scripts/theta_edgecloud.py controller-standard-templates --category serving
python scripts/theta_edgecloud.py controller-validate-disposable --dry-run --probe openai --payload-json '{"project_id":"prj_demo","deployment_template_id":"img_demo"}'
```

## v0.2 direction: official Theta MCP + Hermes extensions

Theta Labs publishes an official MCP server for Theta EdgeCloud On-Demand Model APIs: `@thetalabs/on-demand-api-mcp`.

This repo's v0.2 direction is to use that official MCP server for on-demand inference, then keep this Hermes skill/helper focused on Hermes setup, safety, controller APIs, dedicated endpoint workflows, and deployment lifecycle tooling.

Validate local prerequisites for the official MCP server:

```bash
scripts/validate_official_mcp.sh
scripts/test_official_mcp_hermes.sh
```

Example Hermes MCP config is provided at:

```text
references/hermes-theta-official-mcp-config.yaml
```

Full setup notes are in `references/official-theta-mcp-hermes-setup.md`.

After adding config and token, restart Hermes or run `/reload-mcp`. The official tools should appear with names similar to:

- `mcp_theta_ondemand_list_services`
- `mcp_theta_ondemand_infer`
- `mcp_theta_ondemand_get_request_status`
- `mcp_theta_ondemand_get_upload_url`

## Live validation notes

2026-06-09 live tests confirmed on-demand service discovery, `gpt_oss_120b` chat, and `stable_diffusion_xl_turbo` image generation. Latest on-demand retest confirmed `gpt_oss_120b` chat in about `1.128s`, with OpenAI-compatible usage metrics: `75` prompt tokens, `76` completion tokens, `151` total tokens, and a message `reasoning` field. Qwen3 returned a temporary capacity error (`409 No instances available`). Controller catalog APIs work with a browser-like user-agent; project deployment listing requires a valid project API key with permission.

Organization balance lookup was also live-validated with `THETA_ORG_ID`; the response returns `body.balances[]` with `org_id` and numeric `balance`.

Dedicated inference note: a project API key can create a disposable serving deployment if quota/plan permissions allow it. That flow can generate temporary Basic Auth credentials in the deployment payload, discover the endpoint/auth from the create/list response, test `/v1/models` and `/v1/chat/completions`, then delete the deployment. `THETA_INFERENCE_AUTH_TOKEN` is not required for that Basic Auth path.

2026-06-10 disposable dedicated deployment validation succeeded with the `Grounding Dino` standard serving template on `vm_gt1`: create returned endpoint/auth/deletion handles, authenticated `/config` reached Gradio readiness, `POST /api/predict` returned a real base64 image result, and delete returned success with zero remaining deployments. `/v1/models` returned `404` for this Gradio template, so OpenAI-compatible checks should be reserved for vLLM/OpenAI-compatible templates.

Follow-up OpenAI-compatible test: `gpt-oss-20b` on recommended `vm_gh200x1` created successfully but did not reach `/v1/models` readiness within 10 minutes (`404` -> repeated `502` -> repeated `404`). Cleanup succeeded with zero remaining deployments. This suggests dedicated OpenAI-compatible endpoints may need longer warm-up, different template/VM choices, or persistent always-on operation before they are practical as a Hermes model provider.

Successful OpenAI-compatible test: `DeepSeek R1 / Distill-Qwen-7B` on recommended `vm_gh200x1` reached `/v1/models` after about 655.6 seconds and returned `200` from `/v1/chat/completions` with a valid response. The short smoke request took about 1.024 seconds once ready and reported 78 total tokens. Cleanup succeeded with zero remaining deployments. Cold-start cost was significant, so this is viable as a persistent/pre-warmed Hermes-compatible endpoint, not ideal for spin-up-per-chat usage.

## Publish options

For Hermes users, the preferred publishing path is a public GitHub repo published through the Hermes skills workflow. ClawHub can also be used for cross-agent/OpenClaw distribution.

```bash
hermes skills publish --to github --repo OWNER/REPO /home/hermes/theta-edgecloud-hermes-skill
```

Current Hermes CLI support for ClawHub publishing prints a manual-submit notice, so submit the release package manually at `https://clawhub.ai/submit` if ClawHub accepts this Hermes-targeted port.

Users can install the full release from GitHub with:

```bash
curl -L https://github.com/zeuslabsllc/theta-edgecloud-hermes-skill/archive/refs/tags/v0.1.0.tar.gz -o theta-edgecloud-hermes-skill-v0.1.0.tar.gz
mkdir -p ~/.hermes/skills/theta-edgecloud
tar -xzf theta-edgecloud-hermes-skill-v0.1.0.tar.gz --strip-components=1 -C ~/.hermes/skills/theta-edgecloud
```

To preview only the `SKILL.md` metadata through Hermes:

```bash
hermes skills inspect https://raw.githubusercontent.com/zeuslabsllc/theta-edgecloud-hermes-skill/main/SKILL.md
```

## Release smoke test

```bash
scripts/smoke_test.sh
```

## Notes

This first Hermes version is a skill + helper script. v0.2 should integrate Theta's official MCP server for on-demand inference and extend it with Hermes-specific controller/dedicated endpoint workflows.

