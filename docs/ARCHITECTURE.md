# Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Smart Home AI Brain                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Presentation Layer                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   Web UI    │  │  REST API   │  │  WebSocket  │              │   │
│  │  │  (Streamlit)│  │  (FastAPI)  │  │   (Real-time)│              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         Core Layer                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │   Device     │  │   Pattern    │  │   Anomaly    │         │   │
│  │  │   Manager    │  │   Learner     │  │   Detector   │         │   │
│  │  │              │  │   (ML/ML)     │  │   (Stats)    │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Integration Layer                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │
│  │  │BroadLink │  │  Alexa   │  │  Tuya    │  │  MQTT    │      │   │
│  │  │  (IR/RF) │  │   API    │  │   API    │  │  Bridge  │      │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                          AI Layer                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │    LLM       │  │  Embeddings  │  │   Memory      │         │   │
│  │  │  (Ollama)    │  │ (nomic-embed)│  │ (SQLite-vec) │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         Storage Layer                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │   SQLite     │  │  RabbitMQ   │  │   File        │         │   │
│  │  │   (Data)     │  │   (Queue)   │  │   Storage     │         │   │
│  │  │   (Data)     │  │   (Cache)    │  │   Storage     │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────┐
                         │    Ollama       │
                         │  (Local LLM)    │
                         └─────────────────┘
```

---

## 📦 Components

### Presentation Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web UI | Streamlit/React | Dashboard visual |
| REST API | FastAPI | Endpoints para apps |
| WebSocket | FastAPI | Real-time updates |

### Core Layer

| Component | Description |
|-----------|-------------|
| Device Manager | Descubrimiento y control de dispositivos |
| Pattern Learner | ML para detectar rutinas |
| Anomaly Detector | Detección de comportamientos inusuales |

### Integration Layer

| Component | Protocol | Devices |
|-----------|----------|---------|
| BroadLink | UDP/WiFi | IR/RF controllers |
| Alexa API | HTTPS | Echo devices |
| Tuya API | HTTPS | Smart devices |
| MQTT | TCP/IP | IoT devices |
| RabbitMQ | AMQP | Event streaming |

### AI Layer

| Component | Model | Purpose |
|-----------|-------|---------|
| LLM | llama3.2 | Natural language processing |
| Embeddings | nomic-embed-text | Semantic search |
| Memory | SQLite-vec | Conversation history |

### Storage Layer

| Component | Purpose |
|-----------|---------|
| SQLite | Device state, patterns, events |
| RabbitMQ | Message queue, event streaming |
| File Storage | Learned codes, configs |

---

## 🔄 Data Flow

### Command Flow (User → Device)

```
User Input → LLM → Intent Extraction → Device Manager → Device
```

1. User sends command: "Encender el aire de la sala"
2. LLM extracts intent: `{device: "aire", action: "on", location: "sala"}`
3. Device Manager finds matching device
4. Device Manager sends IR/RF code
5. Device executes command

### Learning Flow (Device → Pattern)

```
Device Events → Event Logger → Pattern Learner → Pattern DB
```

1. Device state changes logged
2. Events aggregated by time
3. ML detects recurring patterns
4. Patterns saved for suggestions

### Query Flow (User ← State)

```
User Query → LLM → Context Builder → Response
```

1. User asks: "¿Qué temperatura hay?"
2. LLM identifies query type
3. Context Builder fetches current state
4. LLM generates natural response

---

## 🔐 Security Architecture

### Data Flow Security

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    API      │────▶│   Service   │
│  (Browser)  │ HTTPS│  (FastAPI) │ TLS │  (Local)    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Storage   │
                    │  (SQLite)   │
                    └─────────────┘
```

### Key Principles

1. **Local-only by default** - No cloud required
2. **TLS for all external connections** - HTTPS only
3. **No API keys in basic mode** - Just works
4. **Configurable authentication** - For multi-user setups

---

## 📈 Scalability

### Single Instance (Default)

```
┌─────────────────────────────┐
│      Single Host            │
│  ┌───────┐  ┌───────┐      │
│  │ API   │  │ Ollama│      │
│  └───────┘  └───────┘      │
│  ┌───────┐  ┌───────┐      │
│  │SQLite │  │RabbitMQ│      │
│  └───────┘  └───────┘      │
└─────────────────────────────┘
```

### Distributed (Advanced)

```
┌──────────────┐     ┌──────────────┐
│   API Node   │────▶│  Ollama Node │
│  (FastAPI)   │     │   (LLM)      │
└──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  (Cluster)   │
└──────────────┘
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `LLM_MODEL` | `llama3.2` | Model to use |
| `DATABASE_URL` | `sqlite:///data/smart_home.db` | Database URL |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost/` | RabbitMQ URL |
| `LOG_LEVEL` | `INFO` | Logging level |

### Config Files

```
config/
├── devices.yaml      # Device definitions
├── settings.yaml     # Application settings
└── secrets.yaml      # API keys (optional)
```

---

## 🧪 Testing Strategy

```
┌─────────────────────────────────────────────────────┐
│                    Testing Pyramid                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│                    ┌─────────┐                       │
│                    │   E2E   │                       │
│                   └─────────┘                        │
│               ┌───────────────┐                      │
│               │  Integration  │                      │
│              └───────────────┘                       │
│          ┌─────────────────────┐                     │
│          │     Unit Tests      │                     │
│         └─────────────────────┘                      │
│     ┌───────────────────────────┐                     │
│     │        Lint/Format        │                     │
│    └───────────────────────────┘                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📚 Related Documentation

- [API Reference](./API.md) - REST endpoints
- [Device Integration](./DEVICES.md) - Supported devices
- [Development Guide](./DEVELOPMENT.md) - Contributing
- [Deployment](./DEPLOYMENT.md) - Production setup