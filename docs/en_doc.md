# python_voice_assistant

## Relations

- python = "^3.10"
- vosk = "^0.3.45" - library for speech recognition
- loguru = "^0.7.0" - logging library
- silero = "^0.4.1" - library for speech synthesizing
- sounddevice = "^0.4.6" - library for voice command input
- numpy = "^1.24.3" -  library for calculating cosine distance during speaker recognition
- pydantic = "^1.10.7" - library for validation environmental variables
- python-dotenv = "^1.0.0" - library for reading environmental variables

Recognition models can be downloaded via link [vosk official page](https://alphacephei.com/vosk/models) (you will need language recognition model along with speaker recognition model)

## Environmental variables

- SPEAKER_MODEL_PATH=models/speaker_model # path to spk model folder
- RECOGNIZING_MODEL_PATH=models/recognizing_model # path to recognizing model folder

- LANGUAGE=en # Language to speak
- MODEL_ID=v3_en # Id of speaker model from siler-model repo
- SPEAKER=random # Speaker name
- DEVICE_TYPE=cpu # Device type for rendering voice. cpu or gpu

- NAME=Kate # Name of the assistant used for giving commands


## Main methods description

### Helper.command

A decorator-based method for binding voice assistant commands. Example:

```
@helper.command("hello")
def hello(voice: dict):
    helper.speaker.say("Hello!")
```

Decorator receives a command name as an input. the function itself receives voice dictionary using this structure:
```
{
    'spk': ['123', '312321'] # voice vector
    'spk_frames': 12312 # frame amount in a single voice vector
    'text': command text with a shorted assistant name
}
```


### Helper.speaker.say

Method for playing back text as a speech. Example:
```
@helper.command("stop")
def stop(_):
    helper.speaker.say("Bye!")
    exit(0)
```

Method receives as an input a text that will be played back by the assistant.


### Helper.listener.add_speaker

Method for creating a speaker in the database of the voice assistant. Example:

```
@helper.command("my name is")
def create_speaker(voice):
    data = {"speaker": voice["text"], "spk": voice["spk"]}
    helper.listener.add_speaker(data)
    helper.speaker.say(f"Hello, {name}")
```

### Helper.listener.identify_speaker

Method for speaker identification by comparing with voices in the database. Example:

```
@helper.command("what is my name")
def identify(voice: dict):
    name = helper.listener.identify_speaker(voice["spk"], min_propability=40)[0]
    helper.speaker.say(f"I think your name is {name}")
```

Receives as an input a voice vector and a minimal probability for speaker recognition.

### Helper.listen

Method that launches infinite cycle of command listening. To start chatting with the voice assistant you have to call out his name.
Example: "Hello, Nancy!"


Assistant creating examples can be found via this link (../examples/)
