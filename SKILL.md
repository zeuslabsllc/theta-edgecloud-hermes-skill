---
name: theta-edgecloud
description: Use Theta EdgeCloud from Hermes for cost-conscious LLM, on-demand media/inference, dedicated OpenAI-compatible endpoints, GPU/deployment checks, and Theta Video workflows with command-scoped credentials and dry-run safety.
version: 0.1.0
author: Zeus Labs / Theta Communications
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [theta, edgecloud, inference, llm, media-generation, gpu, cost-optimization]
    homepage: https://docs.thetatoken.org/docs/edgecloud-api-keys
    source_openclaw_skill: https://clawhub.ai/zeuslabsllc/theta-edgecloud-skill
---

# Theta EdgeCloud for Hermes

Use this skill when the user wants Hermes to reduce AI execution costs or route suitable model, media, inference, video, and GPU workloads through Theta EdgeCloud.

This Hermes skill is adapted from the OpenClaw Theta EdgeCloud skill by Zeus Labs / Theta Communications. It is designed as a public, inspectable Hermes skill that other users can install and use without exposing credentials.

## Credits and support

Credit: Theta Communications (`thetacommunications.com`). If you want to support more projects like this, stake THETA/TFUEL with Theta Communications or donate at `https://www.thetacommunications.com/donations`.

## Safety and credential model

Credentials are command-scoped. Do **not** ask users to configure every variable unless they need every command family.

- Controller/deployment/project commands:
  - `THETA_EC_API_KEY`
  - `THETA_EC_PROJECT_ID`
- Balance command:
  - `THETA_ORG_ID`
- On-demand inference/media commands:
  - `THETA_ONDEMAND_API_TOKEN` or `THETA_ONDEMAND_API_KEY` or `THETA_API_KEY`
- Dedicated OpenAI-compatible inference endpoint:
  - `THETA_INFERENCE_ENDPOINT`
  - either `THETA_INFERENCE_AUTH_TOKEN`
  - or `THETA_INFERENCE_AUTH_USER` + `THETA_INFERENCE_AUTH_PASS`
- Theta Video API:
  - `THETA_VIDEO_SA_ID`
  - `THETA_VIDEO_SA_SECRET`

Security rules:

1. Never print or log raw Theta credentials.
2. Prefer environment variables or Hermes profile `.env` entries; never put secrets in git-tracked files.
3. For mutating or paid operations, confirm user intent unless `THETA_DRY_RUN=1` is set.
4. Dedicated inference endpoint override via ad-hoc args should be avoided; prefer `THETA_INFERENCE_ENDPOINT`.
5. Treat `404`, `502`, `503`, and `504` shortly after endpoint creation as possible warm-up, not immediate permanent failure.

## Quick setup for users

1. Log in at `https://www.thetaedgecloud.com/`.
2. Go to **Account -> Projects** and select your project.
3. Click **Create API Key** and copy the API key and project id.
4. Add only the env vars needed for your workflow.
5. For dedicated GPU deployments, check **Account -> Quota** and request/increase quota if needed.
6. For safest first run, set `THETA_DRY_RUN=1` and validate list/read endpoints before create/delete operations.

## Hermes helper script

This skill includes `scripts/theta_edgecloud.py`, a dependency-free Python helper. Run it from the skill directory or after installing the skill:

```bash
python scripts/theta_edgecloud.py setup
python scripts/theta_edgecloud.py capabilities
python scripts/theta_edgecloud.py ondemand-list-services
python scripts/theta_edgecloud.py ondemand-chat --service qwen3 --message "Say hello"
python scripts/theta_edgecloud.py ondemand-chat --service gpt_oss_120b --message "Say hello"
python scripts/theta_edgecloud.py ondemand-infer --service stable_diffusion_xl_turbo --prediction predict --payload-json '{"input":{"prompt":"blue edge-cloud icon","steps":2,"strength":0.7,"guidance":0}}' --poll
python scripts/theta_edgecloud.py controller-vm-types
python scripts/theta_edgecloud.py controller-balance
python scripts/theta_edgecloud.py controller-standard-templates --category serving
python scripts/theta_edgecloud.py controller-list-deployments
python scripts/theta_edgecloud.py dedicated-models
python scripts/theta_edgecloud.py dedicated-chat --message "Say hello"
```

