import threading

from pydarknet import Detector, Image

import cv2
import numpy as np
import time
import os
import shlex, subprocess

####################################################
# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker

# set resolution taken from webcam
Xresolution = 1280
Yresolution = 720
cell_phone = []
list_chyba = []
trigerlist = []
field_of_view = 0,40  # field of view in m for camera
x_norm_last = 0
y_norm_last = 0
speed_ms = 2   #MS Metere za Sekundu rychlost pasu pily
w_of_one_picture_m = 0.4 # M Meter width og on screen in meter
duration_1screen_s = w_of_one_picture_m / speed_ms # time za kolko prejde jedna obrazovka pri speed_ms
delay = 1
#move_treshold = 0.05
# set web cam properties width and height, working for USB for webcam
cap = cv2.VideoCapture(0)
cap.set(3, Xresolution)
cap.set(4, Yresolution)

# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)


# DONE how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light => red led
# DONE Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3 => https://shop.blinkstick.com/
# DONE give objecs uniqe ID
# TODO calculate speed of objects
# TODO Show found erros with ID on separate screen

def chyba_one_mark_small(object_to_check, cat, score, x, y, w, h, ):
    """
    :param cat:
    :param score:
    :param x: center of detected object on x axis in pixels
    :param y: center of detected object on y axis in pixels
    :param w: width of detected object on x axis in pixels
    :param h: hight of detected object on y axis in pixels
    Experimental function which is drawing red and orange line around desired object.
    It is also drawing magenta line on 0.9 of screen => if object is touching almost edge of the screen
    :return:
    """
    # giving category do utf-8 so is can compare it human language
    x_norm, y_norm, w_norm, h_norm, volume_norm = calculate_volume_norm(x, y, w, h)
    # W_norm is used_for triger how big error to detect 1 is one screen 0.5 is alf screen on x axis . If 0.5 it si detecting object smoler then 0.5 of screen
    if cat.decode("utf-8") == object_to_check and w_norm <= 0.5:
        # left line from camera view at object green
        cv2.line(frame, (int(x - w / 2), int(y - h / 2)), (int(x - w / 2), int(y + h / 2)), (0, 128, 0), 10, 10)
        # right line_from camera view at object orange
        cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (0, 128, 255), 10, 10)
        # test na zaciatok vychadzania detekovane objektu zo zaberu. Test v 90% obrazovej plochy
        if (x_norm + w_norm / 2) > 0.90:
            print("sprav znacku zaciatok koniec ")
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 255), 10)
            pass
    else:
        pass

def error_small(id,object_to_check, cat, score, x, y, w, h,):
    pass


def calculate_volume_norm(x, y, w, h):
    """
    Calculate coordinates in percentage
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
        '''Start your thread here'''
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
        print("BlinkStick exception occurred ")
    pass



if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0,
                   bytes("cfg/coco.data", encoding="utf-8"), )
    # net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    while True:
        r, frame = cap.read()
        if r:
            start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.5)
            del dark_frame
            # clean rect so it is clean an can be filled with new detecttion from frame later used in conversion_to_x1y1x2y2
            rects = []
            resultsWithID = []
            # enable below if you want to see detections from yolo34
            #print(type(results), results)

            # for every detection in results do
            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 0))
                cv2.putText(frame, str(count_objects_in_frame("cell phone")),
                            (int(Xresolution - 50), int(Yresolution - 50)), cv2.FONT_HERSHEY_COMPLEX, 1,
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
            # loop over the tracked objects from Centroids
            for (objectID, centroid) in objects.items():
                # draw both the ID of the object and the centroid of the
                # object on the output frame
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            # Reconstruct Yolo34 results with object id (data from centroid tracker) an put object ID to idresults list, like :
            # class 'list'>[(b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
            # class 'list'>[(1, b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (4, b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]

            idresults = []
            # loop over the tracked objects from Yolo34
            for cat, score, bounds in results:
                x, y, w, h = bounds
                #chyba_one_mark_small("cell phone", cat, score, x, y, w, h, )
                # loop over the tracked objects from Centroid
                for (objectID, centroid) in objects.items():
                    # put centroid coordinates to cX and Cy variables
                    cX, cY = centroid[0], centroid[1]
                    # there is difference between yolo34 centroids and centroids calculated by centroid tracker,Centroid closer then 2 pixel are considired to matcg  TODO find where?
                    if abs(cX - int(x)) <= 2 and abs(cY - int(y)) <= 2:
                        # reconstruct detection list as from yolo34 including ID from centroid
                        idresult = objectID, cat, score, bounds
                        idresults.append(idresult)

            #print results with Id on screen
            #print(type(idresults), idresults)
            #BlinkOnce()
            #end_time = time.time()
            #print("Elapsed Time:",end_time-start_time)

            #vramci jednoho brazka prejdi vsetky cell phone co su vo vzdialenosti x<0,8 su 0.3 >=siroke  >= 0.05 a uz predtym si ich nevidel (triger list)
            for id, cat, score, bounds in idresults:
                x, y, w, h = bounds
                x_norm, y_norm, w_norm, h_norm, volume_norm = calculate_volume_norm(x, y, w, h)
                if cat.decode("utf-8") == "cell phone" and 0.3 >= w_norm >= 0.05 and (x_norm + (w_norm / 2)) > 0.80 and not (any(id in sublist for sublist in trigerlist)):

                    print("sprav znacku zaciatok koniec")
                    cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)),
                                 (255, 0, 255), 10)
                    time_begining = time.time() + delay + ((1-(x_norm + (w_norm/2)))*duration_1screen_s)
                    time_ending = time_begining + ((1-(x_norm - (w_norm/2)))*duration_1screen_s)
                    print (time_ending -time_begining)
                    triger = id, time_begining, time_ending
                    trigerlist.append(triger)
                    print ("trigerlist:",trigerlist)
                    pass
                else:
                    pass

            cv2.imshow("preview", frame)


        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
