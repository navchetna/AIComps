import re
import logging
from typing import Optional, List, Dict
import json

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
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    model_name: str = "gpt-4o-mini"

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

class TaggingRequest(BaseModel):
    text: str
    prompt: Optional[str] = None
    num_tags: Optional[int] = 5  

class TaggingResponse(BaseModel):
    tags: List[str]
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
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content.strip()


def call_groq_chat_completion(messages: List[Dict[str, str]], model: str) -> str:
    """Call Groq API as fallback."""
    if not settings.groq_api_key:
        raise ValueError("Groq API key not configured")

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content.strip()

# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI(
    title="Tagging Service",
    description="A FastAPI service that generates the most relevant tags from text using an LLM",
    version="1.3.0",
)

@app.post("/tags", response_model=TaggingResponse)
async def generate_tags(req: TaggingRequest):
    try:
        num_tags = req.num_tags or 5
        SYSTEM_PROMPT = """
            You are an expert content analyzer.

            Your task:
            - Fully understand the context of the provided text.
            - Generate exactly N relevant tags that describe the content accurately.

            RULES:
            1. Each tag must be concise and relevant.
            2. All tags must be lowercase.
            3. Multi-word tags must use hyphens (e.g., "artificial-intelligence").

            RESPONSE FORMAT:
            - Your entire output MUST be a single, valid JSON object.
            - The JSON object must have a single key "tags".
            - The value of "tags" MUST be a JSON array containing only STRINGS.
            - DO NOT create an array of objects (e.g., [{"name": "tag"}]).

            Example of the required format:
            {
            "tags": [
                "artificial-intelligence",
                "5g-connectivity",
                "llm-inference"
            ]
            }
            """

        DEFAULT_TAGGING_PROMPT = """
        Generate tags that reflect the **main themes and context** of the text.
        """

        user_tagging_prompt = req.prompt or DEFAULT_TAGGING_PROMPT

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{user_tagging_prompt}\n\nText: {req.text}\nGenerate exactly {num_tags} tags."}
        ]

        if settings.openai_api_base and settings.openai_api_key:
            backend = "vLLM"
            result_json = call_openai_chat_completion(messages, settings.model_name)
            print("OpenAI response:", result_json)
            model_used = settings.model_name
        else:
            backend = "groq"
            result_json = call_groq_chat_completion(messages, settings.groq_model)
            model_used = settings.groq_model


        try:
            tags = json.loads(result_json)["tags"]
            formatted_tags = [t.strip().lower().replace(" ", "-") for t in tags if isinstance(t, str)]
            if not isinstance(tags, list):
                raise ValueError("JSON 'tags' key is not a list")
            formatted_tags = [t.strip().lower().replace(" ", "-") for t in tags if isinstance(t, str)]
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from model: {str(e)}")

        if not formatted_tags:
            formatted_tags = []

        return TaggingResponse(tags=formatted_tags[:num_tags], model=model_used, backend=backend)

    except Exception as e:
        logger.exception("Tagging failed")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
