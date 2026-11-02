"""
ATLAS Watchdog Engine
Core repetition, infinite loop, and dangerous command detection algorithms.
"""
import difflib
import re
from typing import Dict, Any, Tuple, Optional
from .config import AtlasConfig, DEFAULT_CONFIG
from .state import SessionState

class WatchdogEngine:
    def __init__(self, config: AtlasConfig = DEFAULT_CONFIG):
        self.config = config

    def check_dangerous_command(self, cmd_line: str) -> Tuple[bool, Optional[str]]:
        for pattern in self.config.dangerous_command_patterns:
            if re.search(pattern, cmd_line, re.IGNORECASE):
                return True, f"Dangerous command pattern matched: {pattern}"
        return False, None

    def calculate_similarity(self, s1: str, s2: str) -> float:
        if s1 == s2:
            return 1.0
        matcher = difflib.SequenceMatcher(None, s1.strip(), s2.strip())
        return matcher.ratio()

    def evaluate_command_execution(
        self, state: SessionState, cmd_line: str
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluates command repetition:
        - Max 2 consecutive identical or highly similar commands.
        - Max 3 total attempts of the same failing command.
        Returns ('allow' | 'warn' | 'block', reason)
        """
        # 1. Check dangerous patterns first
        is_dangerous, dang_reason = self.check_dangerous_command(cmd_line)
        if is_dangerous:
            return "block", f"ATLAS SAFETY INTERVENTION: {dang_reason}"

        recent_cmds = state.commands_executed[-5:] if state.commands_executed else []
        if not recent_cmds:
            return "allow", None

        # Check consecutive identical or similar
        identical_consecutive = 0
        similar_consecutive = 0
        normalized_target = cmd_line.strip()

        for past in reversed(recent_cmds):
            past_cmd = past.get("command", "").strip()
            if past_cmd == normalized_target:
                identical_consecutive += 1
            else:
                sim = self.calculate_similarity(past_cmd, normalized_target)
                if sim >= self.config.thresholds.command_similarity_ratio:
                    similar_consecutive += 1
                else:
                    break

        if identical_consecutive >= self.config.thresholds.max_consecutive_identical_commands:
            return (
                "block",
                f"ATLAS LOOP DETECTED: Command repeated {identical_consecutive} times consecutively. "
                "Detenerse es mejor que repetirse."
            )

        if (identical_consecutive + similar_consecutive) >= self.config.thresholds.max_similar_commands_per_target:
            return (
                "warn",
                f"ATLAS REPETITION WARNING: Similar command executed repeatedly ({identical_consecutive + similar_consecutive} times)."
            )

        # Total attempts for the same failing command
        total_attempts = sum(
            1 for c in state.commands_executed 
            if c.get("command", "").strip() == normalized_target and c.get("exit_code", 0) != 0
        )
        if total_attempts >= self.config.thresholds.max_attempts_per_problem:
            return (
                "block",
                f"ATLAS STALL DETECTED: Command failed {total_attempts} times in this session without resolution."
            )

        return "allow", None

    def evaluate_file_reading(
        self, state: SessionState, file_path: str
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluates repetitive file reading without intermediate editing or progress.
        """
        reads = state.files_viewed.get(file_path, 0)
        edits = state.files_modified.get(file_path, 0)
        
        # If viewed multiple times without edits
        if reads >= self.config.thresholds.max_file_reads_without_edit and edits == 0:
            return (
                "warn",
                f"ATLAS LOOP WARNING: File '{file_path}' has been read {reads} times without any modification."
            )
        return "allow", None
