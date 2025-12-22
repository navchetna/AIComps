from pydantic import BaseModel
from typing import Literal
from enum import Enum 


class Languages(str, Enum):
    HINDI = "hindi"
    ENGLISH = "english"
    MALAYALAM = "malayalam"
    TAMIL = "tamil"
    TELUGU = "telugu"
    KANNADA = "kannada"
    BENGALI = "bengali"
    MARATHI = "marathi"
    GUJARATI = "gujarati"
    PUNJABI = "punjabi"
    ODIA = "odia"
    MANIPURI = "manipuri"
    BODO = "bodo"
    ASSAMESE = "assamese"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class SpeechRequest(BaseModel):
    model: str
    input: str 
    voice: Gender = Gender.MALE
    instructions: Languages = Languages.HINDI 
    response_format: str = None
    speed: float = 1.0 
    stream_format: Literal["sse", "audio"] = "sse"