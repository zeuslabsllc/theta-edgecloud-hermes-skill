#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

node_version="$(node --version 2>/dev/null || true)"
if [[ -z "$node_version" ]]; then
  echo "Node.js is required for Theta's official MCP server (needs Node >=18)."
  exit 1
fi

node - <<'JS'
const major = Number(process.versions.node.split('.')[0]);
if (major < 18) {
  console.error(`Node.js >=18 required; found ${process.versions.node}`);
  process.exit(1);
}
console.log(`Node.js OK: ${process.versions.node}`);
JS

npm view @thetalabs/on-demand-api-mcp name version description license engines --json > /tmp/theta_official_mcp_npm.json
python3 - <<'PY'
import json
from pathlib import Path
meta=json.loads(Path('/tmp/theta_official_mcp_npm.json').read_text())
required={
    'name': '@thetalabs/on-demand-api-mcp',
    'license': 'MIT',
}
for key, expected in required.items():
    if meta.get(key) != expected:
        raise SystemExit(f"Unexpected npm metadata {key}: {meta.get(key)!r}")
print(f"Official Theta MCP npm package OK: {meta['name']}@{meta['version']}")
print(meta.get('description', ''))
PY

# Avoid requiring a real token in this validator. A live Hermes MCP connection test
# should be run by users after adding their token to Hermes config.
echo "Next: add references/hermes-theta-official-mcp-config.yaml to your Hermes config file, set the Theta API key value, then restart Hermes or run /reload-mcp."
