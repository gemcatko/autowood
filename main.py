import threading
import logging
import cv2
import numpy as np
import time
import os
import shlex
import subprocess
import multiprocessing
import re
from mpoint.mpoint import Mpoint
from pydarknet import Detector, Image
# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)



# DONE how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light => red led
# DONE Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3 => https://shop.blinkstick.com/
# DONE give objecs uniqe ID
# TODO calculate speed of objects integarde mpoint
# TODO Store image detections as thumbnails(small images) somewhere

def calculate_relative_coordinates(x, y, w, h):
    """
    Calculate coordinates in percentage relative to the screen
    :param x: center of detected object on x axis in pixels
    :param y: center of detected object on y axis in pixels
    :param w: width of detected object on x axis in pixels
    :param h: height of detected object on y axis in pixels
    :return: x_rel, y_rel, w_rel, h_rel, area_rel
    """
    x_rel = x / Xresolution
    y_rel = y / Yresolution
    w_rel = w / Xresolution
    h_rel = h / Yresolution
    area_rel = w_rel * h_rel
    return x_rel, y_rel, w_rel, h_rel, area_rel

def count_objects_in_frame(object_to_check):
    number_of_object_to_check = 0
    for cat, score, bounds in results:
        if cat.decode("utf-8") == object_to_check:
            number_of_object_to_check = number_of_object_to_check + 1
    return number_of_object_to_check

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

def faster_loop_trigerlist(qtrigerlist, shared_x, shared_y):
    """
    Loop for trigering small error in another process running faster then main loop in separate process it is interconnected with main process with trigerlist and shared_x, shared_y
    :param qtrigerlist, shared_x, shared_y:
    :return:nothing

    """
    while True:
        start_time_loop = time.time()
        try:
            #needed because qtrigerlist is not always having object inside
            trigerlist = qtrigerlist.get_nowait()
            logging.debug("trigerlist%s",trigerlist)

        except:
            # is setting speed of the loop in case 0.0005 it is 2000 times per second
            # except is not executed if qtrigerlist is have data
            time.sleep(0.0005)
        #Data format: id + 0.1, time_begining, id + 0.2, time_ending
        #trigerlist[(4.1, 1551555880.4178755, 4.2, 1551555880.576961), (11.1, 1551555884.1779869, 11.2, 1551555884.252769), (5.1, 1551555885.0371258, 5.2, 1551555885.2632303)]
        #fastTrigerlist:[(4.1, 1551555880.4184797), (4.2, 1551555880.577546), (11.1, 1551555884.1785562), (11.2, 1551555884.2533839), (5.1, 1551555885.0377772)]
        #
        #check for every object in trigerList
        #TODO osetrit vstup nemozu is velmi rychlo po sebe dve rozne chybi
        for id_begining, time_begining, id_ending, time_ending in trigerlist:
                # is trail running left direction ? using only Y
                if  shared_y.value < (speed_considered_trail_stoped*-1):
                    logging.debug('Trail is running left direction')
                    #do some action if needed

                # is trail running right direction ? using only Y
                if  shared_y.value < speed_considered_trail_stoped:
                    new_time_begining = time_begining + absolut_last_loop_duration
                    new_time_ending = time_ending + absolut_last_loop_duration
                    # get index of actual tuple in list
                    index_trigerlist = trigerlist.index((id_begining, time_begining, id_ending, time_ending))
                    # update trigerlist with newly calculated new_time_begining  new_time_ending
                    trigerlist[index_trigerlist] = id_begining, new_time_begining, id_ending, new_time_ending
                    #return updated values to current loop
                    time_begining,time_ending = new_time_begining, new_time_ending


                # if time for blink  of beginning of object (time.time() - time_begining) passed and object is not blinked yet (any(id_begining in sublist for sublist in fastTrigerList)) do:
                if time.time() - time_begining >= 0 and not (any(id_begining in sublist for sublist in fastTrigerList)):
                    fastTriger = id_begining, time_begining
                    # needed thus the function know which object was already blinked and which not
                    fastTrigerList.append(fastTriger)
                    blink_once()
                    logging.debug('id_begining blink_once() called for blink fastTrigerlist:%s', fastTrigerList)
                # if time for blink of beginning of object (time.time() - time_ending)  passed and object is not blinked yet (any(id_ending in sublist for sublist in fastTrigerList)) do:
                if time.time() - time_ending >= 0 and not (any(id_ending in sublist for sublist in fastTrigerList)):
                    fastTriger = id_ending, time_ending
                    # needed thus the function know which object was already blinked and which not
                    fastTrigerList.append(fastTriger)
                    blink_once()
                    logging.debug('id_ending blink_once() called for blink fastTrigerlist:%s', fastTrigerList)
                #TODO implement cleaning-deleting old objects from beginning offastTrigerList and trigerlist (the one which is inside this function )

        end_time_loop = time.time()
        #check for how long took execution the loop and log if it is too long
        last_loop_duration = end_time_loop - start_time_loop
        if (last_loop_duration) > 0.005:
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)
        # need to be on the end to improve measurement
        absolut_end_time_loop = time.time()
        absolut_last_loop_duration = absolut_end_time_loop - start_time_loop


