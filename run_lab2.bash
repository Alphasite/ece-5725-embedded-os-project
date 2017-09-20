#!/usr/bin/env bash
echo #########################
echo RUNNING mplayer in BG!
echo #########################

sudo SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb1 mplayer -input file=/home/pi/fifos/video_fifo -v sdl -framedrop /home/pi/bigbuckbunny320p.mp4 &

echo #########################
echo RUNNING python in FG!
echo #########################

source ../venv/bin/activate
python run.py lab2.six_button

echo #########################
echo Done!
echo #########################
