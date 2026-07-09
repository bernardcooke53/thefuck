def match(command):
    return (
        command.script.startswith("man")
        and "command not found" in command.output.lower()
    )


def get_new_command(command):
    return "man {}".format(command.script[3:])


priority = 2000
