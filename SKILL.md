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
python scripts/theta_edgecloud.py dedicated-models
python scripts/theta_edgecloud.py dedicated-chat --message "Say hello"
```

Use `--json` where available for machine-readable output.

## On-demand service guidance

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
