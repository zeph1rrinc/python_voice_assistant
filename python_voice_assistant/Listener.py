import json
import math
import queue
from os.path import join
from typing import Callable

import numpy as np
import sounddevice as sd
import vosk
from loguru import logger

from .settings import settings


def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)


class Listener:
    def __init__(self) -> None:
        self.sample_rate = 16000
        self.device = 1
        self.queue = queue.Queue()
        self.speakers = {}

        self.__init_recognizer()
        self.__get_speakers()
        logger.debug("Listener initialized")

    def __init_recognizer(self):
        model = vosk.Model(settings.recognizing_model_path)
        spk_model = vosk.SpkModel(join(settings.models_path, "speaker_model"))
        recognizer = vosk.KaldiRecognizer(model, self.sample_rate)
        recognizer.SetSpkModel(spk_model)
        self.recognizer = recognizer

    def __get_speakers(self):
        try:
            with open("speakers.json", encoding="utf-8") as file:
                self.speakers = json.load(file)
        except FileNotFoundError:
            self.__dump_speakers()

    def __dump_speakers(self):
        with open("speakers.json", "w", encoding="utf-8") as file:
            json.dump(self.speakers, file, indent=4, ensure_ascii=False)

    def identify_speaker(self, spk: str, min_propability: int = 45):
        max_dist = 1
        result = None
        for speaker in self.speakers.keys():
            spk = list(map(float, spk))
            dist = cosine_dist(self.speakers[speaker], spk)
            if dist < 0:
                max_dist = 0
                result = speaker
                break
            speaker_probability = math.ceil((1 - dist) * 100)
            logger.debug(f"[VARIANT] {speaker} - {speaker_probability}%")
            if dist < max_dist:
                max_dist = dist
                result = speaker
        probability = math.ceil((1 - max_dist) * 100)
        if probability < min_propability:
            result = None
        return result, math.ceil(probability)

    def add_speaker_from_file(self, speaker_model_path: str):
        with open(speaker_model_path, encoding="utf-8") as file:
            data = json.load(file)
        self.speakers[data["speaker"]] = data["spk"]
        self.__dump_speakers()

    def create_speaker(self, name: str, stop_word: str):
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            device=self.device,
            dtype="int16",
            channels=1,
            callback=self.queue_callback,
        ):
            is_creating = True
            while is_creating:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if stop_word in result["text"]:
                        is_creating = False
                        self.speakers[name] = result["spk"]
                        self.__dump_speakers()

    def queue_callback(self, indata, frames, time, status):
        if status:
            logger.error(status)
        self.queue.put(bytes(indata))

    def listen(self, callback: Callable):
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            device=self.device,
            dtype="int16",
            channels=1,
            callback=self.queue_callback,
        ):
            while True:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if "spk" in result.keys():
                        print(self.identify_speaker(result["spk"]))
                    callback(result)
