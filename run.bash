sudo SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb1 mplayer -input file=/home/pi/fifos/video_fifo -v sdl -framedrop /home/pi/bigbuckbunny320p.mp4
source ../venv/bin/activate
python run.py repl