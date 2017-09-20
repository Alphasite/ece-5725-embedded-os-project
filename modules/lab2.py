import logging
import os
import time
import sys
import threading

done_semaphore = threading.Semaphore(0)
fifo_write_lock = threading.Lock()

def gpio_handler_6_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27, 26, 19], GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
                sys.exit()

            if not GPIO.input(26):
                passthrough(settings, command="seek -3 0")
                print("Rew x30 Button Pressed.")

            if not GPIO.input(19):
                passthrough(settings, command="seek 3 0")
                print("Fwd x30 Button Pressed.")

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


def gpio_handler_6_button_interrupt(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27, 26, 19], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def pause():
            passthrough(settings, command="pause")
            print("Pause Button Pressed.")

        def seek_forwards_1():
            passthrough(settings, command="seek 1 0")
            print("Fwd x10 Button Pressed.")

        def seek_back_1():
            passthrough(settings, command="seek -1 0")
            print("Rew x10 Button Pressed.")

        def seek_back_3():
            passthrough(settings, command="seek -3 0")
            print("Rew x30 Button Pressed.")

        def seek_forwards_3():
            passthrough(settings, command="seek 3 0")
            print("Fwd x30 Button Pressed.")

        def quit():
            passthrough(settings, command="quit")
            print("Quit Button Pressed.")
            done_semaphore.release()
            sys.exit()

        GPIO.add_event_detect(17, GPIO.FALLING, callback=pause, bouncetime=300)
        GPIO.add_event_detect(19, GPIO.FALLING, callback=seek_forwards_3, bouncetime=300)
        GPIO.add_event_detect(22, GPIO.FALLING, callback=seek_forwards_1, bouncetime=300)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=seek_back_1, bouncetime=300)
        GPIO.add_event_detect(26, GPIO.FALLING, callback=seek_back_3, bouncetime=300)
        GPIO.add_event_detect(27, GPIO.FALLING, callback=quit, bouncetime=300)

        done_semaphore.acquire()
    finally:
        GPIO.cleanup()


def passthrough(settings, command, **kwargs) -> bool:
    try:
        with fifo_write_lock.lock():
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
    "six_button": gpio_handler_6_button,
    "six_button_interrupt": gpio_handler_6_button_interrupt,
}
