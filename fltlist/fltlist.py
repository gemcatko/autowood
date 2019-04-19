import struct, time
from multiprocessing import Process, Value
import threading
import subprocess
import logging


class BlinkStickThread(threading.Thread):
    def run(self):
        '''Starting blinkStick to blink once in Separate Thread'''
        subprocess.Popen(["python2", "BlinkStick.py"])
        pass

def blink_once():
    """
    Is using threading for blinking once, create tread for BlinkStick.py (python2.7)

    """
    try:
        # os.system('python2 BlinkStick.py') # najpomalsie
        # subprocess.Popen(["python2", "BlinkStick.py"]) #troska ryclesie
        thread = BlinkStickThread()
        thread.daemon = True
        thread.start()
    except:
        print("BlinkStickOnce exception occurred ")
    pass

class fltlist(Process):
    """
    Docu
    """
    def __init__(self, values_to_triger,shared_x,shared_y):
        Process.__init__(self)
        self.values_to_triger = values_to_triger
        self.s_x = shared_x
        self.s_y = shared_y
        self.speed_considered_trail_stoped = 20
        self.fastTrigerList = []
        self.absolut_last_loop_durationn = 0
        self.trigerlist = []

    def faster_loop_trigerlist(self):
        """
        Loop for trigering small error in another process running faster then main loop in separate process it is interconnected with main process with trigerlist and shared_x, shared_y
        :param values_to_triger, shared_x, shared_y:
        :return:nothing

        """
        start_time_loop = time.time()
        print(self.s_y)
        try:
            # needed because values_to_triger is not always having object inside
            self.trigerlist = self.values_to_triger.get_nowait()
            logging.debug("trigerlist%s", self.trigerlist)

        except:
            # is setting speed of the loop in case 0.0005 it is 2000 times per second
            # except is not executed if values_to_triger is have data
            time.sleep(0.0005)
        # Data format: id + 0.1, time_begining, id + 0.2, time_ending
        # trigerlist[(4.1, 1551555880.4178755, 4.2, 1551555880.576961), (11.1, 1551555884.1779869, 11.2, 1551555884.252769), (5.1, 1551555885.0371258, 5.2, 1551555885.2632303)]
        # fastTrigerlist:[(4.1, 1551555880.4184797), (4.2, 1551555880.577546), (11.1, 1551555884.1785562), (11.2, 1551555884.2533839), (5.1, 1551555885.0377772)]
        #
        # check for every object in trigerList
        # TODO osetrit vstup nemozu is velmi rychlo po sebe dve rozne chybi
        for id_begining, time_begining, id_ending, time_ending in self.trigerlist:

            # is trail running left direction ? using only Y
            if self.s_y.value < (self.speed_considered_trail_stoped * -1):
                logging.debug('Trail is running left direction')
                # do some action if needed

            # is trail running right direction ? using only Y
            if self.s_y.value < self.speed_considered_trail_stoped:
                new_time_begining = time_begining + self.absolut_last_loop_durationn
                new_time_ending = time_ending + self.absolut_last_loop_durationn
                # get index of actual tuple in list
                index_trigerlist = self.trigerlist.index((id_begining, time_begining, id_ending, time_ending))
                # update trigerlist with newly calculated new_time_begining  new_time_ending
                self.trigerlist[index_trigerlist] = id_begining, new_time_begining, id_ending, new_time_ending
                # return updated values to current loop
                time_begining, time_ending = new_time_begining, new_time_ending

            # if time for blink  of beginning of object (time.time() - time_begining) passed and object is not blinked yet (any(id_begining in sublist for sublist in fastTrigerList)) do:
            if time.time() - time_begining >= 0 and not (any(id_begining in sublist for sublist in self.fastTrigerList)):
                fastTriger = id_begining, time_begining
                # needed thus the function know which object was already blinked and which not
                self.fastTrigerList.append(fastTriger)
                blink_once()
                logging.debug('id_begining blink_once() called for blink fastTrigerlist:%s', self.fastTrigerList)
            # if time for blink of beginning of object (time.time() - time_ending)  passed and object is not blinked yet (any(id_ending in sublist for sublist in fastTrigerList)) do:
            if time.time() - time_ending >= 0 and not (any(id_ending in sublist for sublist in self.fastTrigerList)):
                fastTriger = id_ending, time_ending
                # needed thus the function know which object was already blinked and which not
                self.fastTrigerList.append(fastTriger)
                blink_once()
                logging.debug('id_ending blink_once() called for blink fastTrigerlist:%s', self.fastTrigerList)
            # TODO implement cleaning-deleting old objects from beginning offastTrigerList and trigerlist (the one which is inside this function )

        end_time_loop = time.time()
        # check for how long took execution the loop and log if it is too long
        last_loop_duration = end_time_loop - start_time_loop
        if (last_loop_duration) > 0.010:
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)
        # print(translate(shared_y.value, leftMin, leftMax, rightMin, rightMax))
        # need to be on the end to improve measurement
        absolut_end_time_loop = time.time()
        absolut_last_loop_durationn = absolut_end_time_loop - start_time_loop


    def do_something(self):
            try:
                # needed because qtrigerlist is not always having object inside
                print("values_to_triger:", self.values_to_triger.get_nowait())
            except:
                # is setting speed of the loop in case 0.0005 it is 2000 times per second
                # except is not executed if qtrigerlist is have data
                time.sleep(0.005)
            #print(self.s_x)
            print(self.s_y)


    def run(self):
        while True:
            #self.do_something()
            self.faster_loop_trigerlist()
            #print ("X: {} Y: {}".format(self.delta_x.value, self.delta_y.value))

