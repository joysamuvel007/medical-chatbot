import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils.models import ChatRequest, ChatResponse
from utils.logger import logger
from utils.ollama_client import check_ollama_running, get_available_models
from memory.session_manager import session_manager
from pipeline import run_pipeline
from config.settings import APP_TITLE, APP_VERSION, ALLOWED_ORIGINS

os.makedirs("logs", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {APP_TITLE} v{APP_VERSION}")
    logger.info("Checking Ollama connection...")

    ollama_ok = await check_ollama_running()
    if not ollama_ok:
        logger.warning(
            "⚠️  Ollama is not running! "
            "Start it with: ollama serve\n"
            "Pull a model with: ollama pull llama3\n"
            "The server will start but /chat will fail until Ollama is running."
        )
    else:
        models = await get_available_models()
        logger.info(f"✅ Ready. Models available: {models}")

    yield 

    logger.info("👋 Shutting down...")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Healthcare chatbot powered by local Ollama LLMs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": f"{APP_TITLE} is running",
        "version": APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    ollama_ok = await check_ollama_running()
    models = await get_available_models() if ollama_ok else []

    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama_running": ollama_ok,
        "available_models": models,
        "app_version": APP_VERSION,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.user_message.strip():
        raise HTTPException(status_code=400, detail="user_message cannot be empty")

    try:
        response = await run_pipeline(request)
        return response
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}. Check that Ollama is running."
        )


@app.get("/session/{session_id}/history")
async def get_history(session_id: str):
    
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found or expired")

    history = session_manager.get_history(session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": [m.model_dump() for m in history]
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    
    deleted = session_manager.clear_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"message": f"Session {session_id} cleared"}