def detect_object_4_cm(idresults, triger_margin, object_to_detect):
    """
    # is executed in main loop
    Vramci jednoho brazka prejdi vsetky cell phone co su vo vzdialenosti x<0,8 su 0.3 >=siroke  >= 0.05 a uz predtym si ich nevidel (triger list)
    For every detection in idresults check a every "cell phone" resp every detected object which is meets requirements of if loop
    The function should be executed once per every frame
    :param idresults:
    triger_margin:
    object_to_detect

    :return:
    """


    triger_margin = triger_margin
    for id, cat, score, bounds in idresults:
        x, y, w, h = bounds
        x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
        ##chnage format to utf-8### object_to_check ## how width ########### where is triger margin################### check if is not id.1 already in in triger list
        if cat.decode("utf-8") == object_to_detect and 0.9 >= w_rel >= 0.05 and (x_rel + (w_rel / 2)) > triger_margin and not (any((id + 0.1) in sublist for sublist in trigerlist)):
            logging.debug('sprav znacky zaciatok a koniec')
            # draw purple line on the screens it is just for visual control when call for blink ocure
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),(255, 0, 255), 10)
            # time of right blink
            time_begining = time.time() + delay + ((1 - (x_rel + (w_rel / 2))) * duration_1screen_s)
            # time of left blink
            time_ending = time_begining + ((1 - (x_rel - (w_rel / 2))) * duration_1screen_s)
            # add to trigerlist id.01, time when right blink and id.02 time left blink
            triger = id + 0.1, time_begining, id + 0.2, time_ending
            trigerlist.append(triger)
            # TODO implement cleaning-deleting old objects from beginning of the trigerlist
            # TODO or implement class
            try:
                #add to trigerlist id.01, time when right blink and id.02 time left blink to
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

            logging.debug('trigerlist:%s', trigerlist)

            pass
        else:
            pass
#TODO FINISH class
class Yolo_object():
    def __init__(self,id, cat, score, bounds):
        #co vychadza z jola [(1, b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (4, b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
        #centroid_id , detected_category, score, object_x ,y ,w, h
        #copy paste finktionality of  detect_object_4_cm
        self.id = id
        self.cat = cat
        self.score = score
        self.bounds = bounds
    #def update_cat_score_bounds (self):
    def update_cat_score_bouds(self):
        pass


        pass



def update_resutls_for_id(results):
    """
    loop over the tracked objects from Yolo34
    Reconstruct Yolo34 results with object id (data from centroid tracker) an put object ID to idresults list, like :
    class 'list'>[(b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
    class 'list'>[(1, b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (4, b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
    :param results from Yolo34:
    :return:idresults
    """
    global idresults
    idresults = []
    for cat, score, bounds in results:
        x, y, w, h = bounds
        # chyba_one_mark_small("cell phone", cat, score, x, y, w, h, )
        # loop over the tracked objects from Centroid
        for (objectID, centroid) in objects.items():
            # put centroid coordinates to cX and Cy variables
            cX, cY = centroid[0], centroid[1]
            # there is difference between yolo34 centroids and centroids calculated by centroid tracker,Centroid closer then 2 pixel are considired to matcg  TODO find where?
            if abs(cX - int(x)) <= 2 and abs(cY - int(y)) <= 2:
                # reconstruct detection list as from yolo34 including ID from centroid
                idresult = objectID, cat, score, bounds
                idresults.append(idresult)
    # print results with Id on screen
    # print(type(idresults), idresults
    return idresults


