import pytest

from python_voice_assistant import Helper
from python_voice_assistant.Listener import Listener
from python_voice_assistant.Speaker import Speaker


@pytest.fixture()
def helper():
    return Helper()


@pytest.fixture()
def listener():
    return Listener(test_mode=True)


@pytest.fixture()
def speaker():
    return Speaker()
