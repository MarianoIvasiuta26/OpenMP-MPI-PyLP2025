#! /bin/bash

echo "Programación Paralela con MPI simulado en Python"

echo "================================================"
echo "Configurando el entorno virtual..."

echo "Creando el entorno virtual..."
python3 -m venv venv

echo "=== Entorno virtual configurado ==="
echo "Para activar el entorno virtual, ejecuta:"
echo "source venv/bin/activate"

echo "================================================"

echo "Para ejecutar el programa, ejecuta:"
echo "python3 main.py --make-dummy --dummy-n 3 --dummy-lines 50000"

echo "Para ejecutar con 2 procesos, ejecuta:"
echo "mpirun -n 2 python3 main.py --make-dummy --dummy-n 3 --dummy-lines 50000"

echo "================================================"

echo "Para desactivar el entorno virtual, ejecuta:"
echo "deactivate"

echo "================================================"

echo "Para eliminar el entorno virtual, ejecuta:"
echo "rm -rf venv"

echo "================================================"