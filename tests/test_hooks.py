"""
Tests for ATLAS Lifecycle Hooks
Validates stdin/stdout contract and speed.
"""
import json
import subprocess
import time
from pathlib import Path

def test_pre_tool_allows_normal_command():
    hook_path = Path("/home/darwinsin/atlas/atlas/hooks/pre_tool.py")
    payload = {
        "conversationId": "test_hook_session",
        "toolCall": {
            "name": "run_command",
            "args": {"CommandLine": "git status"}
        }
    }
    
    t0 = time.perf_counter()
    res = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
    )
    duration_ms = (time.perf_counter() - t0) * 1000
    
    assert res.returncode == 0
    output = json.loads(res.stdout)
    assert output.get("decision") == "allow"
    # Python cold process invocation under Linux is reliably < 1000ms
    assert duration_ms < 1000

def test_pre_tool_blocks_dangerous_command():
    hook_path = Path("/home/darwinsin/atlas/atlas/hooks/pre_tool.py")
    payload = {
        "conversationId": "test_danger_session",
        "toolCall": {
            "name": "run_command",
            "args": {"CommandLine": "rm -rf /"}
        }
    }
    
    res = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
    )
    assert res.returncode == 0
    output = json.loads(res.stdout)
    assert output.get("decision") == "force_ask"
    assert "ATLAS WATCHDOG ACTIVATED" in output.get("reason", "")
