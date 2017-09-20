import logging
import os
import time


def exit(settings, **kwargs) -> bool:
    return passthrough(settings, command="quit")


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


def gpio_handler_1_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            time.sleep(0.2)
            if not GPIO.input(23):
                print("Button 23: has been pressed!")
    finally:
        GPIO.cleanup()


def gpio_handler_4_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            if not GPIO.input(17):
                print("Button 17: has been pressed!")

            if not GPIO.input(22):
                print("Button 22: has been pressed!")

            if not GPIO.input(23):
                print("Button 23: has been pressed!")

            if not GPIO.input(27):
                print("Button 27: has been pressed!")

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


def gpio_handler(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            if not GPIO.input(17):
                passthrough(settings, command="pause")
                print("Pause Button Pressed.")

            if not GPIO.input(22):
                passthrough(settings, command="seek 1 0")
                print("Fwd x10 Button Pressed.")

            if not GPIO.input(23):
                passthrough(settings, command="seek -1 0")
                print("Rew x10 Button Pressed.")

            if not GPIO.input(27):
                passthrough(settings, command="quit")
                print("Quit Button Pressed.")

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


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
    "one_button": gpio_handler_1_button,
    "four_button": gpio_handler_4_button,
    "": run,
}
