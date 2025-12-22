import os
import psutil
from loguru import logger

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import SpeechRequest

from model_runner import TextToSpeech, numpy_to_wav_bytes


app = FastAPI(root_path="/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


tts = TextToSpeech(
    language=os.getenv("DEFAULT_LANGUAGE", "hindi"),
    batch_size=int(os.getenv("TTS_BATCH_SIZE", "1")),
    gender=os.getenv("GENDER", "male"),
)


@app.get("/health")
async def get_health():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage < 90:
            return {"status": "healthy", "cpu_usage": cpu_usage}
        else:
            return {"status": "unhealthy", "cpu_usage": cpu_usage}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
    

@app.post("/audio/speech")
async def transcribe_audio(request: SpeechRequest):
    logger.info("Request received")
    try:
        language = request.instructions
        audio, response_time = tts.generate_audio(
            text=request.input,
            gender=request.voice,
        )
        audio_bytes = numpy_to_wav_bytes(audio)
        logger.info("Request processed")
        return StreamingResponse(
            audio_bytes, media_type="audio/mpeg"
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Error processing request")
    

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)