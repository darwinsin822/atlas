# ATLAS — Autonomous Task Limitation & Agent Supervision
> **"Detenerse es mejor que repetirse. Preguntar a tiempo es mejor que fracasar en silencio."**

ATLAS es un sistema integral de supervisión, prevención de bucles infinitos y recuperación determinista para agentes de codificación autónomos, optimizado para **Google Antigravity 2.0** en Linux Mint Cinnamon.

---

## Componentes

1. **Watchdog (`atlas.watchdog`):**
   - Límite de 2 comandos consecutivos idénticos o cuasi-idénticos.
   - Máximo 3 intentos sobre el mismo problema antes de requerir intervención.
   - Bloqueo preventivo de comandos destructivos (`rm -rf /`, `mkfs`, fork bombs, etc.).
   - Alerta ante lecturas repetitivas de archivos sin ediciones intermedias.

2. **Ganchos de Ciclo de Vida (`atlas.hooks`):**
   - `pre_tool.py`: Hook `PreToolUse` síncrono ultra-rápido (<15 ms) que intercepta llamadas a herramientas y emite `"force_ask"` para detener bucles en Antigravity.
   - `post_tool.py`: Hook `PostToolUse` para telemetría continua y contadores de sesión.

3. **Servidor MCP (`atlas.mcp`):**
   - `atlas_status`: Consulta el estado del supervisor y métricas de sesión.
   - `atlas_checkpoint`: Registra puntos de control seguros antes de refactorizaciones complejas.
   - `atlas_loop_check`: Permite al agente autoverificarse antes de reintentar comandos.
   - `atlas_report`: Genera un informe forense detallado a partir de `transcript.jsonl`.
   - `atlas_resume`: Reanuda la sesión bajo una de las 3 opciones de rescate (A, B o C).

4. **Skill de Antigravity (`/atlas-rescue`):**
   - Protocolo estandarizado de recuperación accesible directamente en el prompt del usuario.

5. **CLI (`atlas`):**
   - Comandos de terminal: `atlas status` y `atlas rescue`.

---

## Instalación y Verificación

```bash
# Instalar hooks y registrar servidor MCP
bash /home/darwinsin/atlas/scripts/install.sh

# Ejecutar suite de pruebas
bash /home/darwinsin/atlas/scripts/ci.sh
```
