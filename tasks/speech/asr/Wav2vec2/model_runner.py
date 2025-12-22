import os
import io
import time
import torch
import fairseq 
import librosa
import numpy as np
import soundfile as sf

from loguru import logger
import torch.nn.functional as F
import torchaudio.sox_effects as ta_sox

from utilities import download_model


torch.serialization.add_safe_globals([fairseq.data.dictionary.Dictionary])


class AudioToText:
    def __init__(
        self,
        model_path: str = "models",
        language: str = "hindi",
        warmup_iterations: int = 3,
        batch_size: int = 1,
        dtype="bfloat16",
        sample_rate: int = 16000,
        max_audio_length: int = 30, 
    ):
        self.sample_rate = sample_rate
        self.max_audio_length = max_audio_length        # In seconds

        self.model_path = os.path.join(model_path, f"{language.lower()}.pt")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"ASR model not found at {self.model_path}. Please download the model first")

        self.model, self.cfg, self.task = fairseq.checkpoint_utils.load_model_ensemble_and_task([self.model_path])
        self.model = self.model[0]
        self.dtype = torch.float32 if dtype == "float32" else torch.bfloat16
        self.model.to(self.dtype).eval()

        self.effects = [["gain", "-n"]]

        self.token = self.task.target_dictionary
        self.warmup(batch_size, warmup_iterations)

    def warmup(self, batch_size: int, iterations: int):
        dummy_audio = torch.randn(batch_size, self.sample_rate * self.max_audio_length).to(self.dtype)
        logger.info("Warming up the model...")
        for _ in range(iterations):
            _ = self.generate_logits(dummy_audio)


    def transcribe(self, audio: bytes) -> str:
        st = time.perf_counter()
        audio_processed = self._preprocess_audio(audio)

        predicted_ids = self.generate_logits(audio_processed)
        
        transcription = self._post_processes(predicted_ids)
        duration = time.perf_counter() - st 

        if len(transcription) == 1:
            transcription = transcription[0]

        return transcription, duration
    

    def generate_logits(self, audio_processed: torch.Tensor) -> list:
        audio_processed = audio_processed.to(self.dtype)
        
        with torch.no_grad():
            audio_processed = F.layer_norm(audio_processed, audio_processed.shape)

        logits = self.model(source=audio_processed, padding_mask=None)['encoder_out']
        predicted_ids = torch.argmax(logits, axis=-1)
        predicted_ids = torch.unique_consecutive(
            predicted_ids.T, dim=1).tolist()
        return predicted_ids


    def _preprocess_audio(self, audio_bytes: bytes):
        audio_bytes = io.BytesIO(audio_bytes)
        audio_array, sr = sf.read(audio_bytes, dtype="float32")

        # Resample if the sample rate don't match
        if sr != self.sample_rate:
            audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=self.sample_rate)

        padded_audio = self._pad_audio(audio_array)

        audio_processed, rate = ta_sox.apply_effects_tensor(
            torch.tensor(padded_audio), self.sample_rate, self.effects
        )
        audio_processed = audio_processed.float()
        return audio_processed

    def _pad_audio(self, audio: np.array):
        pad_buffer = np.array(
            [0] * (self.max_audio_length * self.sample_rate - len(audio)), dtype=np.float32
        )
        audio = np.append(audio, pad_buffer)
        audio = np.expand_dims(audio, axis=0)
        return audio
    
    def _post_processes(self, predicted_ids: list) -> str:
        transcriptions = []
        for ids in predicted_ids:
            transcription = self.token.string(ids)
            transcription = transcription.replace(
                " ", "").replace('|', " ").strip()
            transcriptions.append(transcription)
        return transcriptions