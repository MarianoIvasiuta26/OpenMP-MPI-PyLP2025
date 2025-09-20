#! /bin/bash

echo "Programación Paralela con OpenMP con Cython"

echo "================================================"
echo "Configurando el entorno virtual..."

echo "Creando el entorno virtual..."
python3 -m venv venv

echo "Activando el entorno virtual..."
source venv/bin/activate

echo "Instalando las dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Entorno virtual configurado ==="
echo "Para activar el entorno virtual, ejecuta:"
echo "source venv/bin/activate"

echo "================================================"

echo "Para ejecutar el programa, ejecuta:"
echo "python3 main.py"

echo "================================================"

echo "Para desactivar el entorno virtual, ejecuta:"
echo "deactivate"

echo "================================================"

echo "Para eliminar el entorno virtual, ejecuta:"
echo "rm -rf venv"

echo "================================================"