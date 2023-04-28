import json
import os
from typing import Callable

from loguru import logger

from .Listener import Listener
from .settings import settings
from .Speaker import Speaker


class Helper:
    def __init__(self):
        self.name = settings.name.lower()
        self.gender = settings.gender
        self.listener = Listener()
        self.speaker = Speaker()
        self.commands = {}
        self.__set_answers(settings.language)

    def __set_answers(self, language: str = "en"):
        try:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "languages",
                    f"{language}.json",
                ),
                encoding="utf-8",
            ) as file:
                self.answers = json.load(file)
        except FileNotFoundError:
            self.__set_answers()

    def bind(self, command: str, callback: Callable) -> bool:
        if command not in self.commands.keys():
            self.commands[command] = callback
            logger.debug(f"Command {command} successfully bound")
            return True
        raise ValueError(self.answers["already"])

    def command(self, command: str):
        def decorator(func):
            self.bind(command, func)
            return func

        return decorator

    def resolve_command(self, voice: str):
        logger.debug(voice["text"])
        if voice["text"].startswith(self.name):
            command = voice["text"].replace(self.name, "").strip()
            logger.debug(command)
            for cmd in self.commands.keys():
                if command.lower().startswith(cmd):
                    voice["text"] = command.replace(cmd, "").strip()
                    self.commands[cmd](voice)
                    return
            self.speaker.say(self.answers["uncought"])

    def listen(self):
        self.speaker.say(
            self.answers["ready"].format(
                **{"name": self.name, "gender": "a" if self.gender else ""}
            )
        )
        self.listener.listen(self.resolve_command)
