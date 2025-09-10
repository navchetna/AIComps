import logging
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import uvicorn

from openai import OpenAI
from groq import Groq


# ----------------------------
# Configuration
# ----------------------------

class Settings(BaseSettings):
    # OpenAI settings if hosted model is available
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    model_name: str = "gpt-4o-mini"

    # Groq if hosted model is not available
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"


    class Config:
        env_file = ".env"


settings = Settings()


# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ----------------------------
# Request/Response Models
# ----------------------------

class SummarizeRequest(BaseModel):
    text: str
    prompt: Optional[str] = None
    word_limit: Optional[int] = None


class SummarizeResponse(BaseModel):
    summary: str
    model: str
    backend: str


# ----------------------------
# Utilities
# ----------------------------

def call_openai_chat_completion(messages: List[Dict[str, str]], model: str) -> str:
    """Call OpenAI-compatible API"""
    if not settings.openai_api_key or not settings.openai_api_base:
        raise ValueError("OpenAI API credentials/base not configured")

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_api_base)

    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content.strip()


def call_groq_chat_completion(messages: List[Dict[str, str]], model: str) -> str:
    """Call Groq API as fallback."""
    if not settings.groq_api_key:
        raise ValueError("Groq API key not configured")

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content.strip()


# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI(
    title="Summarization Service",
    description="A FastAPI service for summarizing text using an LLM",
    version="1.3.0",
)


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    try:
        prompt = req.prompt or (
            "You are a professional summarizer. Summarize the given text "
            "by extracting key insights, ensuring important details are retained. "
            "The summary should be clear, concise, and engaging. Do not omit critical points."
        )
        word_limit = req.word_limit or 150

        messages = [
            {
                "role": "system",
                "content": (
                    f"{prompt}\n\n"
                    f"Ensure the summary is no longer than {word_limit} words."
                ),
            },
            {"role": "user", "content": req.text},
        ]

        if settings.openai_api_base and settings.openai_api_key:
            backend = "vLLM"
            summary = call_openai_chat_completion(messages, settings.model_name)
            model_used = settings.model_name
        else:
            backend = "groq"
            summary = call_groq_chat_completion(messages, settings.groq_model)
            model_used = settings.groq_model

        return SummarizeResponse(summary=summary, model=model_used, backend=backend)

    except Exception as e:
        logger.exception("Summarization failed")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)