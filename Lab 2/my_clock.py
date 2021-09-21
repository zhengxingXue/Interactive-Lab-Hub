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
def draw_clock_eye(big_center, big_r, small_r, theta, compensation = 1):
    draw_circle(center_coordinate=big_center, radius=big_r, fill='white')
    r = big_r - small_r + compensation  # compensate for the edge
    small_center = (
        big_center[0] + r * math.sin(theta),
        big_center[1] + r * math.cos(theta)
    )
    draw_circle(center_coordinate=small_center, radius=small_r, fill='black')

# clock eye, drawing constant
big_r, small_r = 30, 25
clock_eye_y = big_r + 10
spacing = big_r * 2 + 30

# clock mouth, drawing constant
mouth_width, mouth_height = width / 2, height-big_r*2-20
m_x0, m_y0 = width/2 - mouth_width/2, big_r*2 - 5
m_x1, m_y1 = m_x0 + mouth_width, m_y0 + mouth_height
m_bounding_box = [m_x0, m_y0, m_x1, m_y1]

# clock teeth, drawing constant
t_width, t_height = 15, 15
t_x0, t_y0 = width/2 - t_width/2, m_y1
t_x1, t_y1 = t_x0 + t_width, t_y0 + t_height
t_bounding_box = [t_x0, t_y0, t_x1, t_y1]

SHOW_TEETH = False
SHOW_DEBUG_INFO = False

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # clock eye for seconds 
    draw_clock_eye(
        big_center = (width / 2 + spacing / 2, clock_eye_y), 
        big_r = big_r, 
        small_r = small_r, 
        theta = (30 - datetime.now().second) / 30 * math.pi # Transfrom theta to fit the clock convention
    )
    
    # clock eye for minutes
    draw_clock_eye(
        big_center = (width / 2 - spacing / 2, clock_eye_y), 
        big_r = big_r, 
        small_r = small_r, 
        theta = (30 - datetime.now().minute) / 30 * math.pi # Transfrom theta to fit the clock convention
    )

    # mouth
    draw.arc(m_bounding_box, start = 30, end = 150, fill="white", width=3)

    if SHOW_TEETH:
        # teeth
        draw.rectangle(t_bounding_box, fill="white")
    
    if SHOW_DEBUG_INFO: 
        time_string = time.strftime("%H:%M:%S")
        dx, dy = font.getsize(time_string)
        draw.text((0, height - dy), time_string, font=font, fill="white")

    # just button A pressed, show teeth
    if buttonB.value and not buttonA.value:  
        SHOW_TEETH = not SHOW_TEETH
    # just button B pressed, show digital clock display
    elif buttonA.value and not buttonB.value:  
        SHOW_DEBUG_INFO = not SHOW_DEBUG_INFO
        # s = "Debug = " + str(SHOW_DEBUG_INFO)
        # dx, dy = font.getsize(s)
        # draw.text(((width - dx) / 2, (height - dy) / 2), s, font=font, fill="white")

    # Display image.
    disp.image(image, rotation)
    # time.sleep(1/3)
