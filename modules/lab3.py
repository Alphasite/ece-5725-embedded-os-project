from datetime import datetime

import threading
import time
from typing import List

from entities.entity import Entity

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("GPIO not available, mocking.")
    from unittest.mock import Mock

    GPIO = Mock()

from entities.external import Servo
from entities.loop import RunLoop
from entities.ui import Label, ModalButton, Button
from entities import red, green


def blink(settings, **kwargs):
    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

    # Create PWM Instances
    p1 = GPIO.PWM(26, 1)  # Frequency of 1Hz
    p2 = GPIO.PWM(19, 2)  # Frequenxy of 2Hz

    # Start PWM
    p1.start(50)  # 50% Duty Cycle
    p2.start(50)  # 50% Duty Cycle

    while True:
        time.sleep(2)


def pwm_calibrate(settings, **kwargs):
    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

    # Create PWM Instances
    p1 = GPIO.PWM(26, 46.5)  # 0.020ms between pulses
    p2 = GPIO.PWM(19, 46.5)  # 0.020ms between pulses

    # Start PWM
    p1.start(7)  # 7% Duty Cycle [1.5mS signal]
    p2.start(7)  # 7% Duty Cycle [1.5mS signal]

    while True:
        time.sleep(0.2)


def servo_control(settings, **kwargs):
    GPIO.setmode(GPIO.BCM)

    # Initialize Servos
    servo1 = Servo(19)
    servo2 = Servo(26)
    servo1.speed = 0
    servo2.speed = 0

    # Begin Sequence
    print("Servo Speed Sequence Initialized.")
    time.sleep(2)

    for i in range(0, -11, -1):
        servo1.speed = i / 10
        servo2.speed = i / 10
        print("Servo Speed Set to:", i / 10)
        time.sleep(3)

    for i in range(0, 11, 1):
        servo1.speed = i / 10
        servo2.speed = i / 10
        print("Servo Speed Set to:", i / 10)
        time.sleep(3)

    servo1.speed = 0
    servo2.speed = 0
    print("Sequence complete. Servos stopped.")

    return True


def servo_control_beta(settings, **kwargs):
    done_semaphore = threading.Semaphore(0)

    # Default Frequency/PWM Settings
    SpeedS1 = 0
    SpeedS2 = 0

    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Create Servos using Servo Class
    servo1 = Servo(26)
    servo2 = Servo(19)

    # Initialize Speed
    servo1.speed = SpeedS1
    servo2.speed = SpeedS2

    # Adjustment Code
    def quit(channel):
        GPIO.cleanup()
        print("Quit Button Pressed.")
        done_semaphore.release()

    def stop(channel):
        servo1.speed = 0
        servo2.speed = 0

    def adjust_freq_p1(channel):
        nonlocal SpeedS1

        time.sleep(0.5)
        if GPIO.input(23):
            SpeedS1 = SpeedS1 + 0.1  # add 1Hz to the signal
        else:
            SpeedS1 = SpeedS1 - 0.1  # subtract 1Hz from the signal

        servo1.speed = SpeedS1
        print("Servo 1 Speed [-1.0 to 1.0]: ", SpeedS1)

    def adjust_freq_p2(channel):
        nonlocal SpeedS2

        time.sleep(0.5)
        if GPIO.input(27):
            SpeedS2 = SpeedS2 + 0.1  # add 1Hz to the signal
        else:
            SpeedS2 = SpeedS2 - 0.1  # subtract 1Hz from the signal

        servo2.speed = SpeedS2
        print("Servo 2 Speed [-1.0 to 1.0]: ", SpeedS2)

    GPIO.add_event_detect(17, GPIO.FALLING, callback=quit, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=stop, bouncetime=300)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=adjust_freq_p1, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=adjust_freq_p2, bouncetime=300)

    done_semaphore.acquire()

    return True


