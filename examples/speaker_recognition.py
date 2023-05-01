from python_voice_assistant import Helper


# Creating an instance of a voice assistant class.
helper = Helper()


# Binding commands
@helper.command("stop")
def stop(_):
    helper.speaker.say("Bye!")
    exit(0)


# Command to add new speaker in the assistant database
@helper.command("my name is")
def create_speaker(voice):
    data = {"speaker": voice["text"], "spk": voice["spk"]}
    helper.listener.add_speaker(data)


# Command to recognize speaker
@helper.command("what is my name")
def identify(voice: dict):
    name = helper.listener.identify_speaker(voice["spk"], min_propability=40)[0]
    helper.speaker.say(f"I think your name is {name}")


# Lounch assistant
helper.listen()
