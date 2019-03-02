import threading
import logging
from pydarknet import Detector, Image
import cv2
import numpy as np
import time
import os
import shlex, subprocess
import multiprocessing
from mpoint.mpoint import Mpoint
# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

# set resolution taken from webcam
Xresolution = 640
Yresolution = 480
cell_phone = []
list_chyba = []
#Used by pLoopTrigerlist  to communicate with main loop format is [(2.1, 1551338571.7396123, 2.2, 1551338571.9881353), (3.1, 1551338578.9405866, 3.2, 1551338579.1024451), (0.1, 1551338586.2836142, 0.2, 1551338586.4773874)]
trigerlist = []
idresults = []
# Used by pLoopTrigerlist  to confirm object was marked  format is [(2.1, 1551338571.7396123), (2.2, 1551338571.9881353), (3.1, 1551338578.9405866), (3.2, 1551338579.1024451), (0.1, 1551338586.2836142), (0.2, 1551338586.4773874)]
fastTrigerList =[]
field_of_view = 0, 40  # field of view in m for camera
x_norm_last = 0
y_norm_last = 0
speed_ms = 1  # MS Metere za Sekundu rychlost pasu pily
w_of_one_picture_m = 0.4  # M Meter width og on screen in meter
duration_1screen_s = w_of_one_picture_m / speed_ms  # time za kolko prejde jedna obrazovka pri speed_ms
delay = 1  # time in s to delay marking, can be use to set distance of sensing camera from BliknStick.
margin = 0.8 # place on screen where it is detecting objects,
# move_treshold = 0.05
# set web cam properties width and height, working for USB for webcam
cap = cv2.VideoCapture(0)
cap.set(3, Xresolution)
cap.set(4, Yresolution)


# initialize our centroid tracker and frame dimensions
ct = CentroidTracker(maxDisappeared=5)
(H, W) = (None, None)


# DONE how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light => red led
# DONE Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3 => https://shop.blinkstick.com/
# DONE give objecs uniqe ID
# TODO calculate speed of objects integarde mpoint
# TODO Show found erros with ID on separate screen

def calculate_volume_norm(x, y, w, h):
    """
    Calculate coordinates in percentage relative to the screen
    :param x: center of detected object on x axis in pixels
    :param y: center of detected object on y axis in pixels
    :param w: width of detected object on x axis in pixels
    :param h: hight of detected object on y axis in pixels
    :return: x_norm, y_norm, w_norm, h_norm, volume_norm
    """
    x_norm = x / Xresolution
    y_norm = y / Yresolution
    w_norm = w / Xresolution
    h_norm = h / Yresolution
    volume_norm = w_norm * h_norm
    return x_norm, y_norm, w_norm, h_norm, volume_norm

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

def BlinkOnce():
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

def pLoopTrigerlist(qtrigerlist,shared_x, shared_y):
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
            time.sleep(0.0005)
        #Data format: id + 0.1, time_begining, id + 0.2, time_ending
        #trigerlist[(4.1, 1551555880.4178755, 4.2, 1551555880.576961), (11.1, 1551555884.1779869, 11.2, 1551555884.252769), (5.1, 1551555885.0371258, 5.2, 1551555885.2632303)]
        #fastTrigerlist:[(4.1, 1551555880.4184797), (4.2, 1551555880.577546), (11.1, 1551555884.1785562), (11.2, 1551555884.2533839), (5.1, 1551555885.0377772)]
        #
        #check for every object in trigerList
        index = 0
        for id_begining, time_begining, id_ending, time_ending in trigerlist:
                if shared_x.value + shared_y.value < 20:
                    time_begining = time_begining + last_loop_duration
                    time_ending = time_ending + last_loop_duration
                    trigerlist[index]


                if time.time() - time_begining >= 0 and not (any(id_begining in sublist for sublist in fastTrigerList)):
                    fastTriger = id_begining, time_begining
                    fastTrigerList.append(fastTriger)
                    logging.debug('Done fastTrigerlist:%s', fastTrigerList)
                    BlinkOnce()

                if time.time() - time_ending >= 0 and not (any(id_ending in sublist for sublist in fastTrigerList)):
                    fastTriger = id_ending, time_ending
                    fastTrigerList.append(fastTriger)
                    logging.debug('done fastTrigerlist:%s', fastTrigerList)
                    BlinkOnce()
                index = index +1

        end_time_loop = time.time()
        #check for long duration of loop if is not too long
        last_loop_duration = end_time_loop - start_time_loop

        if (last_loop_duration) > 0.005:
            # print("loopTrigerlistThread:", end_time_loop - start_time_loop)
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)