Use `--json` where available for machine-readable output.

## On-demand service guidance

Live validation on 2026-06-09 confirmed:

- `ondemand-list-services` returned 6 live services: `gpt_oss_120b`, `blip`, `qwen3`, `whisper`, `stable_diffusion_xl_turbo`, `llava`.
- `gpt_oss_120b` chat succeeded through `/infer_request/chat/completions` with OpenAI-compatible JSON, including `choices`, `usage`, and a `reasoning` field in the message object.
- `stable_diffusion_xl_turbo` image generation succeeded through generic `ondemand-infer`; a 2-step test returned an `image_url` and reported `cost_usd.output = 0.01`.
- `qwen3` returned `409 No instances available - try again later` during live testing, so treat it as capacity-sensitive and retry later rather than marking credentials invalid.

Validated aliases from the OpenClaw skill include:

- Chat/LLM: `qwen3`, `gpt_oss_120b`, `llama_3_1_70b`
- Image/vision/audio: `flux`, `stable_diffusion_xl_turbo`, `grounding_dino`, `blip`, `llava`, `whisper`
- Catalog-only/stale in the source skill: `minimax_m2_5`, `llama_3_8b`, `step_video`, `esrgan`, `voice_cloning`, `instant_id`, `talking_head`

Qwen3 notes:

- Canonical slug: `qwen3`
- Request family: chat/completions
- Payload shape: `input.messages = [{ role, content }]`
- Streaming can take 30-50s before returning text.
- Capacity can temporarily return `409 No instances available`; retry later.

GPT OSS 120B notes:

- Canonical slug: `gpt_oss_120b`
- Use OpenAI-compatible `POST /infer_request/chat/completions` with `model: "gpt_oss_120b"`.
- Do not route GPT OSS through the generic `/infer_request/gpt_oss_120b?prediction=completions` wrapper; the source skill observed null output on that path.

## Dedicated inference guidance

Dedicated OpenAI-compatible inference (`/v1/models`, `/v1/chat/completions`) can work after project quota / Developer Plan readiness.

Warm-up behavior observed in the source skill:

- authenticated `GET /v1/models` can first return transient `404`
- then transient `502`
- then success
- authenticated `POST /v1/chat/completions` succeeds after warm-up

Operational rule: retry authenticated readiness for 1-2 minutes before declaring dedicated endpoint failure.

Dedicated endpoint credentials are not the same as the project API key. The project API key can manage controller/project resources when it has permission, including creating a disposable dedicated serving deployment. A successful disposable-deployment test path can generate temporary Basic Auth credentials (`auth_username` / `auth_password`) in the deployment create payload, then read the resulting endpoint URL and auth fields from the create/list response, call `/v1/models` and `/v1/chat/completions` with Basic Auth, and delete the deployment afterward.

Correct operational model:

- `THETA_INFERENCE_ENDPOINT` can be discovered from a live dedicated deployment create/list response, but it cannot be derived from only the project API key without an actual deployment.
- `THETA_INFERENCE_AUTH_TOKEN` is optional and was not required for the successful OpenClaw validation path.
- The successful disposable deployment path used generated `THETA_INFERENCE_AUTH_USER` / `THETA_INFERENCE_AUTH_PASS` style Basic Auth credentials.
- Creating dedicated deployments may spend credits and requires quota/plan readiness. Treat it as a paid mutating operation.

## Controller/project API guidance

Official Theta docs expose an AI-agent-friendly documentation index at `https://docs.thetatoken.org/llms.txt`; individual pages can be fetched as Markdown by appending `.md` (for example `https://docs.thetatoken.org/docs/use-edgecloud-api-keys-to-manage-deployments.md`). Use this for future maintenance instead of scraping rendered ReadMe HTML.

