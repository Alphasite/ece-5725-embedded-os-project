import sys
import os
import threading
import time

import pygame

from modules.fifo import passthrough

timestamp = time.time()

done_semaphore = threading.Semaphore(0)


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
                break

            if not GPIO.input(26):
                passthrough(settings, command="seek -3 0")
                print("Rew x30 Button Pressed.")

            if not GPIO.input(19):
                passthrough(settings, command="seek 3 0")
                print("Fwd x30 Button Pressed.")

            time.sleep(0.2)

            if time.time() - timestamp > 10:
                passthrough(settings, command="quit")
                break

    finally:
        GPIO.cleanup()

    return True


def gpio_handler_6_button_interrupt(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27, 26, 19], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def pause(channel):
            passthrough(settings, command="pause")
            print("Pause Button Pressed.")

        def seek_forwards_1(channel):
            passthrough(settings, command="seek 1 0")
            print("Fwd x10 Button Pressed.")

        def seek_back_1(channel):
            passthrough(settings, command="seek -1 0")
            print("Rew x10 Button Pressed.")

        def seek_back_3(channel):
            passthrough(settings, command="seek -3 0")
            print("Rew x30 Button Pressed.")

        def seek_forwards_3(channel):
            passthrough(settings, command="seek 3 0")
            print("Fwd x30 Button Pressed.")

        def quit(channel):
            passthrough(settings, command="quit")
            print("Quit Button Pressed.")
            done_semaphore.release()

        GPIO.add_event_detect(17, GPIO.FALLING, callback=pause, bouncetime=300)
        GPIO.add_event_detect(19, GPIO.FALLING, callback=seek_forwards_3, bouncetime=300)
        GPIO.add_event_detect(22, GPIO.FALLING, callback=seek_forwards_1, bouncetime=300)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=seek_back_1, bouncetime=300)
        GPIO.add_event_detect(26, GPIO.FALLING, callback=seek_back_3, bouncetime=300)
        GPIO.add_event_detect(27, GPIO.FALLING, callback=quit, bouncetime=300)

        time.sleep(10)
        quit(None)
        # done_semaphore.acquire()
    finally:
        GPIO.cleanup()

    return True


def ball_1(settings, **kwargs):
    os.putenv('SDL_FBDEV', '/dev/fb1')

    pygame.init()

    size = width, height = 320, 240
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    ball = pygame.image.load("resources/lab2/ball.png")
    ball = pygame.transform.scale(ball, (50, 50))
    ballrect = ball.get_rect()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]

        screen.fill(black)
        screen.blit(ball, ballrect)
        pygame.display.flip()


def ball_2(settings, **kwargs):
    os.putenv('SDL_FBDEV', '/dev/fb1')

    pygame.init()

    size = width, height = 320, 240
    speed = [2, 2]
    speed2 = [3, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    ball = pygame.image.load("resources/lab2/ball.png")
    ball = pygame.transform.scale(ball, (50, 50))
    ballrect = ball.get_rect()

    ball2 = pygame.image.load("resources/lab2/tennis_ball.png")
    ball2 = pygame.transform.scale(ball2, (30, 30))
    ballrect2 = ball2.get_rect()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]

        ballrect2 = ballrect2.move(speed2)
        if ballrect2.left < 0 or ballrect2.right > width:
            speed2[0] = -speed2[0]
        if ballrect2.top < 0 or ballrect2.bottom > height:
            speed2[1] = -speed2[1]

        screen.fill(black)
        screen.blit(ball, ballrect)
        screen.blit(ball2, ballrect2)
        pygame.display.flip()


def ball_2_collide(settings, **kwargs):
    os.putenv('SDL_FBDEV', '/dev/fb1')

    pygame.init()

    size = width, height = 320, 240
    speed = [2, 2]
    speed2 = [3, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    ball = pygame.image.load("resources/lab2/ball.png")
    ball = pygame.transform.scale(ball, (50, 50))
    ballrect = ball.get_rect()

    ball2 = pygame.image.load("resources/lab2/tennis_ball.png")
    ball2 = pygame.transform.scale(ball2, (30, 30))
    ballrect2 = ball2.get_rect()
    ballrect2 = ballrect2.move([width / 2, height / 2])

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]

        ballrect2 = ballrect2.move(speed2)
        if ballrect2.left < 0 or ballrect2.right > width:
            speed2[0] = -speed2[0]
        if ballrect2.top < 0 or ballrect2.bottom > height:
            speed2[1] = -speed2[1]

        if ballrect.colliderect(ballrect2):
            speed[0] *= -1
            speed[1] *= -1

            speed2[0] *= -1
            speed2[1] *= -0.8

        screen.fill(black)
        screen.blit(ball, ballrect)
        screen.blit(ball2, ballrect2)
        pygame.display.flip()


MODULE = {
    "six_button": gpio_handler_6_button,
    "six_button_interrupt": gpio_handler_6_button_interrupt,
    "ball_1": ball_1,
    "ball_2": ball_2,
    "ball_2_collide": ball_2_collide,
}
