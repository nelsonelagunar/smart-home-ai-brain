# Smart Home AI Brain

<div align="center">

![Smart Home AI Brain](docs/images/logo.png)

**Sistema inteligente de automatización del hogar con IA**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-purple.svg)](https://ollama.ai)

[Demo](#demo) • [Instalación](#instalación) • [Uso](#uso) • [Arquitectura](#arquitectura) • [Contribuir](#contribuir)

</div>

---

## 🎯 Características

### Control Inteligente
- 🏠 **Control unificado** de todos los dispositivos del hogar
- 📱 **App web** responsiva para control desde cualquier dispositivo
- 🗣️ **Control por voz** integrado con Alexa/Google Assistant

### Machine Learning
- 📊 **Aprendizaje de patrones** - Detecta rutinas automáticamente
- 🔮 **Predicción de necesidades** - Prende el A/C antes de que llegues
- 🚨 **Detección de anomalías** - Alerta sobre dispositivos desconocidos

### Inteligencia Artificial
- 🤖 **LLM Local** - Ollama para procesamiento de lenguaje natural
- 🧠 **Memoria persistente** - Recuerda preferencias y contextos
- 💬 **Chat natural** - "Encender las luces de la sala" → Acción

### Seguridad y Privacidad
- 🔒 **100% Local** - Tus datos nunca salen de tu red
- 🔐 **Autenticación** - Control de acceso seguro
- 📝 **Logs completos** - Auditoría de todas las acciones

---

## 🛠️ Hardware Soportado

| Dispositivo | Estado | Protocolo |
|---|---|---|
| BroadLink RM4PRO/RM4MINI | ✅ Soportado | IR/RF/WiFi |
| Alexa Echo | ✅ Soportado | Alexa API |
| Google Chromecast | 🔄 En progreso | Google Cast |
| Midea A/C | 🔄 En progreso | WiFi |
| Tuya Devices | 📋 Planificado | Tuya Cloud API |

---

## 📸 Demo

> 🎥 Video demo próximamente

---

## 🚀 Instalación

### Requisitos

- Python 3.11+
- Ollama (para LLM local)
- Dispositivos BroadLink en la red

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/nelsonelagunar/smart-home-ai-brain.git
cd smart-home-ai-brain

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar dispositivos
cp config/devices.example.yaml config/devices.yaml
# Editar config/devices.yaml con tus dispositivos

# Iniciar servidor
python -m smart_home_brain.main
```

### Con Docker

```bash
docker-compose up -d
```

---

## 🎮 Uso

### API REST

```bash
# Listar dispositivos
curl http://localhost:8000/api/devices

# Enviar comando IR
curl -X POST http://localhost:8000/api/devices/rm4pro-sala/send \
  -H "Content-Type: application/json" \
  -d '{"command": "tv_power"}'

# Chat con IA
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Encender el aire de la sala"}'
```

### Dashboard Web

Abre `http://localhost:8000` en tu navegador.

### Comandos de Voz (Alexa)

```
"Alexa, dile a Smart Brain que encienda las luces"
"Alexa, pregunta a Smart Brain la temperatura de la sala"
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      Smart Home AI Brain                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ Web UI  │  │  API    │  │ Chat    │  │ Alexa   │         │
│  │ React   │  │ FastAPI │  │ LLM     │  │ Skill   │         │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘         │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────┐            │
│  │              Core Engine                       │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │            │
│  │  │ Devices  │ │ Patterns │ │ Anomaly  │      │            │
│  │  │ Manager  │ │ Learner  │ │ Detector │      │            │
│  │  └──────────┘ └──────────┘ └──────────┘      │            │
│  └──────────────────────────────────────────────┘            │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────┐            │
│  │              Integrations                      │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │            │
│  │  │BroadLink │ │  Alexa   │ │  Tuya    │      │            │
│  │  │  IR/RF   │ │   API    │ │   API    │      │            │
│  │  └──────────┘ └──────────┘ └──────────┘      │            │
│  └──────────────────────────────────────────────┘            │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────┐            │
│  │              Storage                           │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │            │
│  │  │ SQLite   │ │ Vector   │ │  Redis   │      │            │
│  │  │  (Data)  │ │(Memory)  │ │ (Cache)  │      │            │
│  │  └──────────┘ └──────────┘ └──────────┘      │            │
│  └──────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                          │
                    ┌─────┴─────┐
                    │   Ollama   │
                    │  (Local)   │
                    └───────────┘
```

---

## 🧠 Componentes

### Core Engine
- **Device Manager**: Descubrimiento y control de dispositivos
- **Pattern Learner**: Detecta rutinas automáticamente (ML)
- **Anomaly Detector**: Identifica comportamientos inusuales

### Integrations
- **BroadLink**: Control IR/RF de TV, A/C, luces
- **Alexa**: Integración con Echo devices
- **Tuya**: Dispositivos WiFi inteligentes

### AI/ML
- **Chat LLM**: Procesamiento de lenguaje natural (Ollama)
- **Pattern ML**: Aprendizaje de rutinas (scikit-learn)
- **Vector Memory**: Memoria conversacional (SQLite-vec)

---

## 📁 Estructura del Proyecto

```
smart-home-ai-brain/
├── src/
│   ├── core/
│   │   ├── device_manager.py
│   │   ├── pattern_learner.py
│   │   └── anomaly_detector.py
│   ├── integrations/
│   │   ├── broadlink/
│   │   ├── alexa/
│   │   └── tuya/
│   ├── ai/
│   │   ├── llm_client.py
│   │   ├── embeddings.py
│   │   └── memory.py
│   ├── api/
│   │   ├── routes/
│   │   └── models/
│   └── web/
│       └── static/
├── config/
│   ├── devices.yaml
│   └── settings.yaml
├── tests/
├── docs/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Coverage
pytest --cov=src tests/

# Tests específicos
pytest tests/test_broadlink.py -v
```

---

## 📊 Roadmap

### v1.0 - MVP (Actual)
- [x] Descubrimiento de dispositivos BroadLink
- [x] Control básico IR/RF
- [x] API REST
- [ ] Dashboard web
- [ ] Chat con LLM

### v1.1 - Learning
- [ ] Detección de patrones
- [ ] Automatizaciones sugeridas
- [ ] Scheduler

### v1.2 - Integrations
- [ ] Alexa Skill
- [ ] Google Assistant
- [ ] Home Assistant bridge

### v2.0 - Intelligence
- [ ] Predicción de necesidades
- [ ] Detección de anomalías
- [ ] Multi-usuario

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

### Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Formatear código
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
```

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Nelson Laguna**
- LinkedIn: [linkedin.com/in/nelsonelagunar](https://linkedin.com/in/nelsonelagunar)
- GitHub: [github.com/nelsonelagunar](https://github.com/nelsonelagunar)
- Blog: [nelsonlaguna.dev](https://nelsonlaguna.dev)

---

## 🙏 Agradecimientos

- [BroadLink](https://github.com/mjg59/python-broadlink) - Librería Python para dispositivos BroadLink
- [Ollama](https://ollama.ai) - LLM local para IA
- [FastAPI](https://fastapi.tiangolo.com) - Framework web moderno

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella! ⭐**

</div>