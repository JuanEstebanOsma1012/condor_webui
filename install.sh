#!/bin/bash
# ===============================================================
# Script de instalación y configuración de la aplicación
# Debe ejecutarse como superusuario (root)
# ===============================================================

set -e  # Detiene la ejecución si hay un error

# --- 1. Verificar que se ejecuta como root ---
if [ "$EUID" -ne 0 ]; then
  echo "❌ Este script debe ejecutarse como superusuario (root)."
  exit 1
fi

# --- 2. Variables ---
REPO_URL="AQUI_VA_LA_URL_DEL_REPOSITORIO"   # <-- Sustituye con la URL real
APP_DIR="/opt/app"
SERVICE_FILE="/etc/systemd/system/grid-app.service"
REQUIREMENTS_FILE="$(dirname "$0")/requirements.txt"

# --- 3. Instalar dependencias necesarias ---
echo "🔧 Verificando instalación de dependencias del sistema..."
apt-get update -y
apt-get install -y git python3 python3-pip

# --- 4. Clonar el repositorio ---
echo "📦 Clonando repositorio en /opt..."
cd /opt
if [ -d "$APP_DIR" ]; then
  echo "⚠️  El directorio $APP_DIR ya existe. Eliminando..."
  rm -rf "$APP_DIR"
fi
git clone "$REPO_URL" "$APP_DIR"

# --- 5. Instalar dependencias de Python ---
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "📚 Instalando dependencias desde requirements.txt..."
  pip3 install --no-cache-dir -r "$REQUIREMENTS_FILE"
else
  echo "⚠️  No se encontró el archivo requirements.txt en $REQUIREMENTS_FILE"
fi

# --- 6. Crear archivo de unidad del servicio ---
echo "🧩 Creando archivo de unidad systemd..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Aplicación para enviar trabajos de HTCondor a través del grid
After=network.target

[Service]
User=pi
Group=pi
Type=simple
ExecStart=/usr/bin/python3 /opt/app/app.py --host=0.0.0.0 --port=5000
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# --- 7. Recargar daemon y habilitar servicio ---
echo "🔄 Recargando systemd..."
systemctl daemon-reload
sleep 2

echo "✅ Habilitando y arrancando servicio..."
systemctl enable grid-app.service
systemctl start grid-app.service

# --- 8. Verificar estado del servicio ---
echo "📋 Verificando estado del servicio..."
systemctl status grid-app.service --no-pager

echo "🎉 Instalación y configuración completadas con éxito."