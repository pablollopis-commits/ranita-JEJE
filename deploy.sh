#!/bin/bash

echo "🚀 Preparando cambios para subir a GitHub..."

# Añadir todos los archivos modificados
git add .

# Crear commit con la fecha actual
git commit -m "Actualización automática: $(date '+%d/%m/%Y a las %H:%M')"

# Subir a GitHub
git push origin main

echo "✅ Cambios subidos correctamente a GitHub"


