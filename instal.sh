#!/bin/bash
python3 -m venv .venv #Crear entorno virtual en la carpeta actual
source .venv/bin/activate #Activar entorno virtual
pip install --upgrade pip # Actualizar pip si es posible
pip3 install -r requirements.txt #Instalar con pip la lista de librerías del archivo

