#!/usr/bin/env bash
set -euo pipefail

# Verifies Hermes can launch Theta's official on-demand MCP server and discover tools.
# Uses a temporary HERMES_HOME and deletes it afterward.
#
# This discovery test intentionally uses a placeholder token. Tool discovery works
# without a valid token; real inference calls require a real Theta token in the
# user's normal Hermes config.

cd "$(dirname "$0")/.."

tmp_home="$(mktemp -d /tmp/hermes-theta-mcp.XXXXXX)"
cleanup() {
  rm -rf "$tmp_home"
}
trap cleanup EXIT

cat > "$tmp_home/config.yaml" <<'YAML'
mcp_servers:
  theta_ondemand:
    command: "npx"
    args: ["@thetalabs/on-demand-api-mcp"]
    env:
      THETA_API_KEY: "PLACEHOLDER_TOKEN_FOR_DISCOVERY_ONLY"
    timeout: 180
    connect_timeout: 60
    sampling:
      enabled: false
YAML

HERMES_HOME="$tmp_home" hermes mcp list
HERMES_HOME="$tmp_home" hermes mcp test theta_ondemand

echo "Hermes official Theta MCP discovery test passed. Real infer/list calls require a valid Theta token configured in Hermes."