def two_wheel(settings, **kwargs):
    done_semaphore = threading.Semaphore(0)

    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Create Servos using Servo Class
    servo1 = Servo(26)
    servo2 = Servo(19)

    def quit(channel):
        GPIO.cleanup()
        print("Quit Button Pressed.")
        done_semaphore.release()

    def stop(channel):
        time.sleep(1)
        if GPIO.input(22):
            servo1.speed = 0
            print("Servo 1: Stopped")
        else:
            servo2.speed = 0
            print("Servo 2: Stopped")

    def servo_1_increment(channel):
        time.sleep(1)
        if GPIO.input(23):
            SpeedS1 = 1.0  # add 1Hz to the signal
            print("Servo 1: Counter-Clockwise Rotation")
        else:
            SpeedS1 = -1.0  # subtract 1Hz from the signal
            print("Servo 1: Clockwise Rotation")
        servo1.speed = SpeedS1

    def servo_2_increment(channel):
        time.sleep(1)
        if GPIO.input(27):
            SpeedS2 = 1.0  # add 1Hz to the signal
            print("Servo 2: Counter-Clockwise Rotation")
        else:
            SpeedS2 = -1.0  # subtract 1Hz from the signal
            print("Servo 2: Clockwise Rotation")
        servo2.speed = SpeedS2

    GPIO.add_event_detect(17, GPIO.FALLING, callback=quit, bouncetime=600)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=stop, bouncetime=600)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=servo_1_increment, bouncetime=600)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=servo_2_increment, bouncetime=600)

    done_semaphore.acquire()

    return True


def update_servo_label_history(history, labels: List[Label]):
    for single_history, label in zip(history, labels):
        event, time = single_history
        label.text = "{0: <4} {1: >8}".format(event, time)


def rolling_control(settings, **kwargs):
    loop = RunLoop()

    servo_1 = Servo(19)
    servo_2 = Servo(26)

    servo_1.history = [("Stop", 0), ("Stop", 0), ("Stop", 0)]
    servo_2.history = [("Stop", 0), ("Stop", 0), ("Stop", 0)]

    servo_1.labels = [
        Label((60,  60), "", text_size=15),
        Label((60, 100), "", text_size=15),
        Label((60, 140), "", text_size=15),
    ]

    servo_2.labels = [
        Label((260,  60), "", text_size=15),
        Label((260, 100), "", text_size=15),
        Label((260, 140), "", text_size=15),
    ]

    update_servo_label_history(servo_1.history, servo_1.labels)
    update_servo_label_history(servo_2.history, servo_2.labels)

    def push_history(servo: Servo, label: str):
        time = datetime.now().strftime('%H:%M:%S')
        servo.history = servo.history[1:3] + [(label, time)]
        update_servo_label_history(servo.history, servo.labels)

    def servo_1_counter_clockwise(loop: RunLoop):
        servo_1.speed = 1.0
        push_history(servo_1, "CW")

    def servo_1_clockwise(loop: RunLoop):
        servo_1.speed = -1.0
        push_history(servo_1, "CCW")

    def servo_1_zero(loop: RunLoop):
        servo_1.speed = 0.0
        push_history(servo_1, "ZERO")

    def servo_2_counter_clockwise(loop: RunLoop):
        servo_2.speed = 1.0
        push_history(servo_2, "CW")

    def servo_2_clockwise(loop: RunLoop):
        servo_2.speed = -1.0
        push_history(servo_2, "CCW")

    def servo_2_zero(loop: RunLoop):
        servo_2.speed = 0.0
        push_history(servo_2, "ZERO")

    def servo_resume(loop: RunLoop):
        servo_1.start()
        servo_2.start()
        push_history(servo_1, "GO")
        push_history(servo_2, "GO")

    def servo_stop(loop: RunLoop):
        servo_1.stop()
        servo_2.stop()
        push_history(servo_1, "HALT")
        push_history(servo_2, "HALT")

    def exit_loop(loop: RunLoop):
        loop.done = True

    modal_active_button = Button((160, 100), "STOP", servo_stop, background_colour=red, text_size=35)
    modal_disabled_button = Button((160, 100), "Resume", servo_resume, background_colour=green, text_size=35)

    buttons = [
        ModalButton(modal_active_button, modal_disabled_button),

        Button((160, 140), "Quit", exit_loop, text_size=30),
        Button(( 35, 200), " + ", servo_1_clockwise, text_size=35),
        Button(( 75, 200), " 0 ", servo_1_zero, text_size=35),
        Button((115, 200), " - ", servo_1_counter_clockwise, text_size=35),
        Button((205, 200), " + ", servo_2_clockwise, text_size=35),
        Button((245, 200), " 0 ", servo_2_zero, text_size=35),
        Button((285, 200), " - ", servo_2_counter_clockwise, text_size=35),
    ]

    labels = [
        Label((80, 20), "Servo 1"),
        Label((240, 20), "Servo 2"),
        *servo_1.labels,
        *servo_2.labels,
    ]

    entities = [
        *labels,
        *buttons
    ]

    loop.start_loop(entities)

    return True


