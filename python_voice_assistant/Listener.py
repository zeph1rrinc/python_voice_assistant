import json
import math
import queue
from typing import Callable
from typing import List

import numpy as np
import sounddevice as sd
import vosk
from loguru import logger

from .settings import settings


def cosine_dist(x: list, y: list) -> float:
    """
    Counting cosine_dist between two vectors

    :param x: first vector
    :type x: List[float]

    :param y: second vector
    :type y: List[float]
    """
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)


class Listener:
    """Class for speech recognition and speaker recognition"""

    def __init__(self, test_mode=False) -> None:
        """
        :param test_mode: if True, not initialize recognizing models
        :type test_mode: bool
        """
        self.sample_rate = 16000
        self.device = 1
        self.queue = queue.Queue()
        self.speakers = {}

        if not test_mode:
            self.__init_recognizer()
        self.get_speakers()
        logger.debug("Listener initialized")

    def __init_recognizer(self):
        """Initialize recognizing models"""
        model = vosk.Model(settings.recognizing_model_path)
        spk_model = vosk.SpkModel(settings.speaker_model_path)
        recognizer = vosk.KaldiRecognizer(model, self.sample_rate)
        recognizer.SetSpkModel(spk_model)
        self.recognizer = recognizer

    def get_speakers(self):
        """Get speaker from speakers.json files"""
        try:
            with open("speakers.json", encoding="utf-8") as file:
                self.speakers = json.load(file)
        except FileNotFoundError:
            pass

    def dump_speakers(self):
        """Dump known speakers to speakers.json file"""
        with open("speakers.json", "w", encoding="utf-8") as file:
            json.dump(self.speakers, file, indent=4, ensure_ascii=False)

    def identify_speaker(self, spk: List[str], min_propability: int = 45):
        """
        Method for speaker identification by voice vector 'spk'

        :param spk: voice vector
        :type spk: List[str]

        :param min_propability: minimal propability for recognizing speaker
        :type min_propability: int
        """
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
        """
        Method for add speaker from json file format {'speaker': 'name', 'spk':['123', '1232', '3213']}

        :param speaker_model_path: path to json file
        :type speaker_model_path: str
        """
        with open(speaker_model_path, encoding="utf-8") as file:
            data = json.load(file)
        self.speakers[data["speaker"]] = data["spk"]
        self.dump_speakers()

    def add_speaker(self, data: dict):
        """
        Method for add speaker from data format {'speaker': 'name', 'spk':['123', '1232', '3213']}

        :param data: dictionary with data
        :type data: dict
        """
        self.speakers[data["speaker"]] = data["spk"]
        self.dump_speakers()

    def create_speaker(self, name: str, stop_word: str):
        """
        Method for create speaker by microphone with user input

        :param name: name of speaker
        :type name: str
        :param stop_word: word to stop recording
        :type stop_word: str
        """
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
                    logger.debug(result["text"])
                    if stop_word in result["text"]:
                        is_creating = False
                        self.speakers[name] = result["spk"]
                        self.dump_speakers()

    def queue_callback(self, indata, frames, time, status):
        """Callback for RawInputStream"""
        if status:
            logger.error(status)
        self.queue.put(bytes(indata))

    def listen(self, callback: Callable):
        """
        Mailoop of listening commands

        :param callback: function to parse commands
        :type callback: Callable
        """
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
                    self.recognizer.Reset()
                    callback(result)
