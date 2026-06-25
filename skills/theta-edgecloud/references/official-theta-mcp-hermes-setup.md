# Official Theta MCP setup for Hermes

Theta Labs publishes the official on-demand MCP server at:

- npm: `@thetalabs/on-demand-api-mcp`
- GitHub: `https://github.com/thetatoken/on-demand-api-mcp`

This server should be the default v0.2 path for Theta on-demand model access in Hermes. This repository adds Hermes-specific setup docs, validation, safety guidance, and controller/dedicated endpoint workflows around it.

## Prerequisites

- Node.js 18+
- `npx`
- Theta On-Demand access token

Token note: the same Theta On-Demand token used by this repo's helper as `THETA_ONDEMAND_API_TOKEN` / `THETA_ONDEMAND_API_KEY` can be passed to Theta's official MCP server as `THETA_API_KEY`.

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

into your Hermes config file, then replace the placeholder token:

```yaml
mcp_servers:
  theta_ondemand:
    command: "npx"
    args: ["@thetalabs/on-demand-api-mcp"]
    env:
      THETA_API_KEY: "${THETA_ONDEMAND_API_TOKEN}"
    timeout: 180
    connect_timeout: 60
    sampling:
      enabled: false
```

Security note: Hermes passes only a filtered baseline environment to stdio MCP subprocesses plus values explicitly listed under `env`. Do not commit real tokens.

If you already store the token as `THETA_ONDEMAND_API_TOKEN`, copy that same value into the MCP server's `THETA_API_KEY` env entry.

## Live validation notes

Validated with a real Theta On-Demand token:

- Hermes could launch the official MCP server.
- `tools/list` discovered 4 tools.
- `list_services` succeeded and included `gpt_oss_120b` and `qwen3`.

Observed inference behavior during validation:

- `gpt_oss_120b` through the official MCP `infer` tool returns a parse error if `stream` is omitted or placed at the top level: `Unexpected token 'd', "data: {"id"... is not valid JSON`. This happens because the service returns SSE-style `data:` chunks and the MCP server expects JSON.
- Workaround confirmed: include `stream: false` inside the `input` object. Example:

  ```json
  {
    "service": "gpt_oss_120b",
    "input": {
      "messages": [{"role": "user", "content": "Reply exactly: Theta MCP OK"}],
      "max_tokens": 64,
      "temperature": 0.3,
      "stream": false
    },
    "wait": 60
  }
  ```

  This returned a successful MCP result with `{"message": "MCP stream false OK"}` during validation.
- `qwen3` through the official MCP `infer` tool returned Theta capacity error `409 No instances available - try again later`, matching earlier helper-script observations.
- Direct API testing also confirmed two viable lower-level paths: parse the SSE `data:` stream manually, or use `/infer_request/chat/completions` with `stream: false`. For the official MCP server, the clean user-level fix is `input.stream: false`.

For now, recommend `input.stream: false` for `gpt_oss_120b` through official MCP. Keep this repo's direct helper path as a fallback when richer OpenAI-compatible fields or raw usage metrics are needed.

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

Manual `config.yaml` editing is the most reliable setup path for this package. The Theta dashboard example uses `args: ["@thetalabs/on-demand-api-mcp"]`; this avoids CLI parsing issues with args beginning with `-`, such as `npx -y`. The config file form above has been discovery-tested.

## What this repo still handles

The official MCP server covers on-demand inference. This repository remains useful for:

- Hermes setup and troubleshooting.
- Credential and dry-run safety guidance.
- Theta controller/project APIs.
- VM/template catalog helpers.
- Org balance lookup.
- Dedicated OpenAI-compatible endpoints.
- Disposable deployment validation and cleanup workflows.
