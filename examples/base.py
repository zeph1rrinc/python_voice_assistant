from python_voice_assistant import Helper


# Creating an instance of a voice assistant class.
helper = Helper()


# Binding commands
@helper.command("hello")
def hello(_):
    helper.speaker.say("Hello!")


@helper.command("stop")
def stop(_):
    helper.speaker.say("Bye!")
    exit(0)


# Launching the assistant.
helper.listen()
