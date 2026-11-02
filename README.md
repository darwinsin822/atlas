<div align="center">

![ATLAS Banner](assets/atlas_banner.jpg)

# 🌐 ATLAS
### Autonomous Task Limitation & Agent Supervision
*Sistema de supervisión, prevención de bucles infinitos y recuperación determinista para agentes de codificación en Google Antigravity 2.0 (Linux Mint Cinnamon).*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/MCP-2.x%20%2F%201.x-cyan.svg)](https://modelcontextprotocol.io/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20Mint%20Cinnamon-orange.svg)]()

> **"Detenerse es mejor que repetirse. Preguntar a tiempo es mejor que fracasar en silencio."**

</div>

---

## ⚡ Descripción

**ATLAS** actúa como un supervisor y árbitro de ejecución para modelos autónomos (Gemini / Claude / DeepSeek) que operan en **Google Antigravity 2.0**. Detecta de manera proactiva desvíos de objetivo (*drift*), bucles infinitos de comandos, lecturas circulares de archivos y reintentos repetitivos sin progreso observable.

Al detectar una anomalía crítica o comando peligroso, ATLAS congela la invocación a nivel de hook de ciclo de vida (`PreToolUse`), exigiendo confirmación interactiva al usuario y habilitando el protocolo forense de rescate con opciones deterministas **A**, **B** y **C**.

---

## 🏛️ Arquitectura del Sistema

```
                    ┌────────────────────────────────────────────────────────┐
                    │            GOOGLE ANTIGRAVITY 2.0 ENGINE               │
                    └──────────────┬─────────────────────────▲───────────────┘
                                   │                         │
               1. PreToolUse Event │                         │ 4. "force_ask" / "allow"
                                   ▼                         │
                    ┌──────────────────────────────┐         │
                    │   ATLAS HOOK DISPATCHER      │─────────┘
                    │   (pre_tool.py < 15ms)       │
                    └──────────────┬───────────────┘
                                   │
                     Evalúa reglas │
                                   ▼
          ┌──────────────────────────────────────────────────┐
          │                  ATLAS WATCHDOG                  │
          │  - Detecta comandos idénticos o cuasi-idénticos   │
          │  - Detecta lecturas cíclicas del mismo archivo   │
          │  - Cuenta reintentos (umbral 2 estrategia / 3 tot)│
          │  - Escanea comandos destructivos / peligrosos    │
          │  - Mide ciclos sin progreso verificable          │
          └────────────────────────┬─────────────────────────┘
                                   │
              Estado & Auditoría   │ Lectura Forense
                                   ▼
          ┌──────────────────────────────────────────────────┐
          │              ATLAS FORENSIC ENGINE               │
          │  - Parseo reactivo de transcript.jsonl           │
          │  - Reconstrucción de la sesión activa            │
          │  - Detección de desviación de objetivos (drift)   │
          └────────────────────────┬─────────────────────────┘
                                   │
                                   ▼
                 ┌───────────────────────────────────┐
                 │        INTERFAZ DE RESCATE        │
                 │   - Skill `/atlas-rescue`         │
                 │   - Servidor MCP (`atlas-mcp`)    │
                 │   - CLI (`atlas status / report`) │
                 └───────────────────────────────────┘
```

---

## 🛡️ Límites Infranqueables del Watchdog

- **Máximo 2 intentos consecutivos** con la misma estrategia o comandos cuasi-idénticos.
- **Máximo 3 intentos totales** sobre el mismo problema fallido en una sesión.
- **Alerta tras 2 ciclos** sin progreso observable ni modificación de archivos.
- **Bloqueo preventivo inmediato** de patrones destructivos (`rm -rf /`, `rm -rf *`, `mkfs`, fork bombs, modificación de permisos de raíz).

---

## 🚨 Protocolo de Rescate (/atlas-rescue)

Cuando ATLAS interviene o el usuario invoca `/atlas-rescue`, el sistema genera el informe forense estructurado con 3 vías de salida:

```text
============================================================
  🚨 ATLAS RESCUE: SUPERVISIÓN Y RECUPERACIÓN DE AGENTE
============================================================
Sesión Activa:      <conversation_id>
Motivo de Parada:   <loop_detected / stall / dangerous_command>
Pasos Totales:      <N>
Archivos Editados:  <N>
Comandos Ejecutados:<N>
------------------------------------------------------------
📋 Objetivo Inicial Detectado:
   <objetivo extraído directamente del transcript>
------------------------------------------------------------
OPCIONES DE RECUPERACIÓN:
  [Opción A] Corregir rumbo: Indicar nueva instrucción directa y continuar.
  [Opción B] Retomar desde punto seguro: Descartar últimos pasos y reintentar con otra estrategia.
  [Opción C] Redefinir: Pausar, replantear el objetivo en subtareas o solicitar intervención humana.
============================================================
```

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/darwinsin822/atlas.git /home/darwinsin/atlas
cd /home/darwinsin/atlas
```

### 2. Configurar entorno y dependencias
```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

### 3. Instalar hooks y registrar servidor MCP
```bash
bash scripts/install.sh
```

### 4. Ejecutar la suite de pruebas
```bash
bash scripts/ci.sh
```

### 5. Comandos CLI
```bash
# Ver estado de supervisión en tiempo real
atlas status --session <conversation_id>

# Ejecutar informe forense y rescate
atlas rescue --session <conversation_id>
```

---

## 🤝 Créditos y Filosofía

Desarrollado para entornos de desarrollo con Inteligencia Artificial autónoma. Diseñado con la premisa de que la autonomía real requiere límites deterministas y verificables.
