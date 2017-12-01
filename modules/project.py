from __future__ import division, print_function
import os
import serial
import sys

from entities import red, green
from entities.external import ActuatorController
from entities.loop import RunLoop
from entities.ui import Label, Button, ModalButton, LinkedProgressSlider, StatusPip, FrameUpdateEvent

"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 4, Lab Section 02, 01/11/17
"""

import time

if "DEBUG" in os.environ:
    debug = True
else:
    debug = False

debug = False


def serial_input(settings, **kwargs):
    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    with serial.Serial('/dev/ttyS1', 19200, timeout=1) as ser:
        while True:
            line = ser.readline()  # read a '\n' terminated line
            print(line)

    while True:
        time.sleep(2)


def gui(settings, arguments, **kwargs):
    serial_path = "/dev/tty.usbmodem14322" if len(arguments) == 0 else arguments[0]

    loop = RunLoop()
    controller = ActuatorController(serial_path)

    def exit_loop(loop):
        loop.done = True
        controller.quit()

    def stop_button(loop):
        print("Stop")
        for actuator in controller.actuators:
            actuator.stopped = True

    def start_button(loop):
        print("Start")
        for actuator in controller.actuators:
            actuator.stopped = False

    modal_active_button = Button((120, 210), "Stop", stop_button, background_colour=red, text_size=30)
    modal_disabled_button = Button((120, 210), "Start", start_button, background_colour=green, text_size=30)

    buttons = [
        ModalButton(modal_disabled_button, modal_active_button),
        Button((200, 210), "Quit", exit_loop, text_size=30),
    ]

    labels = [
        Label((40, 20), "Servo 1"),
        Label((120, 20), "Servo 2"),
        Label((200, 20), "Servo 3"),
        Label((280, 20), "Servo 4"),
        Label((40, 220), "PWM"),
    ]

    bar_colour = (40, 40, 40)
    tri_colour = (10, 200, 10)

    controls = [
        LinkedProgressSlider(0.5, 100, 10, (40, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (120, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (200, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (280, 120), bar_colour, tri_colour)
    ]

    status = [
        StatusPip((40, 45), 8, green),
        StatusPip((120, 45), 8, green),
        StatusPip((200, 45), 8, red),
        StatusPip((280, 45), 8, red),
    ]

    def update_frame(loop, time_delta):
        # link slider target/actual with actuator target/actual
        for i in range(4):  # TODO
            actuator = controller.actuators[i]
            control = controls[i]
            pip = status[i]

            actuator.target_position = control.slider.position
            control.bar.position = actuator.position

            if actuator.stalled:
                pip.colour = red
            else:
                pip.colour = green

        duty_cycle = controller.actuators[0].duty_cycle
        labels[4].text = "{0:0.2f}".format(duty_cycle)

    entities = []
    entities += labels
    entities += buttons
    entities += controls
    entities += status
    entities.append(FrameUpdateEvent(update_frame))

    stop_button(loop)

    sys.setcheckinterval(0)

    controller.start()
    loop.start_loop(entities)

    return True


MODULE = {
    "serial": serial_input,
    "gui": gui
}
