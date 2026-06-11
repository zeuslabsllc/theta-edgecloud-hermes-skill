# Official Theta MCP setup for Hermes

Theta Labs publishes the official on-demand MCP server at:

- npm: `@thetalabs/on-demand-api-mcp`
- GitHub: `https://github.com/thetalabs/on-demand-api-mcp`

This server should be the default v0.2 path for Theta on-demand model access in Hermes. This repository adds Hermes-specific setup docs, validation, safety guidance, and controller/dedicated endpoint workflows around it.

## Prerequisites

- Node.js 18+
- `npx`
- Theta On-Demand access token

Validate local package prerequisites:

```bash
scripts/validate_official_mcp.sh
```

Validate Hermes MCP discovery without a real token:

```bash
scripts/test_official_mcp_hermes.sh
```

Expected discovery output includes 4 tools:

- `list_services`
- `infer`
- `get_request_status`
- `get_upload_url`

## Hermes config

Copy the example config:

```text
references/hermes-theta-official-mcp-config.yaml
```

into `~/.hermes/config.yaml`, then replace the placeholder token:

```yaml
mcp_servers:
  theta_ondemand:
    command: "npx"
    args: ["-y", "@thetalabs/on-demand-api-mcp"]
    env:
      THETA_API_KEY: "REPLACE_WITH_THETA_ONDEMAND_ACCESS_TOKEN"
    timeout: 180
    connect_timeout: 60
    sampling:
      enabled: false
```

Security note: Hermes passes only a filtered baseline environment to stdio MCP subprocesses plus values explicitly listed under `env`. Do not commit real tokens.

## Reload / test

After editing config:

```bash
hermes mcp list
hermes mcp test theta_ondemand
```

In a running Hermes session, restart or run:

```text
/reload-mcp
```

Expected Hermes tool names use the server prefix:

- `mcp_theta_ondemand_list_services`
- `mcp_theta_ondemand_infer`
- `mcp_theta_ondemand_get_request_status`
- `mcp_theta_ondemand_get_upload_url`

## Current Hermes CLI note

Manual `config.yaml` editing is the most reliable setup path for this package because `hermes mcp add --args` can be awkward with args beginning with `-`, such as `npx -y`. The config file form above has been discovery-tested.

## What this repo still handles

The official MCP server covers on-demand inference. This repository remains useful for:

- Hermes setup and troubleshooting.
- Credential and dry-run safety guidance.
- Theta controller/project APIs.
- VM/template catalog helpers.
- Org balance lookup.
- Dedicated OpenAI-compatible endpoints.
- Disposable deployment validation and cleanup workflows.
