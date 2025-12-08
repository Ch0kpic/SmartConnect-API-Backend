#!/bin/bash
# Script para iniciar el servidor Django en desarrollo

echo "SmartConnect - Backend API"
echo "=========================="
echo ""

# Activar entorno virtual
source venv/Scripts/activate

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8000
