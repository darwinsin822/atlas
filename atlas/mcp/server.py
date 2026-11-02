"""
ATLAS MCP Server
Exposes ATLAS supervision, checkpointing, and forensic recovery tools to AI agents.
Compatible with standard Model Context Protocol (stdio) across MCP 1.x and 2.x.
"""
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from atlas.state import StateManager, Checkpoint
from atlas.watchdog import WatchdogEngine
from atlas.forensic import ForensicEngine
from atlas.config import DEFAULT_CONFIG

# Universal MCP import supporting both mcp 2.x (MCPServer) and mcp 1.x (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer
    app = MCPServer("atlas-supervisor")
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP
        app = FastMCP("atlas-supervisor")
    except Exception as e:
        print(f"Error importing MCP server: {e}", file=sys.stderr)
        sys.exit(1)


@app.tool()
def atlas_status(conversation_id: str = "default_session") -> str:
    """
    Returns current ATLAS supervisor status, loop metrics, and recent interventions.
    """
    mgr = StateManager()
    state = mgr.load_session(conversation_id)
    return json.dumps({
        "conversation_id": state.conversation_id,
        "status": state.current_status,
        "total_steps": state.total_steps,
        "recent_warnings": state.recent_loop_warnings[-5:],
        "commands_executed_count": len(state.commands_executed),
        "files_modified_count": len(state.files_modified),
        "checkpoints_count": len(state.checkpoints),
    }, indent=2)


@app.tool()
def atlas_checkpoint(conversation_id: str, description: str) -> str:
    """
    Records a safe checkpoint of the session before high-risk changes or refactors.
    """
    mgr = StateManager()
    state = mgr.load_session(conversation_id)
    cp = Checkpoint(
        id=f"cp_{int(datetime.now(timezone.utc).timestamp())}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        description=description,
        step_index=state.total_steps,
    )
    state.checkpoints.append(cp)
    mgr.save_session(state)
    return f"Checkpoint '{cp.id}' saved successfully: {description}"


@app.tool()
def atlas_loop_check(conversation_id: str, next_command: str) -> str:
    """
    Self-check for the agent before re-executing a command to prevent watchdog blocks.
    """
    mgr = StateManager()
    state = mgr.load_session(conversation_id)
    watchdog = WatchdogEngine(DEFAULT_CONFIG)
    decision, reason = watchdog.evaluate_command_execution(state, next_command)
    return json.dumps({
        "decision": decision,
        "reason": reason,
        "safe_to_execute": decision == "allow",
    }, indent=2)


@app.tool()
def atlas_report(conversation_id: str, transcript_path: Optional[str] = None) -> str:
    """
    Generates a comprehensive forensic report of the session with recovery options.
    """
    mgr = StateManager()
    state = mgr.load_session(conversation_id)
    t_path = Path(transcript_path) if transcript_path else None
    if not t_path:
        brain_dir = Path(f"/home/darwinsin/.gemini/antigravity/brain/{conversation_id}/.system_generated/logs/transcript.jsonl")
        if brain_dir.exists():
            t_path = brain_dir

    forensic = ForensicEngine(t_path)
    entries = forensic.parse_transcript() if t_path else []
    return forensic.format_rescue_report(conversation_id, state.current_status, entries)


@app.tool()
def atlas_resume(conversation_id: str, option: str, instruction: Optional[str] = None) -> str:
    """
    Executes a recovery option (A: Corregir rumbo, B: Retomar checkpoint, C: Redefinir).
    Resets loop warning counters to restore nominal status.
    """
    mgr = StateManager()
    state = mgr.load_session(conversation_id)
    opt = option.upper().strip()
    state.current_status = "nominal"
    state.recent_loop_warnings.clear()
    mgr.save_session(state)

    if opt == "A":
        return f"ATLAS: Rumbo corregido. Procediendo con instrucción: '{instruction or 'Continuar con nuevo enfoque'}'"
    elif opt == "B":
        last_cp = state.checkpoints[-1].description if state.checkpoints else "Inicio de sesión"
        return f"ATLAS: Reanudando desde último punto seguro: {last_cp}"
    elif opt == "C":
        return "ATLAS: Tarea pausada para redefinición y división en subtareas."
    else:
        return f"ATLAS: Opción '{opt}' no reconocida. Elija A, B o C."


def main():
    # Stdio transport for Antigravity MCP integration
    app.run()


if __name__ == "__main__":
    main()
