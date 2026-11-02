#!/usr/bin/env python3
"""
Simulador de bucle y rescate de ATLAS en Antigravity.
1. Simula un agente atrapado reintentando el mismo comando fallido.
2. Comprueba cómo el Watchdog intercepta y bloquea la ejecución.
3. Dispara el análisis forense y el protocolo de rescate con opciones A, B y C.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.state import StateManager
from atlas.forensic import ForensicEngine
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_simulation():
    session_id = "simulacion_bucle_demo"
    hook_path = Path("/home/darwinsin/atlas/atlas/hooks/pre_tool.py")
    post_hook_path = Path("/home/darwinsin/atlas/atlas/hooks/post_tool.py")
    
    # Limpiar estado previo de la simulación
    mgr = StateManager()
    state = mgr.load_session(session_id)
    state.commands_executed.clear()
    state.current_status = "nominal"
    mgr.save_session(state)

    failing_command = "cargo build --release"
    console.print(Panel(f"[bold cyan]Iniciando simulación de bucle con el comando:[/bold cyan] [yellow]{failing_command}[/yellow]", title="🤖 SIMULACIÓN DE AGENTE"))

    # Intentos del agente
    for intento in range(1, 4):
        payload = {
            "conversationId": session_id,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": failing_command}
            }
        }

        # Ejecutar hook PreToolUse
        res = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        decision_data = json.loads(res.stdout)
        decision = decision_data.get("decision")
        
        console.print(f"\n[bold]Paso {intento}:[/bold] Llamada a 'run_command' -> Respuesta de ATLAS: [bold {'green' if decision == 'allow' else 'red'}]{decision}[/bold {'green' if decision == 'allow' else 'red'}]")

        if decision == "force_ask":
            console.print(f"[bold red]🛑 BLOQUEO ACTIVADO:[/bold red] {decision_data.get('reason')}")
            break

        # Simular fallo en PostToolUse
        post_payload = {
            "conversationId": session_id,
            "toolCall": payload["toolCall"],
            "toolResult": {"exitCode": 101, "output": "error: could not compile `crate`"}
        }
        subprocess.run(
            ["python3", str(post_hook_path)],
            input=json.dumps(post_payload),
            text=True,
            capture_output=True
        )

    # Mostrar reporte de rescate generado
    console.print("\n" + "="*70)
    console.print("[bold yellow]DISPARANDO PROTOCOLO DE RESCATE ATLAS (/atlas-rescue):[/bold yellow]")
    console.print("="*70 + "\n")
    
    state = mgr.load_session(session_id)
    forensic = ForensicEngine()
    
    synthetic_transcript = [
        {"step_index": 0, "type": "USER_INPUT", "content": "Compila el proyecto Rust optimizado"},
        {"step_index": 1, "type": "MODEL", "tool_calls": [{"name": "run_command", "args": {"CommandLine": failing_command}}]},
        {"step_index": 2, "type": "MODEL", "tool_calls": [{"name": "run_command", "args": {"CommandLine": failing_command}}]},
    ]
    report = forensic.format_rescue_report(session_id, state.current_status, synthetic_transcript)
    console.print(report)

if __name__ == "__main__":
    run_simulation()