if __name__ == "__main__":

    #### VARS : ####

    # set resolution taken from webcam
    Xresolution = 1280
    Yresolution = 720
    cell_phone = []
    list_chyba = []
    # Used by pLoopTrigerlist  to communicate with main loop format is [(2.1, 1551338571.7396123, 2.2, 1551338571.9881353), (3.1, 1551338578.9405866, 3.2, 1551338579.1024451), (0.1, 1551338586.2836142, 0.2, 1551338586.4773874)]
    trigerlist = []
    idresults = []
    # Used by pLoopTrigerlist  to confirm object was marked  format is [(2.1, 1551338571.7396123), (2.2, 1551338571.9881353), (3.1, 1551338578.9405866), (3.2, 1551338579.1024451), (0.1, 1551338586.2836142), (0.2, 1551338586.4773874)]
    fastTrigerList = []
    field_of_view = 0.4  # field of view in m for camera
    x_norm_last = 0
    y_norm_last = 0
    speed_ms = 1  # MS Metere za Sekundu rychlost pasu pily
    w_of_one_picture_m = 0.4  # M Meter width og on screen in meter
    duration_1screen_s = w_of_one_picture_m / speed_ms  # time za kolko prejde jedna obrazovka pri speed_ms
    delay = 1  # time in s to delay marking, can be use to set distance of sensing camera from BliknStick.
    margin = 0.8  # place on screen where it is detecting objects,
    speed_considered_trail_stoped = 20
    # move_treshold = 0.05
    # set web cam properties width and height, working for USB for webcam
    cap = cv2.VideoCapture(1)
    cap.set(3, Xresolution)
    cap.set(4, Yresolution)

    # initialize our centroid tracker and frame dimensions
    ct = CentroidTracker(maxDisappeared=10)
    (H, W) = (None, None)

    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0,
                   bytes("cfg/coco.data", encoding="utf-8"), )
    # net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    # Start loop for blinking in separate process
    # initialize shared vars  for speed/movement x,y
    s_x = multiprocessing.Value('i', 0)
    s_y = multiprocessing.Value('i', 0)

    # create instance of Process subclass Mpoint and pass shared values vars
    mp = Mpoint(shared_x=s_x, shared_y=s_y)
    mp.start()

    qtrigerlist = multiprocessing.Queue()
    qtrigerlist.put(trigerlist)
    process1 = multiprocessing.Process(target=faster_loop_trigerlist, args=(qtrigerlist, s_x, s_y))
    process1.daemon = True
    process1.start()

    # MAIN LOOP
    while True:
        start_time = time.time()
        r, frame = cap.read()
        if r:
            # start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.5)
            del dark_frame
            # clean rect so it is clean an can be filled with new detection from frame\
            # later used in conversion_to_x1y1x2y2 . Conversion from yolo format to Centroid Format
            # rects are needed for centroid to work. They need to be cleared every time
            rects = []
            # enable below if you want to see detections from yolo34
            # print(type(results), results)
            # for every detection in results do use this loop for drawing
            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1,(255, 255, 0))
                # will show number of objects you are looking for at screens
                cv2.putText(frame, str(count_objects_in_frame("cell phone")),(int(Xresolution - 50), int(Yresolution - 50)), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (150, 150, 150))
                """
                convert from yolo format to cetroid format
                Yolo output:
                [(b'person', 0.9299755096435547, (363.68475341796875, 348.0577087402344, 252.04286193847656, 231.17266845703125)), (b'vase', 0.3197628855705261, (120.3013687133789, 405.3641357421875, 40.76551055908203, 32.07142639160156))]
                centroid input: 
                [array([145, 153, 248, 274]), array([113, 178, 148, 224])]
                """
                # bounding box for centroid
                box = np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
                # list of  bounding boxes for  centroid
                rects.append(box.astype("int"))

            # enable below if you want to see detections from yolo conversed to centroid format
            # print("rect", rects)
            # update our centroid tracker using the computed set of bounding box rectangles
            objects = ct.update(rects)
            # loop over the tracked objects from Centroids and put id on screens
            for (objectID, centroid) in objects.items():
                # draw both the ID of the object and the centroid of the
                # object on the output frame
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            detect_object_4_cm(update_resutls_for_id(results), margin, "cell phone")

            #TODO Here you can write yor own function which will be using class or another object oriented aproach, use
            # idresults variable. You cando whatever you like just do not change existing code. make Class when it see "Apple it give back true use idresults: "
            #TODO Detection for errors which are longer then XX(probably 15) cm


            #print("idresults:",type(idresults),idresults)
            #print("X:{} ".format(s_x.value))
            cv2.imshow("preview", frame)
        end_time = time.time()
        #print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)

        if k == 0xFF & ord("q"):
            break
