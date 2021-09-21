import math
import time
from datetime import datetime
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Setup the buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# helper function for drawing circles
def draw_circle(center_coordinate, radius, fill = 'white', outline = 'black'):
    x, y = center_coordinate
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=fill, outline=outline)

# helper function for draing 'clock eye'
def draw_clock_eye(big_center, big_r, small_r, theta):
    draw_circle(center_coordinate=big_center, radius=big_r, fill='white')
    small_center = (
        big_center[0] + (big_r - small_r) * math.sin(theta),
        big_center[1] + (big_r - small_r) * math.cos(theta)
    )
    draw_circle(center_coordinate=small_center, radius=small_r, fill='black')

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # nothing pressed
    if buttonA.value and buttonB.value:
        big_r, small_r = 30, 20
        spacing = big_r * 2 + 10
        # clock eye for seconds 
        draw_clock_eye(
            big_center = (width / 2 + spacing / 2, height / 2), 
            big_r = big_r, 
            small_r = small_r, 
            theta = (30 - datetime.now().second) / 30 * math.pi # Transfrom theta to fit the clock convention
        )
        # clock eye for minutes
        draw_clock_eye(
            big_center = (width / 2 - spacing / 2, height / 2), 
            big_r = big_r, 
            small_r = small_r, 
            theta = (30 - datetime.now().minute) / 30 * math.pi # Transfrom theta to fit the clock convention
        )
        
        draw.text((0,0), str(datetime.now().minute) + ":" + str(datetime.now().second), font=font, fill="white")
        
    # just button B pressed, show digital clock display
    elif buttonA.value and not buttonB.value:  
        time_string = time.strftime("%m/%d/%Y %H:%M:%S")
        dx, dy = font.getsize(time_string)
        x = (width - dx) / 2
        y = (height - dy) / 2
        draw.text((x, y), time_string, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    time.sleep(1)
