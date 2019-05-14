import struct
import time
from multiprocessing import Process, Value, Queue



class Mpoint(Process):
    """
    You have to change access rights to file /dev/input/mice !!!
    sudo chmod 666 /dev/input/mice
    For using particular mouse use files
    /dev/input/mouse0
    /dev/input/mouse1

    """

    def __init__(self, shared_x, shared_y, shared_d_x, shared_d_y, shared_queue, loop_delay=0, filename="/dev/input/mice"):
        Process.__init__(self)
        self.delta_x = shared_x
        self.delta_y = shared_y
        self.distance_x = shared_d_x
        self.distance_y = shared_d_y
        self.filename = filename
        self._loop_delay = loop_delay
        self._shared_queue = shared_queue

    def update_mouse_movement(self):
        try:
            xy = self._shared_queue.get(block=False)
            self.delta_x.value, self.delta_y.value = xy
            self.distance_x.value += self.delta_x.value
            self.distance_y.value += self.delta_y.value
        except:
            self.delta_x.value = 0
            self.delta_y.value = 0

    def get_speed(self):
        return self.delta_x.value, self.delta_y.value
    
    def get_distance(self):
        return self.distance_x.value, self.distance_y.value

    def run(self):
        while True:
            self.update_mouse_movement()
            time.sleep(self._loop_delay)

def feed_queue(shared_queue, filename="/dev/input/mice"):
    file = filename
    q = shared_queue
    while True:
        with open(file, "rb", 0) as f:
            buf = f.read(3)
            xy = struct.unpack("bb", buf[1:])
            q.put(xy)


            
if __name__ == '__main__':

    #initialize shared vars  for delta movement x,y and distance x,y
    s_x = Value('i', 0)
    s_y = Value('i', 0)
    s_distance_x = Value('l', 0)
    s_distance_y = Value('l', 0)
    s_queue = Queue()
    
    #create process to feed queue
    p = Process(target=feed_queue, args=(s_queue, "/dev/input/mice"))
    p.start()

    #create instance of Process subclass Mpoint and pass shared values vars
    m_point = Mpoint(shared_x=s_x, shared_y=s_y, shared_d_x=s_distance_x, shared_d_y=s_distance_y, shared_queue=s_queue, loop_delay=0.01, filename="/dev/input/mice" )
    m_point.start()

    while True:
        # print("X: {} Y: {} D_x: {} D_y: {}".format(
        #         s_x.value, s_y.value, s_distance_x.value, s_distance_y.value))

        print("Distance {}".format(m_point.get_distance()))
        time.sleep(0.01)   
