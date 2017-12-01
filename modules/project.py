import os
import serial

from entities import red, green
from entities.external import ActuatorController
from entities.loop import RunLoop
from entities.ui import Slider, Label, Button, ModalButton, LinkedProgressSlider, StatusPip, FrameUpdateEvent

"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 4, Lab Section 02, 01/11/17
"""
import time

# if "DEBUG" in os.environ:
#     debug = True
# else:
#     debug = False
debug = False


def serial_input(settings, **kwargs):
    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    with serial.Serial('/dev/ttyS1', 19200, timeout=1) as ser:
        while True:
            line = ser.readline()  # read a '\n' terminated line
            print(line)

    while True:
        time.sleep(2)


def gui(settings, arguments, **kwargs) -> bool:
    serial_path = "/dev/tty.usbmodem14322" if len(arguments) == 0 else arguments[0]

    loop = RunLoop()
    controller = ActuatorController(serial_path)

    def exit_loop(loop: RunLoop):
        loop.done = True
        controller.quit()

    def stop_button(loop:RunLoop):
        print("Stop")
        for actuator in controller.actuators:
            actuator.stopped = True

    def start_button(loop:RunLoop):
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
        Label(( 40, 20), "Servo 1"),
        Label((120, 20), "Servo 2"),
        Label((200, 20), "Servo 3"),
        Label((280, 20), "Servo 4"),
        Label((40, 220), "PWM"),
    ]

    bar_colour = (40, 40, 40)
    tri_colour = (10, 200, 10)

    controls = [
        LinkedProgressSlider(0.5, 100, 10, ( 40, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (120, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (200, 120), bar_colour, tri_colour),
        LinkedProgressSlider(0.5, 100, 10, (280, 120), bar_colour, tri_colour)
    ]

    status = [
        StatusPip(( 40, 45), 8, green),
        StatusPip((120, 45), 8, green),
        StatusPip((200, 45), 8, red),
        StatusPip((280, 45), 8, red),
    ]

    def update_frame(loop: 'RunLoop', time_delta: float):
        # link slider target/actual with actuator target/actual
        for i in range(1): # TODO
            actuator = controller.actuators[i]
            control = controls[i]
            pip = status[i]

            actuator.position = control.position
            control.position = actuator.position

            if actuator.stalled:
                pip.colour = red
            else:
                pip.colour = green

        labels[4].text = "{0:0.2f}".format(controller.actuators[0].duty_cycle)

    entities = [
        *labels,
        *buttons,
        *controls,
        *status,
        FrameUpdateEvent(update_frame)
    ]

    stop_button(loop)
    loop.start_loop(entities)

    return True


MODULE = {
    "serial": serial_input,
    "gui": gui
}
