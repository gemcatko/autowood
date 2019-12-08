# need to run this code in python 2.7
#  add blink stick as root: sudo blinkstick --add-udev-rule
from blinkstick import blinkstick
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

try:
    for bstick in blinkstick.find_all():
        start_time = time.time()

        #time_between_blinks = 0.005
        #time_between_blinks2 = 0.007
        time_between_blinks = 0.005 # 2ms za s klasicky dvojkilik
        time_between_blinks2 = 0.005

        #time_between_blinks = 0.009 # pri 3m zaje vzdialenost ~47mm
        #time_between_blinks2 = 0.007 #pri 2m zaje vzdialenost !32mm
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
        #bstick.set_color(channel=0, index=1, name="red")
        time.sleep(time_between_blinks2)
        bstick.set_color(channel=0, index=0, name="")
        #bstick.set_color(channel=0, index=1, name="")
        time.sleep(time_between_blinks)
        bstick.set_color(channel=0, index=0, name="red")
        #bstick.set_color(channel=0, index=1, name="red")
        time.sleep(time_between_blinks2)
        bstick.set_color(channel=0, index=0, name="")
        #bstick.set_color(channel=0, index=1, name="")
        time.sleep(time_between_blinks)

        end_time = time.time()
        #print("You have bliked, Elapsed Time of the Blink:", end_time - start_time)
        #logging.debug('You have bliked, Elapsed Time of the Blink: %s', end_time - start_time)
        logging.debug('You have bliked 2 times, System time: %s', time.time())
except Exception, e:
        print("you have called blink stick to many times per second", e)