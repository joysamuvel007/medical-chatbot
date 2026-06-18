# 🏥 Healthcare Chatbot — Local AI Pipeline

An agentic healthcare chatbot powered entirely by **open-source LLMs via Ollama**.
No OpenAI. No paid APIs. Runs 100% locally.

## Architecture
```
USER → Session Manager → Input Preprocessor → Ollama Classifier
     → Decision Engine → Context Builder → Ollama Response LLM
     → Safety Check → Memory → USER
```

## Tech Stack
| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.11+, FastAPI             |
| LLM Engine | Ollama (llama3 / mistral)         |
| Web Search | DuckDuckGo (free, no API key)     |
| Memory     | JSON file-based session store     |
| Frontend   | React + Vite + TailwindCSS        |

## Phases
- Phase 1: Project Setup (this file)
- Phase 2: Session & Memory Manager
- Phase 3: Input Preprocessor
- Phase 4: Ollama Classification Node
- Phase 5: Decision Engine
- Phase 6: Response LLM + Safety Check
- Phase 7: Frontend UI

## Quick Start

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```