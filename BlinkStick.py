# need to run this code in python 2.7
#  add blink stick as root: sudo blinkstick --add-udev-rule
from blinkstick import blinkstick
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

try:
    for bstick in blinkstick.find_all():
        start_time = time.time()
        bstick.blink(channel=0, index=3, red=255, green=0, blue=0, name=None, hex=None, repeats=1, delay=7)

        ##bstick.set_color(channel=0, index=0, name="red")
        #bstick.set_color(channel=0, index=1, name="red")
        #bstick.set_color(channel=0, index=2, name="red")
        #bstick.set_color(channel=0, index=3, name="red")

        ##bstick.set_color(channel=0, index=0, name="")
        #bstick.set_color(channel=0, index=1, name="")
        #bstick.set_color(channel=0, index=2, name="")
        #bstick.set_color(channel=0, index=3, name="")

        """
        bstick.set_color(channel=0, index=4, name="red")
        bstick.set_color(channel=0, index=5, name="red")
        bstick.set_color(channel=0, index=6, name="red")
        bstick.set_color(channel=0, index=7, name="red")
        """
        """
        for bstick in blinkstick.find_all():
            bstick.turn_off()
            print bstick.get_serial() + " turned off
        """
        """
        bstick.set_color(channel=0, index=4, name="")
        bstick.set_color(channel=0, index=5, name="")
        bstick.set_color(channel=0, index=6, name="")
        bstick.set_color(channel=0, index=7, name="")
        """
        end_time = time.time()
        #print("You have bliked, Elapsed Time of the Blink:", end_time - start_time)
        #logging.debug('You have bliked, Elapsed Time of the Blink: %s', end_time - start_time)
        logging.debug('You have bliked, System time: %s', time.time())
except Exception, e:
        print("you have called blink stick to many times per second", e)