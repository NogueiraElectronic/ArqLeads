# 🏗️ ArqLeads - Sistema de Captación de Leads con IA para Arquitectura

> Sistema completo de chatbot inteligente para cualificación automática de leads de proyectos de arquitectura. Convierte visitantes web en clientes potenciales cualificados.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2-61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Private-red)]()

## 🎯 Características Principales

### Chatbot Inteligente
- ✅ Conversaciones naturales en español usando IA
- ✅ Respuestas breves y profesionales (2-3 líneas)
- ✅ Sin emojis ni lenguaje informal
- ✅ Tono consultivo y experto

### Cualificación Automática
- ✅ Extrae tipo de proyecto automáticamente
- ✅ Detecta presupuesto en formato flexible
- ✅ Identifica timeline y urgencia
- ✅ Captura ubicación geográfica
- ✅ Sistema de puntuación 0-100

### IA Gratuita o de Pago
- ✅ **Ollama**: 100% gratis, corre localmente (RECOMENDADO)
- ✅ **Anthropic Claude**: $5 gratis al registrarte
- ✅ **OpenAI GPT**: Requiere pago

### Base de Datos Completa
- ✅ PostgreSQL con historial de conversaciones
- ✅ Redis para caché y rate limiting
- ✅ Migraciones con Alembic

### Seguridad
- ✅ Rate limiting (protección anti-spam)
- ✅ Validación de inputs (anti XSS/SQLi)
- ✅ Sanitización de datos
- ✅ Secrets fuertes autogenerados

## 📋 Requisitos Previos

### Desarrollo Local (Recomendado)
- **Python 3.11+** → https://www.python.org/downloads/
- **Node.js 18+** → https://nodejs.org/
- **Docker Desktop** → https://www.docker.com/products/docker-desktop/
- **Ollama** (opcional) → https://ollama.com/download

### Todo con Docker (Alternativa)
- **Docker Desktop** únicamente

## 🚀 Instalación Rápida (15 minutos)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/NogueiraElectronic/ArqLeads.git
cd ArqLeads
```

### 2. Instalar Ollama (IA Gratuita - RECOMENDADO)

#### Windows:
1. Descarga: https://ollama.com/download/windows
2. Ejecuta el instalador `OllamaSetup.exe`
3. Abre PowerShell y descarga el modelo:
```powershell
ollama pull llama3.1
```

#### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
```

#### Mac:
```bash
brew install ollama
ollama pull llama3.1
```

Verifica la instalación:
```bash
ollama list
# Deberías ver: llama3.1
```

### 3. Configurar Variables de Entorno

El archivo `.env` ya está configurado para usar Ollama. Si quieres personalizarlo:

```bash
# Windows
notepad .env

# Linux/Mac
nano .env
```

Personaliza estos valores:

```env
# Studio Information
STUDIO_NAME=Mi Estudio de Arquitectura
STUDIO_LOCATION=Vigo, Galicia
STUDIO_SPECIALTIES=Viviendas unifamiliares,Reformas,Rehabilitaciones

# Chatbot
CHATBOT_NAME=AsistenteArq
CHATBOT_PERSONALITY=Profesional, cercano y experto

# AI Provider (ya configurado para Ollama - GRATIS)
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

### 4. Arrancar Base de Datos (Docker)

```bash
docker-compose up -d postgres redis
```

Verifica que están corriendo:
```bash
docker-compose ps
# Deberías ver postgres y redis como "Up"
```

### 5. Instalar y Arrancar Backend

#### Windows (PowerShell):
```powershell
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Linux/Mac:
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Espera a ver:** `✅ ArqLeads System ready!`

### 6. Instalar y Arrancar Frontend

**Abre OTRA terminal/ventana:**

```bash
cd frontend
npm install
npm run dev
```

**Espera a ver:** `VITE ... ready in ... ms`

### 7. Abrir la Aplicación

Abre tu navegador en: **http://localhost:5173/**

## 🧪 Probar el Chatbot

Ejemplo de conversación efectiva:

```
Usuario: Hola
Bot: Buenos días. ¿En qué proyecto estás trabajando?

Usuario: Quiero reformar un baño
Bot: Entendido. ¿Qué presupuesto aproximado tienes en mente?

Usuario: 20000 euros
Bot: Perfecto, 20.000 EUR. ¿En qué plazo te gustaría realizarla?

Usuario: 3 meses
Bot: 3 meses es razonable. ¿En qué zona sería el proyecto?

Usuario: Vigo centro
Bot: Entendido. Para coordinar mejor, ¿me podrías facilitar tu email o teléfono?
```

**Resultado:**
- ✅ Tipo: Reforma de apartamento
- ✅ Presupuesto: 20.000 EUR
- ✅ Timeline: 3 meses
- ✅ Ubicación: Vigo
- ✅ **Puntuación: 65/100 (Lead Tibio)**

## 📊 Dashboard y API

### API Docs (Swagger)
http://localhost:8000/docs

### Endpoints Principales

```bash
# Health Check
GET http://localhost:8000/health

# Enviar mensaje al chatbot
POST http://localhost:8000/api/v1/chat/message
{
  "session_id": "session-123",
  "message": "Hola",
  "language": "es",
  "channel": "web"
}

# Ver todos los leads
GET http://localhost:8000/api/v1/leads/

# Ver leads calientes (score >= 70)
GET http://localhost:8000/api/v1/leads/hot

# Ver estadísticas
GET http://localhost:8000/api/v1/leads/stats
```

## 🎨 Personalización

### Cambiar Nombre del Estudio

