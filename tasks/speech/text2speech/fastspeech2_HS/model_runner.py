import io
import os
import sys
import json
import yaml
import torch
import time
import numpy as np
import soundfile as sf
from loguru import logger

from utilities import WARMUP_PARAGRAPHS, LANG_TEMPOS
from text_preprocess_for_inference import TTSDurAlignPreprocessor

sys.path.append(os.getenv("HIFIGAN_PATH", f"hifigan"))
from hifigan.env import AttrDict
from hifigan.models import Generator
from hifigan.meldataset import MAX_WAV_VALUE

from espnet2.bin.tts_inference import Text2Speech


import nltk
nltk.download("averaged_perceptron_tagger_eng")


def load_hifigan_vocoder(language: str, gender: str, device: torch.device):
    """
    Loads HiFi-GAN vocoder configuration file and generator model.
    """
    vocoder_config = f"vocoder/{gender}/{language}/config.json"
    vocoder_generator = f"vocoder/{gender}/{language}/generator"

    if not os.path.exists(vocoder_config) or not os.path.exists(vocoder_generator):
        raise FileNotFoundError(
            f"Vocoder files not found. Expected config: {vocoder_config}, generator: {vocoder_generator}"
        )

    with open(vocoder_config, "r") as f:
        data = f.read()

    json_config = json.loads(data)
    h = AttrDict(json_config)
    torch.manual_seed(h.seed)
    device = torch.device(device)
    generator = Generator(h).to(device)
    state_dict_g = torch.load(vocoder_generator, map_location=device)
    generator.load_state_dict(state_dict_g['generator'])
    generator.eval()
    generator.remove_weight_norm()
    return generator


def load_fastspeech2_model(language: str, gender: str, device: str):
    """
        Loads FastSpeech2 model and updates its configuration with absolute paths.
    """
    config_path = f"{language}/{gender}/model/config.yaml"
    tts_model_path = f"{language}/{gender}/model/model.pth"

    if not os.path.exists(config_path) or not os.path.exists(tts_model_path):
        raise FileNotFoundError(
            f"FastSpeech2 model files not found. Expected config: {config_path}, model: {tts_model_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    current_working_directory = os.getcwd()
    feat_rel_path = "model/feats_stats.npz"
    pitch_rel_path = "model/pitch_stats.npz"
    energy_rel_path = "model/energy_stats.npz"

    feat_path = os.path.join(current_working_directory,
                             language, gender, feat_rel_path)
    pitch_path = os.path.join(
        current_working_directory, language, gender, pitch_rel_path)
    energy_path = os.path.join(
        current_working_directory, language, gender, energy_rel_path)

    config["normalize_conf"]["stats_file"] = feat_path
    config["pitch_normalize_conf"]["stats_file"] = pitch_path
    config["energy_normalize_conf"]["stats_file"] = energy_path

    # Temporarily write the modified config to a new file or use a BytesIO object if preferred
    with open(config_path, "w") as file:
        yaml.dump(config, file)

    model = Text2Speech(train_config=config_path, model_file=tts_model_path, device=device, vocoder_config=None,vocoder_file=None)
    model.vocoder=None 
    return model



def split_into_chunks(text: str, words_per_chunk: int = 100):
    """Splits text into chunks of specified words_per_chunk."""
    words = text.split()
    chunks = [words[i:i + words_per_chunk]
              for i in range(0, len(words), words_per_chunk)]
    return [' '.join(chunk) for chunk in chunks]


def numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int = 48000) -> io.BytesIO:
    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return buf


class TextToSpeech:
    def __init__(
            self,
            language: str,
            batch_size: str = 1,
            gender: str = 'male',
            warmup_iters: int = 3,
            device: str = "cpu"
        ):
        self.alpha = LANG_TEMPOS.get(language.lower(), 1.0)
        self.lang = language
        self.gender = gender
        self.batch_size = batch_size
        self.warmup_iters = warmup_iters


        self.preprocessor = TTSDurAlignPreprocessor()

        self.vocoder_model = load_hifigan_vocoder(
            f"{language}_latest", gender, device)
        logger.debug(
            f"Loaded HiFi-GAN vocoder for {language}-{gender}")

        self.fastspeech2_model = load_fastspeech2_model(
            f"{language}_latest", gender, device)
        logger.debug(
            f"Loaded FastSpeech2 model for {language}-{gender}")
        
        self.warmup(warmup_iters)


    def warmup(self, warmup_iters: int):
        logger.info("TTS Warming up!")

        lang = self.lang.lower()
        text = WARMUP_PARAGRAPHS.get(lang)

        if not text:
            logger.warning(f"No warmup paragraph available for langauge: {lang}")
            return
        
        # Ensure warmup output directory exists
        logger.debug(f"Running warmup for language: {lang}")
        logger.debug(f"Warmup text length: {len(text.split())} words")

        try:
            for iter in range(warmup_iters):
                _, duration = self.generate_audio(
                    text=text,
                    gender=self.gender
                ) 
                logger.debug(f"Iteration {iter} for {self.gender} completed in {duration}")
        except Exception as e:
            logger.error(f"Warmup error failed for {lang}-{self.gender}: {e}")

 
    def generate_audio(self, text: str, gender: str):
        st = time.perf_counter()
        preprocessed_text, _ = self.preprocessor.preprocess(
            text, self.lang, gender
        )
        preprocessed_text = " ".join(preprocessed_text)

        with torch.no_grad():
            # Generate mel-spectograms 
            out = self.fastspeech2_model(preprocessed_text, decode_conf={"alpha": self.alpha})
            x = out["feat_gen_denorm"].T.unsqueeze(0) * 2.3262

            # Convert mel-spectograms to raw audio waveforms 
            y_g_hat = self.vocoder_model(x)
            audio = y_g_hat.squeeze()
            audio = audio * MAX_WAV_VALUE
            audio = audio.numpy().astype('int16')
        latency = time.perf_counter() - st
        return audio, latency