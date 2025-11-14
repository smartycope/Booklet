from PIL import Image,ImageDraw
from Screen import Screen

disp = Screen()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image1)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,disp.width, disp.height), outline=0, fill=0)
disp.show_image(image1)


try:
    while True:
        # with canvas(device) as draw:
        if disp.gpio_key_up_pin.value == 0: # button is released
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up
        else: # button is pressed:
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
            print ("Up")

        if disp.gpio_key_left_pin.value == 0: # button is released
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
        else: # button is pressed:
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
            print ("left")

        if disp.gpio_key_right_pin.value == 0: # button is released
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        else: # button is pressed:
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled
            print ("right")

        if disp.gpio_key_down_pin.value == 0: # button is released
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
        else: # button is pressed:
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled
            print ("down")

        if disp.gpio_key_press_pin.value == 0: # button is released
            draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center
        else: # button is pressed:
            draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
            print ("center")

        if disp.gpio_key1_pin.value == 0: # button is released
            draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button
        else: # button is pressed:
            draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled
            print ("KEY1")

        if disp.gpio_key2_pin.value == 0: # button is released
            draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button]
        else: # button is pressed:
            draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled
            print ("KEY2")

        if disp.gpio_key3_pin.value == 0: # button is released
            draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
        else: # button is pressed:
            draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled
            print ("KEY3")
        disp.show_image(image1)
except:
	print("except")

disp.close()