Edita `.env`:
```env
STUDIO_NAME=Arquitectura Moderna S.L.
STUDIO_LOCATION=Madrid
```

Reinicia el backend (Ctrl+C y vuelve a arrancar).

### Ajustar Especialidades

```env
STUDIO_SPECIALTIES=Obra nueva,Reformas integrales,Proyectos sostenibles,Diseño de interiores
```

### Modificar Comportamiento del Bot

Edita `Backend/app/core/services/chat_service.py` línea 43:

```python
def get_system_prompt(self) -> str:
    return f"""Eres {settings.CHATBOT_NAME}...

    # Añade tus reglas personalizadas aquí
    PROHIBIDO:
    - Hacer más de 1 pregunta por respuesta
    - Usar lenguaje técnico innecesario

    OBLIGATORIO:
    - Ser empático pero profesional
    - Reconocer cada dato que te proporcionen
    ```

Reinicia el backend.

### Cambiar el Modelo de IA

#### Usar un modelo más potente de Ollama:

```bash
ollama pull llama3.1:70b  # Mejor calidad pero más lento
```

Edita `.env`:
```env
OLLAMA_MODEL=llama3.1:70b
```

#### Usar OpenAI en lugar de Ollama:

1. Obtén API key: https://platform.openai.com/api-keys
2. Edita `.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-tu-key-aqui
```

#### Usar Anthropic Claude:

1. Regístrate: https://console.anthropic.com/ ($5 gratis)
2. Edita `.env`:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
```

## 🐳 Deployment en Producción

### Opción 1: Docker Compose (Simple)

```bash
# Build
docker-compose build

# Arrancar en producción
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down
```

### Opción 2: Servidor VPS (Recomendado)

**Requisitos:**
- Ubuntu 22.04 LTS
- 2GB RAM mínimo
- Docker instalado

```bash
# 1. En el servidor, clonar repo
git clone https://github.com/tu-user/ArqLeads.git
cd ArqLeads

# 2. Configurar .env para producción
nano .env
# Cambiar:
# - ENVIRONMENT=production
# - DEBUG=False
# - Generar SECRET_KEY nuevo
# - Configurar dominio en CORS_ORIGINS

# 3. Arrancar
docker-compose up -d

# 4. Configurar nginx reverse proxy
sudo nano /etc/nginx/sites-available/arqleads
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }
}
```

```bash
# Activar y recargar
sudo ln -s /etc/nginx/sites-available/arqleads /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL con Let's Encrypt
sudo certbot --nginx -d tu-dominio.com
```

## 🔧 Mantenimiento

### Ver Logs

```bash
# Backend
docker-compose logs -f backend

# PostgreSQL
docker-compose logs -f postgres

# Todos
docker-compose logs -f
```

### Backup de Base de Datos

```bash
# Exportar
docker-compose exec postgres pg_dump -U arqleads_user arqleads_db > backup.sql

# Importar
cat backup.sql | docker-compose exec -T postgres psql -U arqleads_user arqleads_db
```

### Actualizar el Sistema

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

## 🚨 Troubleshooting

### Error: "OpenAI API error: 401"
**Problema**: API key inválida o sin créditos

**Solución**: Cambia a Ollama (gratis)
```env
AI_PROVIDER=ollama
```

### Frontend muestra 404
**Problema**: No se generó el build o falta vite.config.ts

**Solución**:
```bash
cd frontend
npm install
npm run dev
```

### Backend no arranca
**Problema**: PostgreSQL no está corriendo

**Solución**:
```bash
docker-compose up -d postgres redis
docker-compose logs postgres
```

### Ollama no responde
**Problema**: Ollama no está corriendo

**Solución**:
```bash
# Windows: Abre Ollama desde el menú inicio
# Linux/Mac:
ollama serve
```

## 📁 Estructura del Proyecto

```
ArqLeads/
├── Backend/
│   ├── app/
│   │   ├── api/              # Endpoints REST
│   │   │   ├── chat.py       # Chatbot endpoints
│   │   │   ├── leads.py      # CRUD de leads
│   │   │   └── analytics.py  # Estadísticas
│   │   ├── core/             # Lógica de negocio
│   │   │   ├── config.py     # Configuración
│   │   │   ├── database.py   # DB connection
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── services/     # Chat service con IA
│   │   │   └── validators.py # Validación inputs
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Migraciones DB
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env
└── README.md
```

## 📈 Roadmap

- [x] Chatbot con IA (OpenAI/Anthropic/Ollama)
- [x] Cualificación automática de leads
- [x] Sistema de puntuación 0-100
- [x] Base de datos PostgreSQL
- [x] Rate limiting y seguridad
- [x] Soporte Ollama (100% gratis)
- [x] Respuestas breves y profesionales
- [ ] Dashboard admin web completo
- [ ] Notificaciones por email automáticas
- [ ] Integración WhatsApp Business
- [ ] CRM integration (HubSpot, Pipedrive)
- [ ] Multi-idioma (inglés, francés)
- [ ] Analytics avanzado con gráficos
- [ ] A/B testing de prompts
- [ ] Exportación de leads a CSV/Excel

## 🔐 Seguridad

### En Producción

1. **Generar secrets fuertes**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Configurar CORS**:
```env
CORS_ORIGINS=["https://tu-dominio.com"]
```

3. **Rate limiting**:
```env
RATE_LIMIT=50/minute
```

4. **SSL/HTTPS** obligatorio con Let's Encrypt

## 📝 Licencia

Proyecto privado - Todos los derechos reservados

## 💬 Soporte

¿Problemas? Contacta a través de GitHub Issues

---

**Desarrollado con ❤️ para estudios de arquitectura**
