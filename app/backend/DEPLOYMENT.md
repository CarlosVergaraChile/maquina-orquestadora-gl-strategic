# Guía de Despliegue - Máquina Orquestadora v2.3

Documentación completa para desplegar y ejecutar la Máquina Orquestadora de IA GL Strategic en producción.

## Índice

- [Requisitos Previos](#requisitos-previos)
- [Configuración Local](#configuracion-local)
- [Variables de Entorno](#variables-de-entorno)
- [Ejecución del Servidor](#ejecucion-del-servidor)
- [Comprobaciones de Salud](#comprobaciones-de-salud)
- [Endpoints API](#endpoints-api)
- [Base de Datos](#base-de-datos)
- [Resolución de Problemas](#resolucion-de-problemas)
- [Despliegue en Producción](#despliegue-en-produccion)

## Requisitos Previos

### Sistema
- Python 3.8+
- pip (gestor de paquetes de Python)
- SQLite3
- Git

### Paquetes Python
```bash
pip install fastapi uvicorn pydantic anthropic pytest pytest-asyncio python-dotenv
```

### Claude API Key
- Obtener clave de API de Anthropic: https://console.anthropic.com
- Generar una clave de API de prueba

## Configuración Local

### 1. Clonar repositorio
```bash
git clone https://github.com/CarlosVergaraChile/maquina-orquestadora-gl-strategic.git
cd maquina-orquestadora-gl-strategic/app/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

Si no hay archivo requirements.txt, instalar manualmente:
```bash
pip install fastapi uvicorn pydantic anthropic pytest pytest-asyncio python-dotenv
```

## Variables de Entorno

### Crear archivo .env
```bash
touch .env
```

### Contenido de .env
```env
# API Key de Claude (REQUERIDO)
CLAUDE_API_KEY=sk-ant-...

# Puerto del servidor (opcional, default: 8000)
PORT=8000

# Modo debug (opcional, default: False)
DEBUG=False

# Ubicación de la base de datos (opcional)
DB_PATH=data/conversations.db
```

### Cargar variables de entorno
```bash
export $(cat .env | xargs)  # En Linux/Mac
set -a && source .env && set +a  # En Bash
```

## Ejecución del Servidor

### Modo Desarrollo
```bash
python server.py
```

El servidor estará disponible en: `http://localhost:8000`

### Modo Producción
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Con variables de entorno
```bash
PORT=8000 DEBUG=False python server.py
```

## Comprobaciones de Salud

### 1. Endpoint Raíz
```bash
curl http://localhost:8000/
```

**Respuesta esperada:**
```json
{
  "name": "Máquina Orquestadora GL Strategic",
  "version": "2.3.0",
  "status": "online",
  "claude_api": "ready",
  "features": [...],
  "endpoints": {...}
}
```

### 2. Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00.000000",
  "database": "connected",
  "claude_api": "ready",
  "components": {
    "database": "operational",
    "orchestrator": "operational",
    "api": "operational"
  }
}
```

### 3. Documentación Interactiva
Acceder a Swagger UI: `http://localhost:8000/api/docs`

## Endpoints API

### POST /ask
Ejecutar pregunta con Claude

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, cómo estoy?",
    "user_id": "user123"
  }'
```

**Respuesta:**
```json
{
  "response": "Hola! Estoy bien, gracias por preguntar...",
  "emotion": "confident",
  "timestamp": "2024-01-20T10:30:00.000000",
  "model": "claude-3-5-sonnet-20241022"
}
```

### GET /history
Obtener historial de conversaciones

```bash
curl http://localhost:8000/history?user_id=user123&limit=20
```

### GET /users
Listar usuarios activos

```bash
curl http://localhost:8000/users
```

### DELETE /clear/{user_id}
Limpiar historial de usuario

```bash
curl -X DELETE http://localhost:8000/clear/user123
```

### GET /metrics
Obtener métricas del sistema

```bash
curl http://localhost:8000/metrics
```

## Base de Datos

### Ubicación
Por defecto: `data/conversations.db`

### Estructura

**Tabla: users**
- id (INTEGER PRIMARY KEY)
- user_id (TEXT UNIQUE)
- created_at (TEXT)
- updated_at (TEXT)

**Tabla: conversations**
- id (INTEGER PRIMARY KEY)
- user_id (TEXT FOREIGN KEY)
- role (TEXT) - "user" | "assistant" | "system"
- content (TEXT)
- emotion (TEXT) - opcional
- model (TEXT) - opcional
- timestamp (TEXT)

**Tabla: messages**
- id (INTEGER PRIMARY KEY)
- conversation_id (INTEGER FOREIGN KEY)
- role (TEXT)
- content (TEXT)
- timestamp (TEXT)

### Respaldo de Base de Datos
```bash
cp data/conversations.db data/conversations.db.backup
```

### Limpiar Base de Datos
```bash
rm data/conversations.db
```

## Ejecutar Tests

### Tests Unitarios
```bash
pytest tests/ -v
```

### Tests de Integración
```bash
pytest test_integration.py -v
```

### Con cobertura
```bash
pytest --cov=. test_integration.py
```

## Resolución de Problemas

### Error: CLAUDE_API_KEY no configurada
**Solución:** Agregar clave de API en archivo .env

### Error: Database is locked
**Solución:** Solo una instancia del servidor debe usar la BD a la vez

### Error: Port already in use
**Solución:** Cambiar puerto con `PORT=8001 python server.py`

### Error: ModuleNotFoundError
**Solución:** Verificar que esté en el directorio correcto y activar venv

## Despliegue en Producción

### Plataformas Soportadas

#### Heroku
```bash
heroku create mi-orquestadora
git push heroku main
heroku config:set CLAUDE_API_KEY=sk-ant-...
heroku logs --tail
```

#### Railway
```bash
railway link
railway add
railway up
```

#### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t orquestadora .
docker run -e CLAUDE_API_KEY=sk-ant-... -p 8000:8000 orquestadora
```

### Variables de Producción Recomendadas
```env
CLAUDE_API_KEY=sk-ant-...
PORT=8000
DEBUG=False
DB_PATH=/var/lib/orquestadora/conversations.db
```

### Monitoreo

#### Health Check cada 30s
```bash
watch -n 30 'curl -s http://localhost:8000/health | jq .status'
```

#### Logs
```bash
tail -f logs/orquestadora.log
```

## Actualización a Nueva Versión

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python server.py
```

## Soporte

Para reportar problemas o sugerencias:
- GitHub Issues: https://github.com/CarlosVergaraChile/maquina-orquestadora-gl-strategic/issues
- Email: soporte@orquestadora.ai

---

**Versión:** 2.3.0  
**Última actualización:** Enero 2024  
**Estado:** Production Ready ✅
