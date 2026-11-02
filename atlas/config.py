"""
ATLAS Configuration Module
Defines system thresholds, detection heuristics, and risk policies.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class WatchdogThresholds:
    max_consecutive_identical_commands: int = 2
    max_similar_commands_per_target: int = 2
    max_attempts_per_problem: int = 3
    max_file_reads_without_edit: int = 3
    max_cycles_without_progress: int = 2
    command_similarity_ratio: float = 0.85

@dataclass
class AtlasConfig:
    enabled: bool = True
    workspace_root: Path = Path("/home/darwinsin/atlas")
    data_dir: Path = Path("/home/darwinsin/.gemini/antigravity/atlas")
    thresholds: WatchdogThresholds = field(default_factory=WatchdogThresholds)
    
    # Dangerous commands requiring immediate intervention or confirmation
    dangerous_command_patterns: List[str] = field(default_factory=lambda: [
        r"\brm\s+-(?:r|f|rf|fr)\s+/(?:$|\s)",
        r"\brm\s+-(?:r|f|rf|fr)\s+\*",
        r"\bmkfs\b",
        r"\bdd\s+if=.*of=/dev/",
        r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",  # Fork bomb
        r"\bchmod\s+-R\s+777\s+/",
        r"\bchown\s+-R.*root\s+/",
        r">\s*/dev/sd[a-z]",
        r">\s*/dev/nvme",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bkillall\s+-9\s+(?:systemd|init|cinnamon|Xorg)",
    ])
    
    # Sensitive file patterns
    sensitive_path_patterns: List[str] = field(default_factory=lambda: [
        r"\.env(?:\..+)?$",
        r"id_rsa",
        r"id_ed25519",
        r".*\.pem$",
        r".*\.key$",
        r"credentials\.json",
        r"\.netrc$",
        r"\.bash_history$",
    ])

DEFAULT_CONFIG = AtlasConfig()
