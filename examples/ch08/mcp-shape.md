---
on:
  workflow_dispatch:
permissions:
  contents: read
engine: copilot
network:
  allowed: [defaults, mcp.example.invalid]
mcp-servers:
  example:
    url: https://mcp.example.invalid/mcp
    allowed: [lookup_reference]
safe-outputs:
  add-comment:
    max: 1
---

# Illustrative MCP configuration shape

Do not run this fixture. The endpoint and tool name are deliberately placeholders,
not a Slack integration. Supply a verified provider, authentication and tool catalog
before adapting this configuration to a real service.
