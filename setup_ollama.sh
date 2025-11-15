#!/bin/bash

echo "🔧 ArqLeads - Configuración de Ollama en WSL"
echo "=============================================="
echo ""

# Detectar IP del host Windows
WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')

if [ -z "$WINDOWS_IP" ]; then
    WINDOWS_IP=$(cat /etc/resolv.conf 2>/dev/null | grep nameserver | awk '{print $2}')
fi

if [ -z "$WINDOWS_IP" ]; then
    echo "❌ No se pudo detectar la IP de Windows automáticamente"
    echo ""
    echo "Por favor, encuentra tu IP manualmente:"
    echo "1. En Windows PowerShell, ejecuta: ipconfig"
    echo "2. Busca 'Adaptador de Ethernet vEthernet (WSL)' o similar"
    echo "3. Copia la 'Dirección IPv4' (ejemplo: 172.24.176.1)"
    echo ""
    read -p "Ingresa la IP de Windows: " WINDOWS_IP
fi

echo "✅ IP de Windows detectada: $WINDOWS_IP"
echo ""

# Probar conexión con Ollama
echo "🔍 Probando conexión con Ollama..."
OLLAMA_URL="http://$WINDOWS_IP:11434"

if curl -s --max-time 5 "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama está accesible en $OLLAMA_URL"

    # Listar modelos disponibles
    echo ""
    echo "📦 Modelos disponibles:"
    curl -s "$OLLAMA_URL/api/tags" | python3 -m json.tool | grep '"name"' | cut -d'"' -f4

else
    echo "❌ No se puede conectar a Ollama en $OLLAMA_URL"
    echo ""
    echo "Soluciones:"
    echo "1. Verifica que Ollama esté corriendo en Windows:"
    echo "   - Abre PowerShell y ejecuta: ollama list"
    echo ""
    echo "2. Configura Ollama para aceptar conexiones externas:"
    echo "   - En PowerShell (como administrador):"
    echo "     setx OLLAMA_HOST \"0.0.0.0:11434\""
    echo "     taskkill /F /IM ollama.exe"
    echo "     ollama serve"
    echo ""
    echo "3. Verifica el firewall de Windows:"
    echo "   - Permite conexiones entrantes en puerto 11434"
    echo ""
    exit 1
fi

# Actualizar .env
echo ""
echo "📝 Actualizando Backend/.env..."

if [ -f "Backend/.env" ]; then
    # Actualizar OLLAMA_BASE_URL
    if grep -q "OLLAMA_BASE_URL" Backend/.env; then
        sed -i "s|OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=$OLLAMA_URL|" Backend/.env
    else
        echo "OLLAMA_BASE_URL=$OLLAMA_URL" >> Backend/.env
    fi

    # Actualizar AI_PROVIDER
    if grep -q "AI_PROVIDER" Backend/.env; then
        sed -i "s|AI_PROVIDER=.*|AI_PROVIDER=ollama|" Backend/.env
    else
        echo "AI_PROVIDER=ollama" >> Backend/.env
    fi

    echo "✅ Archivo .env actualizado"
else
    echo "❌ No se encontró Backend/.env"
    exit 1
fi

echo ""
echo "✅ Configuración completa!"
echo ""
echo "Ahora puedes ejecutar:"
echo "  cd Backend"
echo "  python -m uvicorn app.main:app --reload"
echo ""
echo "Y probar el chat en: http://localhost:5173"
