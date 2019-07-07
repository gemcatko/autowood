# need to run this code in python 2.7
#  add blink stick as root: sudo blinkstick --add-udev-rule
from blinkstick import blinkstick
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def blink():
    bstick.set_color(channel=0, index=0, name="red")
    bstick.set_color(channel=0, index=1, name="red")
    # bstick.set_color(channel=0, index=2, name="red")
    # bstick.set_color(channel=0, index=3, name="red")
    time.sleep(.01)
    bstick.set_color(channel=0, index=0, name="")
    bstick.set_color(channel=0, index=1, name="")
    # bstick.set_color(channel=0, index=2, name="")
    # bstick.set_color(channel=0, index=3, name="")

try:
    for bstick in blinkstick.find_all():
        start_time = time.time()
        blink()
        end_time = time.time()
        #print("You have bliked, Elapsed Time of the Blink:", end_time - start_time)
        #logging.debug('You have bliked, Elapsed Time of the Blink: %s', end_time - start_time)
        logging.debug('You have bliked, System time: %s', time.time())
except Exception as e:
    print(e)
    print(e,"you have called blink stick to many times per second")

time.sleep(0.05)
try:
    for bstick in blinkstick.find_all():
        start_time = time.time()
        blink()
        end_time = time.time()
        #print("You have bliked, Elapsed Time of the Blink:", end_time - start_time)
        #logging.debug('You have bliked, Elapsed Time of the Blink: %s', end_time - start_time)
        logging.debug('You have bliked, System time: %s', time.time())
except Exception as e:
    print(e)
    print(e,"you have called blink stick to many times per second")