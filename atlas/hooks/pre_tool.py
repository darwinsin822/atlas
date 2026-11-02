#!/usr/bin/env python3
"""
ATLAS PreToolUse Hook
Executed synchronously before any tool invocation.
Receives event payload via stdin, applies Watchdog checks (<15ms latency),
and outputs decision JSON to stdout.
"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from atlas.config import DEFAULT_CONFIG
from atlas.state import StateManager
from atlas.watchdog import WatchdogEngine

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            # Nothing to inspect, allow
            print(json.dumps({"decision": "allow"}))
            return 0

        payload = json.loads(raw_input)
    except Exception:
        # Fail open with warning on malformed payload to prevent blocking IDE
        print(json.dumps({"decision": "allow"}))
        return 0

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", tool_call.get("toolName", ""))
    tool_args = tool_call.get("args", {})
    conversation_id = payload.get("conversationId", "default_session")

    state_mgr = StateManager()
    state = state_mgr.load_session(conversation_id)
    watchdog = WatchdogEngine(DEFAULT_CONFIG)

    # 1. Inspect run_command
    if tool_name == "run_command":
        cmd_line = tool_args.get("CommandLine", "")
        decision, reason = watchdog.evaluate_command_execution(state, cmd_line)

        if decision == "block":
            state.current_status = "loop_detected"
            state.recent_loop_warnings.append(reason)
            state_mgr.save_session(state)
            
            # Antigravity PreToolUse hook contract: force_ask triggers confirmation modal
            response = {
                "decision": "force_ask",
                "reason": f"🛑 [ATLAS WATCHDOG ACTIVATED]\n\n{reason}\n\nOpción A: Aprobar manualmente si es intencional.\nOpción B: Cancelar y solicitar rescate (/atlas-rescue)."
            }
            print(json.dumps(response))
            return 0
        
        elif decision == "warn":
            state.recent_loop_warnings.append(reason)
            state_mgr.save_session(state)
            # Output allow with audit logged
            print(json.dumps({"decision": "allow"}))
            return 0

    # 2. Inspect view_file / read operations
    elif tool_name in ("view_file", "read_resource"):
        target_path = tool_args.get("AbsolutePath", tool_args.get("Uri", ""))
        decision, reason = watchdog.evaluate_file_reading(state, target_path)
        if decision == "warn":
            state.recent_loop_warnings.append(reason)
            state_mgr.save_session(state)

    print(json.dumps({"decision": "allow"}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
