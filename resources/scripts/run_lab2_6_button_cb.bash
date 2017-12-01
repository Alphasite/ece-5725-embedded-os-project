#!/usr/bin/env bash
echo #########################
echo RUNNING mplayer in BG!
echo #########################

sudo SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb1 mplayer \
    -input file=/home/pi/fifos/video_fifo \
    -framedrop /home/pi/bigbuckbunny320p.mp4 \
    -v sdl \
    >$0.log \
    &

echo #########################
echo RUNNING python in FG!
echo #########################

source ../venv/bin/activate
python run.py lab2.six_button_interrupt

echo #########################
echo Done!
echo #########################
