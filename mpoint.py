import struct, os, time
import multiprocessing
from multiprocessing import Process, Value


class Mpoint(Process):


    def __init__(self, shared_x, shared_y, measurement_delay=0, filename="/dev/input/mice"):
        Process.__init__(self)
        self.delta_x = shared_x
        self.delta_y = shared_y
        self.filename = filename
        self.measurement_delay = measurement_delay

    def calculate_mouse_relmov(self):
        with open(self.filename) as file:
            buf = file.read(3)
            self.delta_x.value, self.delta_y.value = struct.unpack("bb", buf[1:])

    def get_speed(self):
        return (self.delta_x.value, self.delta_y.value)

    def run(self):
        while True:
            self.calculate_mouse_relmov()
            # print ("X: {} Y: {}".format(self.delta_x.value, self.delta_y.value))
            time.sleep(self.measurement_delay)



if __name__ == '__main__':

    #initialize shared vars  for speed/movement x,y
    s_x = multiprocessing.Value('i', 0)
    s_y = multiprocessing.Value('i', 0)

    #create instance of Process subclass Mpoint and pass shared values vars
    mp = Mpoint(shared_x=s_x, shared_y=s_y)
    mp.start()

    # for i in range(10):
    #      print("X:{} ".format(s_x.value))
    #      time.sleep(1)
