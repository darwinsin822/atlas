#!/usr/bin/env bash
set -e

echo "=== Ejecutando ATLAS CI Suite ==="
export PYTHONPATH="/home/darwinsin/atlas:$PYTHONPATH"

/home/darwinsin/atlas/.venv/bin/pytest -v /home/darwinsin/atlas/tests

echo "=== Todas las pruebas pasaron con éxito ==="
