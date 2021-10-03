# ask for zipcode
say() { local IFS=+;/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$*&tl=en"; }
say " What's your zipcode?"

# record response
arecord -D hw:2,0 -f cd -c1 -r 48000 -d 5 -t wav recorded_mono.wav

# process and print response
python3 zipcode.py recorded_mono.wav
