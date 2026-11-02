#!/usr/bin/env python3
"""
ATLAS Command Line Interface
Provides terminal status, manual rescue triggering, and auditing.
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from atlas.state import StateManager
from atlas.forensic import ForensicEngine
from atlas.config import DEFAULT_CONFIG

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
except ImportError:
    console = None

def cmd_status(args):
    mgr = StateManager()
    state = mgr.load_session(args.session)
    
    if console:
        table = Table(title=f"ATLAS Status — Sesión: {state.conversation_id}")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="magenta")
        table.add_row("Estado", f"[bold green]{state.current_status}[/bold green]" if state.current_status == "nominal" else f"[bold red]{state.current_status}[/bold red]")
        table.add_row("Pasos totales", str(state.total_steps))
        table.add_row("Comandos ejecutados", str(len(state.commands_executed)))
        table.add_row("Archivos modificados", str(len(state.files_modified)))
        table.add_row("Archivos consultados", str(len(state.files_viewed)))
        table.add_row("Puntos de control (Checkpoints)", str(len(state.checkpoints)))
        table.add_row("Advertencias recientes", str(len(state.recent_loop_warnings)))
        console.print(table)
    else:
        print(f"Sesión: {state.conversation_id}")
        print(f"Estado: {state.current_status}")
        print(f"Pasos: {state.total_steps}")
        print(f"Comandos: {len(state.commands_executed)}")

def cmd_rescue(args):
    mgr = StateManager()
    state = mgr.load_session(args.session)
    t_path = Path(args.transcript) if args.transcript else None
    if not t_path:
        brain_path = Path(f"/home/darwinsin/.gemini/antigravity/brain/{args.session}/.system_generated/logs/transcript.jsonl")
        if brain_path.exists():
            t_path = brain_path

    forensic = ForensicEngine(t_path)
    entries = forensic.parse_transcript() if t_path else []
    report = forensic.format_rescue_report(args.session, state.current_status, entries)
    
    if console:
        console.print(Panel(report, title="[bold red]ATLAS RESCUE DISPATCHER[/bold red]", expand=False))
    else:
        print(report)

def main():
    parser = argparse.ArgumentParser(description="ATLAS CLI Supervisor")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Muestra el estado de supervisión")
    p_status.add_argument("--session", default="default_session", help="ID de la conversación")
    p_status.set_defaults(func=cmd_status)

    # rescue
    p_rescue = subparsers.add_parser("rescue", help="Dispara el informe de rescate forense")
    p_rescue.add_argument("--session", default="default_session", help="ID de la conversación")
    p_rescue.add_argument("--transcript", default=None, help="Ruta al transcript.jsonl")
    p_rescue.set_defaults(func=cmd_rescue)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
