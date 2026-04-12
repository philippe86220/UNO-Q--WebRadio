#!/bin/sh
/usr/bin/mpg123 -o alsa -a hw:0,0 --buffer 4096 "http://icecast.radiofrance.fr/francemusique-midfi.mp3"
