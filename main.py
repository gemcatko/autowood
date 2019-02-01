import time
import traceback
import sys
from pydarknet import Detector, Image
import cv2
import logging
import weakref
####################################################
from pyimagesearch.centroidtracker import CentroidTracker
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

Xresolution = 640
Yresolution = 480
cell_phone = []
list_chyba = []
field_of_view = 40 #field of view in cm for camera
x_norm_last = 0
y_norm_last = 0
move_treshold = 0.05
idd= 0

# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)

#TODO how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light
#TODO Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3
#TODO give objecs uniqe ID
#TODO calculate speed of objects
#TODO Show found erros with ID on separate screen


def chyba_one_mark_small(cat, score, x, y, w, h, ):
    catdecoded = cat.decode("utf-8")
    x_norm, y_norm, w_norm, h_norm,volume_norm = calculate_volume_norm(x, y, w, h)
    #W_norm is used_for triger how big error to detect
    if catdecoded == "cell phone" and w_norm <= 1:
        #left line from camera view at object green
        cv2.line(frame, (int(x-w/2),int(y-h/2)),(int(x-w/2),int(y+h/2)),(0,128,0),10,10)
        #right line_from camera view at object orange
        cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(0,128,255),10,10)
        #test na zaciatok vychadzania detekovane objektu zo zaberu. Test v 90% obrazovej plochy
        if (x_norm + w_norm/2) > 0.90:
            print("sprav znacku zaciatok koniec ")
            cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,255),10)
            pass
    else:
        pass

def is_near_by_object (cat, score, x, y, w, h):
    global x_norm_last
    global y_norm_last

    x_norm = x / Xresolution
    y_norm = y / Yresolution

    if (abs(x_norm - x_norm_last ) <= 0.05) and (abs(y_norm - y_norm_last) <= 0.05):
        ("Je to ten isty object:   dif:", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last), x_norm,x_norm_last )
        pass
    if (abs(x_norm - x_norm_last ) > 0.05) or (abs(y_norm - y_norm_last) > 0.05):
        ("nie je  ten isty objekt  ", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last), x_norm,x_norm_last)
        pass

    x_norm_last = x_norm
    y_norm_last = y_norm
    pass

def calculate_volume_norm(x, y, w, h):
    x_norm = x / Xresolution
    y_norm = y / Yresolution
    w_norm = w / Xresolution
    h_norm = h / Yresolution
    volume_norm = w_norm * h_norm
    return x_norm, y_norm, w_norm, h_norm,volume_norm

def count_objects_in_frame(object_to_check):
    number_of_object_to_check = 0
    for cat, score, bounds in results:
        if cat.decode("utf-8") == object_to_check:
            number_of_object_to_check = number_of_object_to_check + 1
    return  number_of_object_to_check


def conversion_to_x1y1x2y2(x, y, w, h):
     #box = np.array([x, y, w, h])
     box = np.array([x-w/2, y-h/2, x+w/2, y+h/2])
     rects.append(box.astype("int"))

if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0, bytes("cfg/coco.data", encoding="utf-8"), )
    #net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    cap = cv2.VideoCapture(0)

    while True:
        r, frame = cap.read()
        if r:
            #start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            #This are the function parameters of detect:
            #def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.5)
            del dark_frame
            rects = []
            print(type(results), results)
            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                chyba_one_mark_small(cat, score, x, y, w, h, )
                cv2.putText(frame, str(count_objects_in_frame("cell phone")), (int(Xresolution - 50), int(Yresolution - 50)), cv2.FONT_HERSHEY_COMPLEX, 1, (150, 150,150))
                conversion_to_x1y1x2y2(x,y,w,h)
            print("rect", rects)

            objects = ct.update(rects)

            # loop over the tracked objects
            for (objectID, centroid) in objects.items():
                # draw both the ID of the object and the centroid of the
                # object on the output frame
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            cv2.imshow("preview", frame)
            #print(results)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break