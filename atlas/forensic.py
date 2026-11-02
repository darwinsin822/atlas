"""
ATLAS Forensic Engine
Parses transcript.jsonl, extracts chronological execution traces,
detects divergence (drift), and compiles recovery status reports.
"""
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ForensicEngine:
    def __init__(self, transcript_path: Optional[Path] = None):
        self.transcript_path = transcript_path

    def parse_transcript(self, path: Optional[Path] = None) -> List[Dict[str, Any]]:
        target_path = path or self.transcript_path
        if not target_path or not Path(target_path).exists():
            return []
        
        entries = []
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            return []
        return entries

    def extract_summary(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extracts key forensic telemetry:
        - initial_prompt
        - tool_invocations count by tool
        - executed commands sequence
        - modified files
        - errors encountered
        """
        initial_prompt = ""
        tool_counts: Dict[str, int] = {}
        commands: List[Dict[str, Any]] = []
        files_modified: List[str] = []
        errors: List[str] = []

        for step in entries:
            step_type = step.get("type", "")
            # Extract initial user prompt
            if step_type == "USER_INPUT" and not initial_prompt:
                initial_prompt = step.get("content", "")

            # Tool calls
            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                tool_name = call.get("name", call.get("toolName", "unknown"))
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

                args = call.get("args", {})
                if tool_name == "run_command":
                    cmd = args.get("CommandLine", "")
                    commands.append({
                        "step_index": step.get("step_index", 0),
                        "command": cmd,
                        "cwd": args.get("Cwd", ""),
                    })
                elif tool_name in ("replace_file_content", "write_to_file"):
                    target = args.get("TargetFile", "")
                    if target and target not in files_modified:
                        files_modified.append(target)

            # Errors in step
            if step.get("status") == "ERROR":
                errors.append(step.get("content", "Unknown error"))

        return {
            "initial_prompt": initial_prompt[:500] if initial_prompt else "No registrado",
            "total_steps": len(entries),
            "tool_counts": tool_counts,
            "commands": commands,
            "files_modified": files_modified,
            "error_count": len(errors),
            "recent_errors": errors[-3:] if errors else [],
        }

    def format_rescue_report(
        self,
        conversation_id: str,
        reason: str,
        entries: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        summary = self.extract_summary(entries or [])
        report = []
        report.append("=" * 60)
        report.append("  🚨 ATLAS RESCUE: SUPERVISIÓN Y RECUPERACIÓN DE AGENTE")
        report.append("=" * 60)
        report.append(f"Sesión Activa:      {conversation_id}")
        report.append(f"Motivo de Parada:   {reason}")
        report.append(f"Pasos Totales:      {summary.get('total_steps', 0)}")
        report.append(f"Archivos Editados:  {len(summary.get('files_modified', []))}")
        report.append(f"Comandos Ejecutados:{len(summary.get('commands', []))}")
        report.append("-" * 60)
        report.append("📋 Objetivo Inicial Detectado:")
        report.append(f"   {summary.get('initial_prompt', 'N/A')[:200]}...")
        report.append("-" * 60)
        report.append("🛠️ Desglose de Herramientas Usadas:")
        for t, count in summary.get("tool_counts", {}).items():
            report.append(f"   - {t}: {count} llamadas")
        report.append("=" * 60)
        report.append("OPCIONES DE RECUPERACIÓN:")
        report.append("  [Opción A] Corregir rumbo: Indicar nueva instrucción directa y continuar.")
        report.append("  [Opción B] Retomar desde punto seguro: Descartar últimos pasos y reintentar con otra estrategia.")
        report.append("  [Opción C] Redefinir: Pausar, replantear el objetivo en subtareas o solicitar intervención humana.")
        report.append("=" * 60)
        return "\n".join(report)
