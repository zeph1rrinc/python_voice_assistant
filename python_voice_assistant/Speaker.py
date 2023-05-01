import time

import sounddevice as sd
import torch
from loguru import logger

from .settings import settings


class Speaker:
    """Class for generating speech by text"""

    def __init__(self) -> None:
        self.model, _ = torch.hub.load(
            repo_or_dir=settings.repo_or_dir,
            model=settings.model,
            language=settings.language,
            speaker=settings.model_id,
        )
        self.model.to(torch.device(settings.device_type))
        logger.debug("Speaker initialized")

    def say(self, text: str):
        """
        Мethod for generating and playing sound

        :param text: message for converting and playing
        :type text: str
        """
        audio = self.model.apply_tts(
            text=text,
            speaker=settings.speaker,
            sample_rate=settings.sample_rate,
            put_accent=settings.put_accent,
            put_yo=settings.put_yo,
        )
        sd.play(audio, settings.sample_rate)
        time.sleep(len(audio) / settings.sample_rate)
        sd.stop()
