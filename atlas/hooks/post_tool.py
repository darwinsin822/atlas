#!/usr/bin/env python3
"""
ATLAS PostToolUse Hook
Executed after tool invocation completes.
Updates telemetry, counts executions, and persists state.
"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from atlas.state import StateManager

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return 0
        payload = json.loads(raw_input)
    except Exception:
        return 0

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", tool_call.get("toolName", ""))
    tool_args = tool_call.get("args", {})
    conversation_id = payload.get("conversationId", "default_session")

    state_mgr = StateManager()
    state = state_mgr.load_session(conversation_id)
    state.total_steps += 1

    if tool_name == "run_command":
        cmd_line = tool_args.get("CommandLine", "")
        exit_code = payload.get("toolResult", {}).get("exitCode", 0)
        state.commands_executed.append({
            "command": cmd_line,
            "exit_code": exit_code,
        })
        # Keep list bounded
        if len(state.commands_executed) > 50:
            state.commands_executed = state.commands_executed[-50:]

    elif tool_name in ("view_file", "read_resource"):
        target_path = tool_args.get("AbsolutePath", tool_args.get("Uri", ""))
        if target_path:
            state.files_viewed[target_path] = state.files_viewed.get(target_path, 0) + 1

    elif tool_name in ("replace_file_content", "write_to_file"):
        target_path = tool_args.get("TargetFile", "")
        if target_path:
            state.files_modified[target_path] = state.files_modified.get(target_path, 0) + 1

    state_mgr.save_session(state)
    return 0

if __name__ == "__main__":
    sys.exit(main())
