# Changelog — Theta EdgeCloud Hermes Skill

## Unreleased

- Added Theta EdgeCloud GLM-5.2 on-demand guidance using the canonical `glm_5_2` service alias.
- Added official MCP and direct-helper GLM-5.2 examples with optional thinking, token-limit, temperature, and top-p controls.
- Updated direct on-demand chat requests to send `stream: false` for reliable JSON responses.
- Preserved non-secret token limits and usage counters in redacted output while continuing to hide credential-bearing token fields.
- Live-checked Theta's public service catalog: GLM-5.2 is public under model id `glm-5.2`, uses the `completions` prediction, exposes thinking/sampling controls, and had a live default worker.
- Recorded Theta's 2026-08-05 launch article and the model's MIT license, 1M-token context, and long-horizon coding/agentic positioning.

## 0.2.1 - 2026-06-23

- Reviewed the downloaded 61-file official Theta Markdown docs corpus for skill improvements.
- Added initial Theta Video API helper commands: `video-upload-url`, `video-create`, `video-get`, `video-list`, `video-search`, `stream-create`, `stream-get`, `stream-list`, `ingestors-list`, and `ingestor-select`.
- Added dry-run/`--yes` safety gates for mutating Theta Video calls.
- Hardened recursive redaction for service-account secrets, signed/presigned upload URLs, credential-bearing URL query values, and stream keys.
- Enforced `https://` before sending dedicated endpoint credentials to readiness/smoke probes.
- Documented VOD upload/transcode/poll/list/search flow, livestream/ingestor flow, and webhook event caveats from the official docs.

## 0.2.0 - 2026-06-11

- Aligned v0.2 with Theta's official MCP server, `@thetalabs/on-demand-api-mcp`, for on-demand model access.
- Added Hermes MCP config, setup guide, and discovery validator for the official Theta MCP server.
- Live-validated official MCP discovery, `list_services`, and `gpt_oss_120b` inference with `input.stream=false`.
- Documented the correct public upstream repository: `https://github.com/thetatoken/on-demand-api-mcp`.
- Added structured examples for `gpt_oss_120b`, `qwen3`, Flux, Stable Diffusion XL Turbo, Whisper, LLaVA, Step Video, and dedicated endpoint workflows.
- Added `ondemand-upload-url` helper for presigned upload URLs.
- Added `controller-lifecycle-deployment --action start|stop` helper with dry-run/`--yes` safety.
- Completed `controller-validate-disposable` with generated Basic Auth, readiness probes, cleanup verification, and pre/post balance delta reporting.
- Added `dedicated-ready` helper for configurable OpenAI/Gradio readiness checks.
- Expanded smoke tests, dry-run redaction checks, release archive inspection, and security scan coverage.

## 0.1.0 - 2026-06-10

- Created ongoing project scaffold for public release.
- Added Hermes `SKILL.md` adapted from the Zeus Labs OpenClaw Theta EdgeCloud skill.
- Added stdlib-only helper script: `scripts/theta_edgecloud.py`.
- Added setup and capability diagnostics.
- Added on-demand list/chat and dedicated models/chat helper commands.
- Added generic on-demand infer/status helpers with polling support.
- Added controller catalog/deployment read helpers.
- Added advanced controller create/delete wrappers gated by dry-run/`--yes`.
- Added live-tested `controller-balance` helper for `THETA_ORG_ID` org balance lookup.
- Live-tested on-demand service discovery, `gpt_oss_120b` chat, and `stable_diffusion_xl_turbo` image generation.
- Live-tested disposable dedicated serving deployment create/readiness/predict/delete flow with `Grounding Dino` on `vm_gt1`.
- Tested `gpt-oss-20b` dedicated OpenAI-compatible deployment on recommended `vm_gh200x1`; create/delete worked but `/v1/models` did not become ready within 10 minutes.
- Live-tested `DeepSeek R1 / Distill-Qwen-7B` dedicated OpenAI-compatible deployment on `vm_gh200x1`; `/v1/models` and `/v1/chat/completions` both succeeded after ~656s warm-up.
- Retested `gpt_oss_120b` on-demand chat: success in ~1.128s with 151 total tokens and OpenAI-compatible usage metrics; `qwen3` still returned transient capacity `409`.
- Documented Qwen3 capacity behavior, controller Cloudflare user-agent requirement, and disposable dedicated deployment Basic Auth flow.
- Added roadmap and security policy.

