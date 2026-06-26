# Theta EdgeCloud Hermes Skill — Ongoing Project

## Project status

**Status:** Active / ongoing

**Goal:** Publicly release and maintain a Hermes skill that lets Hermes users use Theta EdgeCloud AI tools for cost-conscious inference, media generation, dedicated OpenAI-compatible endpoints, GPU/deployment workflows, and Theta Video operations.

**Working directory:** `/home/hermes/theta-edgecloud-hermes-skill`

**Source inspiration:** Zeus Labs' OpenClaw-era Theta EdgeCloud work, ported into a dedicated Hermes skill distribution.

## Product objective

Make Theta EdgeCloud accessible to Hermes users as a reusable, public skill first, then evolve it into a richer Hermes plugin/toolset or MCP server if demand warrants native tool-call UX.

## Release strategy

### v0.1 — Public skill release

Scope:
- Hermes `SKILL.md` adapted from the OpenClaw skill.
- Dependency-free Python helper script under `scripts/theta_edgecloud.py`.
- Setup and credential diagnostics.
- On-demand service list.
- On-demand chat helper for `qwen3` and `gpt_oss_120b` routes.
- Dedicated OpenAI-compatible `/v1/models` and `/v1/chat/completions` helpers.
- Clear credential-scoping and dry-run guidance.
- Public README.

Acceptance criteria:
- `python scripts/theta_edgecloud.py setup` works.
- `python scripts/theta_edgecloud.py capabilities` works and never prints secrets.
- Skill docs explain minimal env vars by command family.
- Archive/package contains only intended files.
- Ready to publish as a Hermes GitHub/skills.sh skill.

### v0.2 — Coverage expansion

Add helper commands for:
- deployment list/create/stop/delete
- balance lookup
- standard/custom deployment template listing
- on-demand infer/status/poll/upload-url
- Theta Video list/upload/video/stream/ingestor operations
- Agentic AI / RAG chatbot operations if public API support remains stable

### v0.3 — Native Hermes integration

Evaluate and build one of:
- Hermes plugin/toolset exposing native `theta_*` tool calls
- MCP server compatible with Hermes native MCP support
- Both, if useful

## Maintenance policy

### Theta feature updates

When the Theta team ships new EdgeCloud APIs, model aliases, auth behavior, quota behavior, or docs:
1. Review official Theta docs and dashboard/API changes.
2. Compare with the current OpenClaw source skill if it has been updated.
3. Update `SKILL.md` feature guidance.
4. Add or update helper script commands.
5. Run local smoke tests without credentials.
6. If credentials are available, run live read-only tests first, then dry-run/mutating tests only after confirmation.
7. Update `CHANGELOG.md`.

### Security updates

Periodic security checks must verify:
- No hardcoded credentials or tokens.
- No secret values printed in normal or error output.
- No local shell execution introduced by helper commands unless intentionally reviewed.
- No local file reads/uploads without explicit user intent.
- Mutating or paid operations support `THETA_DRY_RUN=1` and/or confirmation flow.
- Dependencies remain minimal; currently helper script is stdlib-only.
- If dependencies are later added, run vulnerability checks before release.

### Public release channels

Candidate publish commands:

```bash
hermes skills publish --to github --repo OWNER/REPO /home/hermes/theta-edgecloud-hermes-skill
```

Users should eventually be able to install with:

```bash
hermes skills install <id-or-url>
```

## Important URLs

- Hermes skill tap: `zeuslabsllc/theta-edgecloud-hermes-skill/skills/theta-edgecloud`
- Theta EdgeCloud: `https://www.thetaedgecloud.com/`
- Theta API key docs: `https://docs.thetatoken.org/docs/edgecloud-api-keys`
- Theta Communications: `https://www.thetacommunications.com/`

## Ownership notes

- Public-facing project name: **Theta EdgeCloud Hermes Skill**
- Credit: Zeus Labs / Theta Communications
- Avoid publishing user/private credentials or local machine-specific configuration.