def robot_control(settings, **kwargs):
    loop = RunLoop()

    servo_1 = Servo(19)
    servo_2 = Servo(26)

    servo_1.history = [("Stop", 0), ("Stop", 0), ("Stop", 0)]
    servo_2.history = [("Stop", 0), ("Stop", 0), ("Stop", 0)]

    servo_1.labels = [
        Label((60,  60), "", text_size=15),
        Label((60, 100), "", text_size=15),
        Label((60, 140), "", text_size=15),
    ]

    servo_2.labels = [
        Label((260,  60), "", text_size=15),
        Label((260, 100), "", text_size=15),
        Label((260, 140), "", text_size=15),
    ]

    update_servo_label_history(servo_1.history, servo_1.labels)
    update_servo_label_history(servo_2.history, servo_2.labels)

    def push_history(servo: Servo, label: str):
        time = datetime.now().strftime('%H:%M:%S')
        servo.history = servo.history[1:3] + [(label, time)]
        update_servo_label_history(servo.history, servo.labels)

    def servo_1_counter_clockwise(loop: RunLoop):
        servo_1.speed = 0.5
        push_history(servo_1, "CW")

    def servo_1_clockwise(loop: RunLoop):
        servo_1.speed = -0.5
        push_history(servo_1, "CCW")

    def servo_1_zero(loop: RunLoop):
        servo_1.speed = 0.0
        push_history(servo_1, "ZERO")

    def servo_2_counter_clockwise(loop: RunLoop):
        servo_2.speed = 0.5
        push_history(servo_2, "CW")

    def servo_2_clockwise(loop: RunLoop):
        servo_2.speed = -0.5
        push_history(servo_2, "CCW")

    def servo_2_zero(loop: RunLoop):
        servo_2.speed = 0.0
        push_history(servo_2, "ZERO")

    def servo_resume(loop: RunLoop):
        servo_1.start()
        servo_2.start()
        push_history(servo_1, "GO")
        push_history(servo_2, "GO")

    def servo_stop(loop: RunLoop):
        servo_1.stop()
        servo_2.stop()
        push_history(servo_1, "HALT")
        push_history(servo_2, "HALT")

    def exit_loop(loop: RunLoop):
        loop.done = True

    def command_thread_function():
        steps = [
            (3, servo_1_clockwise, servo_2_counter_clockwise, "forward"),
            (2, servo_1_zero, servo_2_zero, "stop"),
            (3, servo_1_counter_clockwise, servo_2_clockwise, "backwards"),
            (2, servo_1_zero, servo_2_zero, "stop"),
            (1, servo_1_clockwise, servo_2_clockwise, "left"),
            (2, servo_1_zero, servo_2_zero, "stop"),
            (1, servo_1_counter_clockwise, servo_2_counter_clockwise, "right"),
            (2, servo_1_zero, servo_2_zero, "stop"),
        ]

        while not loop.done:
            for delay, left, right, command in steps:
                if loop.done:
                    break

                print(command)
                left(loop)
                right(loop)
                time.sleep(delay)

            print("Loop done, restarting.")

        print("Command thread done.")

    modal_active_button = Button((160, 100), "STOP", servo_stop, background_colour=red, text_size=35)
    modal_disabled_button = Button((160, 100), "Resume", servo_resume, background_colour=green, text_size=35)

    buttons = [
        ModalButton(modal_active_button, modal_disabled_button),
        Button((160, 140), "Quit", exit_loop, text_size=30),
    ]

    labels = [
        Label((80, 20), "Servo 1"),
        Label((240, 20), "Servo 2"),
        *servo_1.labels,
        *servo_2.labels,
    ]

    entities = [
        *labels,
        *buttons
    ]

    command_thread = threading.Thread(target=command_thread_function)
    command_thread.start()

    loop.start_loop(entities)

    command_thread.join()

    return True


MODULE = {
    "blink": blink,
    "pwm_calibrate": pwm_calibrate,
    "servo_control_beta": servo_control_beta,
    "servo_control": servo_control,
    "two_wheel": two_wheel,
    "rolling_control": rolling_control,
    "robot_control": robot_control,
}
