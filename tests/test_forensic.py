"""
Tests for ATLAS Forensic Engine
Validates parsing of transcript.jsonl, extracting objectives, and rescue report formatting.
"""
import json
from pathlib import Path
from atlas.forensic import ForensicEngine

def test_forensic_extract_summary(tmp_path):
    transcript_file = tmp_path / "transcript.jsonl"
    events = [
        {
            "step_index": 0,
            "type": "USER_INPUT",
            "content": "Refactor the database layer and add migrations",
        },
        {
            "step_index": 1,
            "type": "MODEL",
            "tool_calls": [
                {
                    "name": "run_command",
                    "args": {"CommandLine": "python3 manage.py migrate"}
                }
            ]
        },
        {
            "step_index": 2,
            "type": "MODEL",
            "tool_calls": [
                {
                    "name": "write_to_file",
                    "args": {"TargetFile": "/app/models.py"}
                }
            ]
        }
    ]
    with open(transcript_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    forensic = ForensicEngine(transcript_file)
    entries = forensic.parse_transcript()
    assert len(entries) == 3

    summary = forensic.extract_summary(entries)
    assert "Refactor the database" in summary["initial_prompt"]
    assert summary["tool_counts"]["run_command"] == 1
    assert summary["tool_counts"]["write_to_file"] == 1
    assert "/app/models.py" in summary["files_modified"]

    report = forensic.format_rescue_report("test_conv_123", "loop_detected", entries)
    assert "ATLAS RESCUE: SUPERVISIÓN Y RECUPERACIÓN" in report
    assert "[Opción A]" in report
    assert "[Opción B]" in report
    assert "[Opción C]" in report