def error4Cm(idresults):
    """
    # is executed in main loop
    Vramci jednoho brazka prejdi vsetky cell phone co su vo vzdialenosti x<0,8 su 0.3 >=siroke  >= 0.05 a uz predtym si ich nevidel (triger list)
    :param idresults:
    :return:
    """
    for id, cat, score, bounds in idresults:
        x, y, w, h = bounds
        x_norm, y_norm, w_norm, h_norm, volume_norm = calculate_volume_norm(x, y, w, h)
        if cat.decode("utf-8") == "cell phone" and 0.9 >= w_norm >= 0.05 and (x_norm + (w_norm / 2)) > margin and not (any((id + 0.1) in sublist for sublist in trigerlist)):
            logging.debug('sprav znacku zaciatok koniec')
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),(255, 0, 255), 10)
            # time of right bounding box
            time_begining = time.time() + delay + ((1 - (x_norm + (w_norm / 2))) * duration_1screen_s)
            time_ending = time_begining + ((1 - (x_norm - (w_norm / 2))) * duration_1screen_s)
            # add to triger list Id, time when beginning mark, time when ending mark
            triger = id + 0.1, time_begining, id + 0.2, time_ending
            trigerlist.append(triger)
            try:
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

            logging.debug('trigerlist:%s', trigerlist)

            pass
        else:
            pass

def updateResutlsForId(results):
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
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0,
                   bytes("cfg/coco.data", encoding="utf-8"), )
    # net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    #Start loop for blinking in separate process
    #initialize shared vars  for speed/movement x,y
    s_x = multiprocessing.Value('i', 0)
    s_y = multiprocessing.Value('i', 0)

    #create instance of Process subclass Mpoint and pass shared values vars
    mp = Mpoint(shared_x=s_x, shared_y=s_y)
    mp.start()

    qtrigerlist = multiprocessing.Queue()
    qtrigerlist.put(trigerlist)
    process1 = multiprocessing.Process(target=pLoopTrigerlist, args=(qtrigerlist, s_x, s_y))
    process1.daemon = True
    process1.start()


    while True:
        start_time = time.time()
        r, frame = cap.read()
        if r:
            #start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.5)
            del dark_frame
            # clean rect so it is clean an can be filled with new detecttion from frame later used in conversion_to_x1y1x2y2 . Conversion from yolo format to Centroid Format
            # rects are needed for neded to work with centroid thy need to be cleared every time
            rects = []
            # enable below if you want to see detections from yolo34
            # print(type(results), results)
            # for every detection in results do use thi loop for drawing
            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1,(255, 255, 0))
                #will show number of objects you are looking for at screens
                cv2.putText(frame, str(count_objects_in_frame("cell phone")),(int(Xresolution - 50), int(Yresolution - 50)), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (150, 150, 150))
                """
                converse data from yolo format to cetroid format
                [(b'person', 0.9299755096435547, (363.68475341796875, 348.0577087402344, 252.04286193847656, 231.17266845703125)), (b'vase', 0.3197628855705261, (120.3013687133789, 405.3641357421875, 40.76551055908203, 32.07142639160156))]
                [array([145, 153, 248, 274]), array([113, 178, 148, 224])]
                """
                box = np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
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
            error4Cm(updateResutlsForId(results))

            #TODO Here you can write yor own function which will be using class or another object oriented aproach, use
            # idresults variable. You can whatever you like just do not change existing code. make Class when it see "Apple it give back true use idresults: "

            #print("idresults:",type(idresults),idresults)
            #print("X:{} ".format(s_x.value))
            cv2.imshow("preview", frame)
        end_time = time.time()
        #print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)

        if k == 0xFF & ord("q"):
            break
