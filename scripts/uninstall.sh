#!/usr/bin/env bash
set -e

echo "=== Desinstalando ATLAS ==="
rm -f /home/darwinsin/.local/bin/atlas
rm -f /home/darwinsin/.gemini/antigravity/hooks/hooks.json

MCP_CONFIG="/home/darwinsin/.gemini/config/mcp_config.json"
if [ -f "$MCP_CONFIG" ]; then
    python3 - << 'PY'
import json
from pathlib import Path

path = Path("/home/darwinsin/.gemini/config/mcp_config.json")
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "atlas" in data.get("mcpServers", {}):
        del data["mcpServers"]["atlas"]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("✓ Servidor MCP 'atlas' removido de mcp_config.json")
except Exception:
    pass
PY
fi

echo "=== ATLAS desinstalado ==="
