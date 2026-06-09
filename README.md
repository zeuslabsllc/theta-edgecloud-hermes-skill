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
```

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
