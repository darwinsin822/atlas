"""
Tests for ATLAS Watchdog Engine
Verifies loop prevention, identical command thresholds, and dangerous pattern matching.
"""
from atlas.config import AtlasConfig, WatchdogThresholds
from atlas.state import SessionState
from atlas.watchdog import WatchdogEngine

def test_identical_consecutive_commands_blocked():
    cfg = AtlasConfig(thresholds=WatchdogThresholds(max_consecutive_identical_commands=2))
    watchdog = WatchdogEngine(cfg)
    state = SessionState(conversation_id="test_conv")
    
    cmd = "pytest tests/failing_test.py"
    
    # First execution -> allow
    decision, _ = watchdog.evaluate_command_execution(state, cmd)
    assert decision == "allow"
    state.commands_executed.append({"command": cmd, "exit_code": 1})
    
    # Second execution -> allow
    decision, _ = watchdog.evaluate_command_execution(state, cmd)
    assert decision == "allow"
    state.commands_executed.append({"command": cmd, "exit_code": 1})
    
    # Third execution (exceeds threshold 2) -> block
    decision, reason = watchdog.evaluate_command_execution(state, cmd)
    assert decision == "block"
    assert "ATLAS LOOP DETECTED" in reason

def test_dangerous_commands_blocked_immediately():
    watchdog = WatchdogEngine()
    state = SessionState(conversation_id="test_danger")
    
    dangerous_cmds = [
        "rm -rf /",
        "rm -rf *",
        "mkfs.ext4 /dev/sda1",
        "chmod -R 777 /",
    ]
    for cmd in dangerous_cmds:
        decision, reason = watchdog.evaluate_command_execution(state, cmd)
        assert decision == "block"
        assert "ATLAS SAFETY INTERVENTION" in reason

def test_file_reading_loop_warning():
    cfg = AtlasConfig(thresholds=WatchdogThresholds(max_file_reads_without_edit=3))
    watchdog = WatchdogEngine(cfg)
    state = SessionState(conversation_id="test_reads")
    
    file_path = "/path/to/source.py"
    state.files_viewed[file_path] = 3
    
    decision, reason = watchdog.evaluate_file_reading(state, file_path)
    assert decision == "warn"
    assert "ATLAS LOOP WARNING" in reason
