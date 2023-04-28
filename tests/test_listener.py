from os import remove
from os.path import exists

import pytest


@pytest.mark.parametrize(
    "data", [{"speaker": "john", "spk": [123]}, {"speaker": "albert", "spk": [321]}]
)
def test_add_speaker(data, listener):
    listener.add_speaker(data)
    assert data["spk"] == listener.speakers[data["speaker"]]
    remove("speakers.json")


def test_dump_speakers(listener):
    listener.add_speaker({"speaker": "albert", "spk": [432]})
    listener.dump_speakers()
    assert exists("speakers.json")


def test_get_speakers(listener):
    listener.get_speakers()
    assert listener.speakers["albert"] == [432]


def test_identify_speaker(listener):
    result = listener.identify_speaker([432])
    assert result[0] == "albert"
