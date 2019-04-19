import struct, time
import multiprocessing
from multiprocessing import Process, Value


class Mpoint(Process):
    """
    You have to change access rights to file /dev/input/mice !!!
    sudo chmod 666 /dev/input/mice
    For using particular mouse use files
    /dev/input/mouse0
    /dev/input/mouse1

    """


    def __init__(self, shared_x, shared_y, measurement_delay=0, filename="/dev/input/mice"):
        Process.__init__(self)
        self.delta_x = shared_x
        self.delta_y = shared_y
        self.filename = filename
        self.measurement_delay = measurement_delay

    def calculate_mouse_relmov(self):
        with open(self.filename, "rb") as file:
            buf = file.read(3)
            self.delta_x.value, self.delta_y.value = struct.unpack("bb", buf[1:])

    def get_speed(self):
        return (self.delta_x.value, self.delta_y.value)

    def run(self):
        while True:
            self.calculate_mouse_relmov()
            #print ("X: {} Y: {}".format(self.delta_x.value, self.delta_y.value))
            time.sleep(self.measurement_delay)