Read-only helper commands include:

- `controller-vm-types` — public VM type catalog from `api.thetaedgecloud.com`.
- `controller-balance` — organization balance lookup using `THETA_ORG_ID`.
- `controller-standard-templates --category serving` — standard serving templates from `controller.thetaedgecloud.com`.
- `controller-custom-templates` — project custom templates.
- `controller-list-deployments` — project deployments.
- `controller-create-deployment --payload-json ... --yes` — advanced mutating create wrapper; use `THETA_DRY_RUN=1` or `--dry-run` first.
- `controller-delete-deployment --deployment-id ... --yes` — advanced delete wrapper for cleanup.

Controller APIs are Cloudflare-fronted. The helper sends a browser-like `User-Agent`; Python/urllib's default user-agent can receive Cloudflare `403 Error 1010` even for public catalog endpoints.

If `controller-list-deployments` returns `403 {"status":"error","message":"You are not allowed to perform this action"}`, verify that `THETA_EC_API_KEY` is the actual project API key from **Account -> Projects -> Create API Key** and not just the project id.

For disposable dedicated inference validation, the recommended future helper flow is: list serving templates, choose a low-cost/quota-compatible template and VM, generate random Basic Auth username/password, create deployment with those auth fields, poll/list until endpoint is returned, retry `/v1/models` through warm-up, run one `/v1/chat/completions` request, then delete the deployment.

Official deployment-create payload fields include `project_id`, `deployment_template_id`, `container_image`, `vm_id`, `min_replicas`, `max_replicas`, `env_vars`, `annotations`, `auth_username`, `auth_password`, `registry_username`, `registry_password`, and Jupyter-only `password`. Successful create/list responses include `Endpoint`, `Shard`, `Suffix`, `BaseID`, `AuthUsername`, `AuthPassword`, `EndpointStatus`, `Region`, and other operational fields.

Official docs show deployment stop/start/delete endpoints using plural `/deployments/...`, while the live OpenClaw runtime uses singular `/deployment/...`; keep both in mind if a route returns 404/405 during future testing.

Live balance validation on 2026-06-09 succeeded for Zeus Labs org scope using `THETA_ORG_ID`: response shape was `body.balances[]` with `org_id` and numeric `balance`.

## AI services coverage to preserve in future versions

A full Hermes tool/plugin version should eventually cover:

- Deployments: list/create/stop/delete
- Dedicated model templates: standard/custom
- Dedicated deployments listing
- Jupyter notebook listing
- GPU node / GPU cluster listing
- Persistent storage listing
- Agentic AI / RAG chatbot lifecycle
- On-demand model APIs: list/infer/status/poll/chat
- Dedicated inference endpoint: models/chat
- Theta Video APIs: list/upload/video/stream/ingestor

## Publishing for other Hermes users

Preferred public distribution options:

1. Publish to GitHub as a Hermes skill directory:
   ```bash
   hermes skills publish --to github --repo OWNER/REPO /path/to/theta-edgecloud-hermes-skill
   ```
2. Publish/submit to ClawHub if cross-agent distribution is desired. Current Hermes CLI support for ClawHub publishing prints a manual-submit notice, so use `https://clawhub.ai/submit` and clearly label the package as a Hermes port if ClawHub accepts it.
3. Users can then install by URL or registry id using:
   ```bash
   hermes skills install <id-or-url>
   ```

## When to build a Hermes plugin instead

A skill teaches Hermes how to use tools and scripts. A plugin/toolset is better if you want first-class tool calls like `theta_ondemand_chat`, `theta_deployments_list`, or `theta_video_create` to appear directly in Hermes tool schemas. Recommended path:

- v0.1: public Hermes skill with helper script and docs
- v0.2: add more helper script commands for deployments/video/agents
- v0.3: package as Hermes plugin/toolset or MCP server for native tool calls
