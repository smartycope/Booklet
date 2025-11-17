# import spidev as SPI
import atexit
import logging
# import ST7789
import time
# from Screen import Screen
from src.Screen import Screen

from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.DEBUG)
# 240x240 display with hardware SPI:
disp = Screen()

# Create blank image for drawing.

# draw.rectangle((5,25,7,27), fill = "BLACK")
# draw.rectangle((5,40,8,43), fill = "BLACK")
# draw.rectangle((5,55,9,59), fill = "BLACK")

# logging.info("draw line")
# draw.line([(20, 10),(70, 60)], fill = "RED",width = 1)
# draw.line([(70, 10),(20, 60)], fill = "RED",width = 1)
# draw.line([(170,15),(170,55)], fill = "RED",width = 1)
# draw.line([(150,35),(190,35)], fill = "RED",width = 1)

# logging.info("draw rectangle")

# draw.rectangle([(20,10),(70,60)],fill = "WHITE",outline="BLUE")
# draw.rectangle([(85,10),(130,60)],fill = "BLUE")

# logging.info("draw circle")
# draw.arc((150,15,190,55),0, 360, fill =(0,255,0))
# draw.ellipse((150,65,190,105), fill = (0,255,0))

# logging.info("draw text")
# Font1 = ImageFont.truetype("assets/Orbitron-VariableFont_wght.ttf",25)

# draw.rectangle([(0,65),(140,100)],fill = "WHITE")
# draw.text((5, 68), 'Hello world', fill = "BLACK",font=Font1)
# draw.rectangle([(0,115),(190,160)],fill = "RED")
# draw.text((5, 118), 'WaveShare', fill = "WHITE",font=Font1)
# draw.text((5, 160), '1234567890', fill = "GREEN",font=Font1)
# text= u"微雪电子"
# draw.text((5, 200),text, fill = "BLUE",font=Font1)
# im_r=image1.rotate(270)
# disp.show_image(im_r)
# time.sleep(3)
# logging.info("show image")
image0 = Image.new("RGB", (100, 100), "BLUE")
disp.show_image(image0)
time.sleep(3)

image1 = Image.new("RGB", (100, 100), "WHITE")
draw = ImageDraw.Draw(image1)

draw.rectangle((25,25,75,75), fill = "BLACK")
disp.show_image(image1, x_start=25, y_start=25, x_end=75, y_end=75)
# time.sleep(3)

while True:
    time.sleep(0.1)

