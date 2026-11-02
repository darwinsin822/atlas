"""
ATLAS Session & Checkpoint State Management
Maintains in-memory and file-backed telemetry of the active session.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

@dataclass
class Checkpoint:
    id: str
    timestamp: str
    description: str
    files_state: Dict[str, str] = field(default_factory=dict)
    git_head: Optional[str] = None
    step_index: int = 0

@dataclass
class SessionState:
    conversation_id: str
    initial_objective: str = ""
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    current_status: str = "nominal"  # nominal, warning, loop_detected, halted
    total_steps: int = 0
    commands_executed: List[Dict[str, Any]] = field(default_factory=list)
    files_viewed: Dict[str, int] = field(default_factory=dict)
    files_modified: Dict[str, int] = field(default_factory=dict)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    recent_loop_warnings: List[str] = field(default_factory=list)
    consecutive_no_progress_cycles: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        checkpoints = [
            Checkpoint(**cp) if isinstance(cp, dict) else cp 
            for cp in data.get("checkpoints", [])
        ]
        data_copy = dict(data)
        data_copy["checkpoints"] = checkpoints
        return cls(**data_copy)

class StateManager:
    def __init__(self, base_dir: Path = Path("/home/darwinsin/.gemini/antigravity/atlas")):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _session_file(self, conversation_id: str) -> Path:
        safe_id = "".join(c for c in conversation_id if c.isalnum() or c in ("-", "_"))
        return self.sessions_dir / f"{safe_id}.json"

    def load_session(self, conversation_id: str) -> SessionState:
        filepath = self._session_file(conversation_id)
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return SessionState.from_dict(data)
            except Exception:
                pass
        return SessionState(conversation_id=conversation_id)

    def save_session(self, state: SessionState) -> None:
        filepath = self._session_file(state.conversation_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
