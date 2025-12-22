import os
import psutil
from loguru import logger
from models import TranscriptionResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, Form, UploadFile, FastAPI, HTTPException

from model_runner import AudioToText
from utilities import download_model

app = FastAPI(root_path="/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    global asr
    asr = None

    logger.info("Starting up and downloading model if not present...")
    download_model(
        language=os.getenv("ASR_LANGUAGE", "hindi"),
        model_dir=os.getenv("ASR_MODEL_PATH", "models")
    )

    logger.info("Loading ASR model...")
    asr = AudioToText(
        model_path=os.getenv("ASR_MODEL_PATH", "models"),
        language=os.getenv("ASR_LANGUAGE", "hindi"),
        batch_size=int(os.getenv("ASR_BATCH_SIZE", "1")),
    )


@app.get("/health")
async def get_cpu_health():
    # Use the core utilization if its less than 90% 
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage < 90:
            return {"status": "healthy", "cpu_usage": cpu_usage}
        else:
            return {"status": "unhealthy", "cpu_usage": cpu_usage}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
    

@app.post("/audio/transcriptions", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Source audio file"),
    model: str = Form(..., description="Model name"),
    response_format: str = Form("text", description="Format response")
):
    if asr is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    logger.info("Request received")
    audio_bytes = await file.read()
    transcription, response_time = asr.transcribe(audio_bytes)
    logger.info("Request processed")
    return TranscriptionResponse(text=transcription, latency=response_time)