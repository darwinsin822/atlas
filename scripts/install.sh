#!/usr/bin/env bash
set -e

echo "=== Instalando ATLAS Supervisor en Antigravity 2.0 ==="

# 1. Enlace simbólico de CLI global
mkdir -p /home/darwinsin/.local/bin
cat << 'LAUNCHER' > /home/darwinsin/.local/bin/atlas
#!/usr/bin/env bash
exec /home/darwinsin/atlas/.venv/bin/python3 /home/darwinsin/atlas/atlas/cli/main.py "$@"
LAUNCHER
chmod +x /home/darwinsin/.local/bin/atlas

# 2. Configuración de hooks en Antigravity
HOOKS_DIR="/home/darwinsin/.gemini/antigravity/hooks"
mkdir -p "$HOOKS_DIR"
cp /home/darwinsin/atlas/config/hooks.json "$HOOKS_DIR/hooks.json"
echo "✓ Hooks instalados en $HOOKS_DIR/hooks.json"

# 3. Registrar servidor MCP en Antigravity mcp_config.json
MCP_CONFIG="/home/darwinsin/.gemini/config/mcp_config.json"
if [ -f "$MCP_CONFIG" ]; then
    /home/darwinsin/atlas/.venv/bin/python3 - << 'PY'
import json
from pathlib import Path

path = Path("/home/darwinsin/.gemini/config/mcp_config.json")
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}

mcp_servers = data.setdefault("mcpServers", {})
mcp_servers["atlas"] = {
    "command": "/home/darwinsin/atlas/.venv/bin/python3",
    "args": ["/home/darwinsin/atlas/atlas/mcp/server.py"]
}

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("✓ Servidor MCP 'atlas' registrado en mcp_config.json")
PY
fi

echo "=== ATLAS instalado y activo con éxito ==="
