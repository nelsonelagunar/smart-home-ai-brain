# Contributing to Smart Home AI Brain

¡Gracias por tu interés en contribuir! 🎉

## 🚧 Estado del Proyecto

Este proyecto está en **desarrollo activo**. Actualmente estamos trabajando en:

- [ ] MVP funcional con descubrimiento de dispositivos
- [ ] Integración completa con BroadLink
- [ ] Dashboard web
- [ ] Documentación

## 🤝 Cómo Contribuir

### Reportar Bugs

1. Busca en [Issues](https://github.com/nelsonelagunar/smart-home-ai-brain/issues) si ya existe
2. Si no existe, crea uno nuevo con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs/screenshots si es posible

### Sugerir Features

1. Abre un [Issue](https://github.com/nelsonelagunar/smart-home-ai-brain/issues/new)
2. Usa el template "Feature Request"
3. Describe:
   - El problema que resuelve
   - Solución propuesta
   - Alternativas consideradas

### Enviar Código

1. **Fork** del repositorio
2. **Clonar** tu fork:
   ```bash
   git clone https://github.com/tu-usuario/smart-home-ai-brain.git
   cd smart-home-ai-brain
   ```
3. **Crear rama** para tu cambio:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```
4. **Desarrollar**:
   ```bash
   # Crear entorno virtual
   python -m venv venv
   source venv/bin/activate
   
   # Instalar dependencias de desarrollo
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Instalar pre-commit hooks
   pre-commit install
   ```
5. **Tests**:
   ```bash
   pytest tests/ -v
   ```
6. **Commit**:
   ```bash
   git add .
   git commit -m "feat: descripción de tu cambio"
   ```
7. **Push**:
   ```bash
   git push origin feature/mi-nueva-feature
   ```
8. **Pull Request**:
   - Abre PR desde tu fork
   - Describe los cambios
   - Referencia issues relacionados

## 📝 Convenciones

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato, punto y coma, etc
refactor: refactorización
test: tests
chore: mantenimiento
```

### Código

- **Python**: Seguir PEP 8
- **Imports**: Ordenar con isort
- **Formato**: Black con línea 88 caracteres
- **Typing**: Type hints donde sea posible

### Estructura de Archivos

```
src/smart_home_brain/
├── core/          # Lógica principal
├── ai/            # Integración con LLM
├── api/           # Endpoints REST
├── integrations/  # Integraciones externas
└── utils/         # Utilidades
```

## 🏃 Desarrollo Local

### Requisitos

- Python 3.11+
- Ollama (para LLM local)
- Dispositivo BroadLink (opcional, para pruebas)

### Setup

```bash
# Crear entorno
python -m venv venv
source venv/bin/activate

# Instalar
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ejecutar
python -m smart_home_brain.main

# Tests
pytest tests/ -v --cov=src
```

### Sin Dispositivos

El proyecto incluye un modo de simulación para desarrollo:

```bash
# Usar datos simulados
export SIMULATION_MODE=true
python -m smart_home_brain.main
```

## 📋 Checklist para PRs

- [ ] Código sigue las convenciones
- [ ] Tests pasan
- [ ] Nueva funcionalidad tiene tests
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado (si aplica)

## ❓ Preguntas

¿Dudas? Abre un [Discussion](https://github.com/nelsonelagunar/smart-home-ai-brain/discussions) o contacta:

- **GitHub**: [@nelsonelagunar](https://github.com/nelsonelagunar)
- **LinkedIn**: [Nelson Laguna](https://linkedin.com/in/nelsonelagunar)

## 📜 Código de Conducta

Ver [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

¡Gracias por contribuir! 🙌