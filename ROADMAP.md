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
- [x] Revise v0.2 direction around Theta's official `@thetalabs/on-demand-api-mcp` server.

## Next: v0.1 release checklist

- [x] Review branding/credit wording.
- [x] Confirm license.
- [x] Confirm whether to publish on GitHub, ClawHub, or both.
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

- [x] Document Theta's official on-demand MCP server as the preferred on-demand integration path.
- [x] Add Hermes MCP config example for `@thetalabs/on-demand-api-mcp`.
- [x] Add official MCP prerequisite validator script.
- [ ] Test official Theta MCP server discovery inside Hermes with a real token.
- [ ] Document `hermes mcp add/test/list` flow after live validation.
- [x] Port deployment list/create/delete helpers.
- [x] Port balance lookup helper.
- [x] Port standard/custom templates listing.
- [x] Port on-demand infer/status/poll helpers.
- [ ] Port deployment stop/start helpers.
- [ ] Port on-demand upload-url helper.
- [ ] Port Theta Video API helpers.
- [ ] Add dedicated endpoint readiness retry helper with configurable window.
- [ ] Add safe disposable dedicated deployment validation command: create with generated Basic Auth, poll readiness, run template-appropriate probe, cleanup, and estimate balance delta.
- [ ] Add structured examples for `qwen3`, `gpt_oss_120b`, `flux`, `step_video`, `whisper`, `llava`.

## v0.3 native integration backlog

- [x] Draft native Hermes plugin/MCP plan in `V0.2_NATIVE_PLUGIN_MCP_PLAN.md`.
- [x] Decide between Hermes plugin/toolset and MCP server: use Theta's official MCP server for on-demand APIs first, then build Hermes/controller/dedicated endpoint extensions.
- [ ] Create native schemas for core Theta operations.
- [ ] Add check functions so tools only appear when credentials are configured.
- [ ] Add tests for secret redaction and dry-run behavior.
- [ ] Submit/distribute as public Hermes plugin if appropriate.

## Ongoing maintenance

- [ ] Monthly security review.
- [ ] Monthly check for Theta docs/API/model catalog changes.
- [ ] Update model aliases as live catalog changes.
- [ ] Update troubleshooting guidance for quota/capacity/auth changes.

