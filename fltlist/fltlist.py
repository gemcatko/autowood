import struct, time
from multiprocessing import Process, Value


class fltlist(Process):
    """
    Docu
    """
    def __init__(self, values_to_triger):
        Process.__init__(self)
        self.values_to_triger = values_to_triger

    def do_something(self):
        #print("values_to_triger:",self.values_to_triger.get_nowait())
            start_time_loop = time.time()
            try:
                # needed because qtrigerlist is not always having object inside
                print("values_to_triger:", self.values_to_triger.get_nowait())

            except:
                # is setting speed of the loop in case 0.0005 it is 2000 times per second
                # except is not executed if qtrigerlist is have data
                time.sleep(0.0005)


    def run(self):
        while True:
            self.do_something()
            #print ("X: {} Y: {}".format(self.delta_x.value, self.delta_y.value))
            fltlist.do_something(self)
