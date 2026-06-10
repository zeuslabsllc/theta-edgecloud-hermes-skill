# Changelog — Theta EdgeCloud Hermes Skill

## Unreleased

- Created ongoing project scaffold for public release.
- Added Hermes `SKILL.md` adapted from the Zeus Labs OpenClaw Theta EdgeCloud skill.
- Added stdlib-only helper script: `scripts/theta_edgecloud.py`.
- Added setup and capability diagnostics.
- Added on-demand list/chat and dedicated models/chat helper commands.
- Added generic on-demand infer/status helpers with polling support.
- Added controller catalog/deployment read helpers.
- Added advanced controller create/delete wrappers gated by dry-run/`--yes`.
- Live-tested on-demand service discovery, `gpt_oss_120b` chat, and `stable_diffusion_xl_turbo` image generation.
- Documented Qwen3 capacity behavior, controller Cloudflare user-agent requirement, and disposable dedicated deployment Basic Auth flow.
- Added roadmap and security policy.
