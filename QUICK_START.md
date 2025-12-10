# Máquina Orquestadora de IA GL Strategic - QUICK START

## Descripción
App de IA conversacional para móvil con soporte de voz y lenguaje natural.
Diseñada para producción con Docker.

## Requisitos
- Docker & Docker Compose
- O: Python 3.11+ (sin Docker)

## Iniciar en Producción (Docker)

### Opción 1: Docker Compose (Recomendado)
```bash
cd /path/to/maquina-orquestadora
docker-compose up -d
```

**Acceso:**
- Web: http://localhost (Puerto 80)
- API: http://localhost:8000
- Health: http://localhost:8000/health

### Opción 2: Docker Manual
```bash
# Build
docker build -t orquesta-api .

# Run
docker run -d -p 8000:8000 --name orquesta-api orquesta-api
```

## Iniciar Localmente (Sin Docker)
```bash
# 1. Instalar deps
pip install -r requirements.txt

# 2. Ejecutar backend
python app/backend/server.py

# 3. Servir frontend (en otra terminal)
python -m http.server 8080 -d app/frontend/
```

**Acceso:** http://localhost:8080

## Estructura
```
.
├── app/
│   ├── frontend/
│   │   └── index.html (Mobile-first UI con voz)
│   └── backend/
│       └── server.py (FastAPI)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Features
- ✍️ **Voice Input**: Habla en lugar de escribir (Web Speech API)
- 🔊 **Voice Output**: La orquesta responde con voz (TTS)
- 💱 **Mobile-First**: Diseño responsive para móvil
- 🌟 **Natural Language**: Entiende lenguaje natural
- ⚙️ **REST API**: Endpoint POST /ask para integraciones
- 🚀 **Production Ready**: Docker, CORS habilitado, Health checks

## API Endpoints

### GET /health
Verifica estado del servidor
```bash
curl http://localhost:8000/health
```

### POST /ask
Envía pregunta a la orquesta
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, cómo estás?", "context": []}'
```

**Respuesta:**
```json
{
  "response": "He entendido tu pregunta...",
  "emotion": "thoughtful",
  "timestamp": "2024-..."
}
```

## Variables de Entorno
```
PORT=8000              # Puerto API
ENVIRONMENT=production # production|development
```

## Logs

### Docker
```bash
docker-compose logs -f api
```

### Local
```
Consola con output de uvicorn
```

## Troubleshooting

**"Connection refused en localhost:8000"**
- Docker: `docker-compose ps` para verificar que corren
- Local: Asegúrate que `python app/backend/server.py` está corriendo

**"CORS error en navegador"**
- Está solucionado en server.py (allow_origins=["*"])
- En producción, cambiar a dominios específicos

**"Voz no funciona"**
- Requiere HTTPS o localhost
- Navegadores modernos: Chrome, Firefox, Safari

## Próximos Pasos
1. Integrar APIs reales (OpenAI, Claude, etc.)
2. Agregar base de datos para historial
3. Implementar autenticación
4. Mejorar generación de respuestas
5. Agregar más idiomas

## Soporte
Para issues o preguntas: Ver issues en GitHub
