# 🏗️ ArqLeads System

Sistema de Captación Automatizada de Leads para Estudios de Arquitectura con IA.

## 🚀 Inicio Rápido

### 1. Verificar Prerequisitos
```bash
docker --version
docker-compose --version
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env` en la raíz del proyecto y configura:

- `OPENAI_API_KEY` → Tu clave de OpenAI
- `NOTIFICATION_EMAILS` → Tu email
- `STUDIO_NAME` → Nombre de tu estudio

### 3. Levantar el Sistema
```bash
docker-compose up -d
```

### 4. Verificar que Funciona

Abre tu navegador:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📊 Endpoints Principales

- `POST /api/v1/chat/message` - Enviar mensaje al chatbot
- `GET /api/v1/leads/` - Ver todos los leads
- `GET /api/v1/leads/hot` - Ver leads calientes
- `GET /api/v1/leads/stats` - Estadísticas

## 🛠️ Comandos Útiles
```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar todo
docker-compose stop

# Borrar todo (CUIDADO)
docker-compose down -v
```

## 📧 Soporte

Desarrollado por Jesús Nogueira
```

---

## 🎉 ¡AHORA SÍ, VAMOS A ARRANCAR TODO!

### PASO 1: Verificar Estructura de Archivos

Primero, verifica que tienes esta estructura:
```
arq-lead-system/
├── .env                          ← Configuración principal
├── docker-compose.yml            ← Configuración de Docker
├── README.md                     ← Documentación
└── backend/
    ├── .env                      ← Configuración del backend
    ├── requirements.txt          ← Dependencias Python
    ├── Dockerfile                ← Imagen Docker
    └── app/
        ├── __init__.py
        ├── main.py               ← Archivo principal
        ├── core/
        │   ├── __init__.py
        │   ├── config.py
        │   └── database.py
        ├── models/
        │   ├── __init__.py
        │   ├── lead.py
        │   ├── conversation.py
        │   └── message.py
        ├── services/
        │   ├── __init__.py
        │   └── chat_service.py
        └── api/
            ├── __init__.py
            ├── chat.py
            ├── leads.py
            └── analytics.py