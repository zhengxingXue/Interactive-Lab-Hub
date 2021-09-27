import math
import time
from datetime import datetime
import subprocess
import digitalio
import board
import busio
from i2c_button import I2C_Button
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

## Example code from library_example.py
# initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# scan the I2C bus for devices
while not i2c.try_lock():
	pass
devices = i2c.scan()
i2c.unlock()
print('I2C devices found:', [hex(n) for n in devices])
default_addr = 0x6f
if default_addr not in devices:
	print('warning: no device at the default button address', default_addr)

# initialize the button
button = I2C_Button(i2c)

button.led_bright = 50
button.led_gran = 0
button.led_cycle_ms = 0
button.led_off_ms = 0

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
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=fill, outline=outline, width=2)

# helper function for drawing 'clock eye'
def draw_clock_eye(big_center, big_r, small_r, theta, compensation = 1):
    # outer part of eye
    draw_circle(center_coordinate=big_center, radius=big_r, fill='white')
    r = big_r - small_r + compensation  # compensate for the edge
    small_center = (
        big_center[0] + r * math.sin(theta),
        big_center[1] + r * math.cos(theta)
    )
    # inner part of eye
    draw_circle(center_coordinate=small_center, radius=small_r, fill='blue')
    # additional line for better visual
    line_length = 5
    line_color = 'green'
    draw.line((big_center[0] + big_r, big_center[1], big_center[0] + big_r + line_length, big_center[1]), fill=line_color, width=2)
    draw.line((big_center[0] - big_r, big_center[1], big_center[0] - big_r - line_length, big_center[1]), fill=line_color, width=2)
    draw.line((big_center[0], big_center[1] + big_r, big_center[0], big_center[1] + big_r + line_length), fill=line_color, width=2)
    draw.line((big_center[0], big_center[1] - big_r, big_center[0], big_center[1] - big_r - line_length), fill=line_color, width=2)

# clock eye, drawing constant
big_r, small_r = 25, 20
clock_eye_y = big_r + 10
spacing = big_r * 2 + 25

# clock mouth, drawing constant
mouth_width, mouth_height = width / 2, height-big_r*2-20
m_x0, m_y0 = width/2 - mouth_width/2, big_r*2 + 20
m_x1, m_y1 = m_x0 + mouth_width, m_y0 + mouth_height

# helper function for drawing face and clothe
def draw_face_clothe():
    # draw face
    draw.polygon(
        (
            (width/2 - 80, 10),
            (width/2 - 70, 0),
            (width/2 + 70, 0),
            (width/2 + 80, 10),

            (width/2 + 80, height - 60),
            (width/2 + 20, height),
            (width/2 - 20, height),
            (width/2 - 80, height - 60),

        ),
        outline=0, fill="white"
    )
    # draw left collar 
    draw.polygon(
        (
            (width/2 - 30, height),
            (width/2 - 70, height - 40),
            (width/2 - 70, height)
        ),
        outline=0, fill='green'
    )
    # draw left clothe
    draw.polygon(
        (
            (width/2 - 70, height - 40),
            (0, height - 20),
            (0, height),
            (width/2 - 70, height)
        ),
        outline=0, fill='red'
    )
    # draw right collar
    draw.polygon(
        (
            (width/2 + 30, height),
            (width/2 + 70, height - 40),
            (width/2 + 70, height)
        ),
        outline=0, fill='green'
    )
    # draw right clothe
    draw.polygon(
        (
            (width/2 + 70, height - 40),
            (width, height - 20),
            (width, height),
            (width/2 + 70, height)
        ),
        outline=0, fill='red'
    )

SHOW_HOUR = True
SHOW_DEBUG_INFO = False

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill="black")

    # draw face and clothe
    draw_face_clothe()

    if not SHOW_HOUR:
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
    else:
        # clock eye for minutes 
        draw_clock_eye(
            big_center = (width / 2 + spacing / 2, clock_eye_y), 
            big_r = big_r, 
            small_r = small_r, 
            theta = (30 - datetime.now().minute) / 30 * math.pi # Transfrom theta to fit the clock convention
        )

        # clock eye for hour
        draw_clock_eye(
            big_center = (width / 2 - spacing / 2, clock_eye_y), 
            big_r = big_r, 
            small_r = small_r, 
            theta = (6 - datetime.now().hour % 12) / 12 * math.pi # Transfrom theta to fit the clock convention
        )

    # nose    
    draw.polygon(
        (
            (width/2, clock_eye_y+big_r),
            (width/2 - 15, clock_eye_y+big_r + 15),
            (width/2 + 15, clock_eye_y+big_r + 15),
        ),
        outline=0, fill='red'
    )

    # mouth
    draw.polygon(
        (
            (m_x0, m_y0),
            (m_x0 + 39, m_y0+20),
            (m_x1 - 39, m_y0+20),
            (m_x1, m_y0),
            (width/2 + 10, m_y0+50),
            (width/2 - 10, m_y0+50)
        ),
        fill = "red",
        outline = 'black'
    )
    
    if SHOW_DEBUG_INFO: 
        time_string = time.strftime("%H:%M:%S")
        dx, dy = font.getsize(time_string)
        draw.text((0, height - dy), time_string, font=font, fill="white")

    # just button B pressed, show digital clock display for debug
    if buttonA.value and not buttonB.value:  
        SHOW_DEBUG_INFO = not SHOW_DEBUG_INFO

    # Display image.
    disp.image(image, rotation)

    button.clear()
    time.sleep(1/2)
    # I2C button clicked
    if button.status.been_clicked:
        SHOW_HOUR = not SHOW_HOUR
    
    if SHOW_HOUR:
        button.led_bright = 50
        button.led_gran = 1
        button.led_cycle_ms = 1000
        button.led_off_ms = 1000
    else:
        button.led_bright = 50
        button.led_gran = 0
        button.led_cycle_ms = 0
        button.led_off_ms = 0
