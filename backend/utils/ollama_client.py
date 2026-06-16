import httpx
import json
from typing import List, Dict, Optional
from utils.logger import logger
from config.settings import OLLAMA_CHAT_URL, OLLAMA_BASE_URL


async def check_ollama_running() -> bool:

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                logger.info(f"✅ Ollama is running. Available models: {model_names}")
                return True
    except Exception as e:
        logger.error(f"❌ Cannot reach Ollama at {OLLAMA_BASE_URL}: {e}")
        logger.error("   → Make sure Ollama is installed and running: `ollama serve`")
        logger.error("   → Pull a model if needed: `ollama pull llama3`")
    return False


async def call_ollama_chat(
    model: str,
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    full_messages = []
    if system_prompt:
        full_messages.append({
            "role": "system",
            "content": system_prompt
        })
    full_messages.extend(messages)

    payload = {
        "model": model,
        "messages": full_messages,
        "stream": False,            
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }

    logger.debug(f"📤 Calling Ollama [{model}] with {len(full_messages)} messages")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_CHAT_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned status {response.status_code}: {response.text}"
                )

            data = response.json()
            content = data.get("message", {}).get("content", "")

            if not content:
                raise RuntimeError("Ollama returned empty content")

            logger.debug(f"📥 Ollama response: {content[:100]}...")
            return content.strip()

    except httpx.TimeoutException:
        raise RuntimeError(
            "Ollama request timed out (>120s). "
            "Try a smaller model or check system resources."
        )
    except httpx.ConnectError:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Run `ollama serve` and ensure it's on port 11434."
        )


async def get_available_models() -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except Exception:
        return []