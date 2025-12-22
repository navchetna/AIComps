from pydantic import BaseModel
from enum import Enum


class Languages(str, Enum):
    HINDI = "hi"


class TranslateRequest(BaseModel):
    src_lang: str
    tgt_lang: str
    text: str


class TranslationResponse(BaseModel):
    translation: str
    time_taken: float