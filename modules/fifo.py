import logging
import os


def exit(settings, **kwargs) -> bool:
    return passthrough(settings, command="exit")


def stop(settings, **kwargs) -> bool:
    return passthrough(settings, command="stop")


def pause(settings, **kwargs) -> bool:
    return passthrough(settings, command="pause")


def load(settings, arguments, **kwargs) -> bool:
    return passthrough(settings, command="loadfile {file}".format(file=arguments))


def loop(settings, arguments, **kwargs) -> bool:
    if len(arguments) > 0:
        iterations = arguments[0]
    else:
        iterations = ""

    return passthrough(settings, command="loop {0}".format(iterations))


def mute(settings, arguments, **kwargs) -> bool:
    if len(arguments) > 0:
        iterations = arguments[0]
    else:
        print("Mute requires and argument of value 0 OR 1")
        return False

    return passthrough(settings, command="mute {0}".format(iterations))


def gpio_handler(settings, **kwargs) -> bool:

    return False


def run(settings, arguments, **kwargs) -> bool:
    command = " ".join(arguments)
    return passthrough(settings, command)


def passthrough(settings, command, **kwargs) -> bool:
    try:
        if not os.path.exists(settings.fifo_path):
            print("File does not exist.")
            return False

        with open(settings.fifo_path, "w") as f:
            f.write("{command}\n".format(command=command))

        return True
    except:
        logging.exception("Exception encountered while writing.")
        return False


MODULE = {
    "play": pause,
    "pause": pause,
    "load": load,
    "mute": mute,
    "loop": loop,
    "stop": stop,
    "exit": exit,
    "buttons": gpio_handler,
    "": run,
}
