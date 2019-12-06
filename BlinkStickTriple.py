# need to run this code in python 2.7
#  add blink stick as root: sudo blinkstick --add-udev-rule
from blinkstick import blinkstick
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

try:
    for bstick in blinkstick.find_all():
        start_time = time.time()
        time_between_blinks_dark = 0.005
        time_between_blinks_light = 0.01
        """
        print ("Found device:")
        print ("    Manufacturer:  " + bstick.get_manufacturer())
        print ("    Description:   " + bstick.get_description())
        print ("    Serial:        " + bstick.get_serial())
        print ("    Current Color: " + bstick.get_color(color_format="hex"))
        print ("    Info Block 1:  " + bstick.get_info_block1())
        print ("    Info Block 2:  " + bstick.get_info_block2())
        """
        bstick.set_color(channel=0, index=0, name="red")
        time.sleep(time_between_blinks_light)
        bstick.set_color(channel=0, index=0, name="")
        time.sleep(time_between_blinks_dark)
        bstick.set_color(channel=0, index=0, name="red")
        #bstick.set_color(channel=0, index=1, name="red")
        time.sleep(time_between_blinks_light)
        bstick.set_color(channel=0, index=0, name="")
        time.sleep(time_between_blinks_dark)
        bstick.set_color(channel=0, index=0, name="red")
        #bstick.set_color(channel=0, index=1, name="red")
        time.sleep(time_between_blinks_light)
        bstick.set_color(channel=0, index=0, name="")
        #bstick.set_color(channel=0, index=1, name="")
        #bstick.set_color(channel=0, index=1, name="")
        end_time = time.time()
        #print("You have bliked, Elapsed Time of the Blink:", end_time - start_time)
        #logging.debug('You have bliked, Elapsed Time of the Blink: %s', end_time - start_time)
        logging.debug('You have bliked 3 times, System time: %s', time.time())
except Exception, e:
        print("you have called blink stick to many times per second", e)