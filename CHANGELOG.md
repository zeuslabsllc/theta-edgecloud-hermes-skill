# Changelog — Theta EdgeCloud Hermes Skill

## Unreleased

- No unreleased changes yet.

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

