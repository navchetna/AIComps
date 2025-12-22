from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from core import IndicTranslator
from models import TranslateRequest, TranslationResponse


translator = IndicTranslator("ai4bharat/indictrans2-indic-indic-1B", batch_size=1)


app = FastAPI() 


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=['*'], 
)


@app.post("/translation/", response_model=TranslationResponse)
async def translation(request: TranslateRequest):    
    translation, time_taken = translator.single_translate(
        sentence=request.text,
        src_lang=request.src_lang,
        tgt_lang=request.tgt_lang
    )
    return {
        "translation": translation,
        "time_taken": time_taken
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)