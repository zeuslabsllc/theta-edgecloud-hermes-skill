# Roadmap — Theta EdgeCloud Hermes Skill

## Now

- [x] Inspect OpenClaw skill package.
- [x] Draft Hermes `SKILL.md`.
- [x] Add dependency-free helper script.
- [x] Add setup and capabilities commands.
- [x] Package local zip artifact.
- [ ] Decide public repo/registry destination.
- [ ] Publish v0.1.
- [ ] Test install from published source in a clean Hermes profile.

## Next: v0.1 release checklist

- [ ] Review branding/credit wording.
- [ ] Confirm license.
- [ ] Confirm whether to publish on GitHub, ClawHub, or both.
- [x] Add example `.env.example` with placeholder names only.
- [x] Add smoke-test script.
- [x] Run secret scan.
- [x] Run `python scripts/theta_edgecloud.py setup`.
- [x] Run `python scripts/theta_edgecloud.py capabilities`.
- [x] Create release zip and hash.
- [ ] Publish.
- [ ] Install from public source and verify `skill_view` loads.
- [x] Run live on-demand service discovery.
- [x] Run live `gpt_oss_120b` chat.
- [x] Run live `stable_diffusion_xl_turbo` image generation.
- [x] Capture Qwen3 capacity behavior.
- [x] Add controller catalog helper commands.
- [x] Clarify disposable dedicated deployment endpoint/auth flow from OpenClaw validation.
- [x] Run live org balance lookup with `THETA_ORG_ID`.
- [x] Review official Theta EdgeCloud Markdown docs and capture API payload/route notes.
- [x] Run live disposable dedicated deployment validation with Basic Auth, readiness polling, Gradio prediction, and cleanup.

## v0.2 feature backlog

- [ ] Port deployment list/create/stop/delete helpers.
- [ ] Port balance lookup helper.
- [ ] Port standard/custom templates listing.
- [ ] Port on-demand infer/status/poll/upload-url helpers.
- [ ] Port Theta Video API helpers.
- [ ] Add dedicated endpoint readiness retry helper with configurable window.
- [ ] Add safe disposable dedicated deployment validation command: create with generated Basic Auth, poll readiness, run template-appropriate probe, cleanup, and estimate balance delta.
- [ ] Add structured examples for `qwen3`, `gpt_oss_120b`, `flux`, `step_video`, `whisper`, `llava`.

## v0.3 native integration backlog

- [ ] Decide between Hermes plugin/toolset and MCP server.
- [ ] Create native schemas for core Theta operations.
- [ ] Add check functions so tools only appear when credentials are configured.
- [ ] Add tests for secret redaction and dry-run behavior.
- [ ] Submit/distribute as public Hermes plugin if appropriate.

## Ongoing maintenance

- [ ] Monthly security review.
- [ ] Monthly check for Theta docs/API/model catalog changes.
- [ ] Update model aliases as live catalog changes.
- [ ] Update troubleshooting guidance for quota/capacity/auth changes.

