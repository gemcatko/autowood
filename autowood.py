from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/automateit/Projects/darknet-alexeyAB/darknet')
import darknet
from multiprocessing import Process, Value, Array, Manager
from multiprocessing import shared_memory
import numpy as np
manager = Manager()
manager_detections = manager.list()
#a = np.array([])
shm = shared_memory.SharedMemory(create=True, size=6520800, name='psm_c013ddb7')
shm_image = np.ndarray((416,416,3), dtype=np.uint8, buffer=shm.buf)
#b[:] = a[:]  # Copy the original data into shared memory
#print(b,shm.name)
#print(type(detections))

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    return img


netMain = None
metaMain = None
altNames = None

def YOLO():

    global metaMain, netMain, altNames ,manager_detections
    configPath = "./x64/Release/data/2019_12_22_yolo-obj_v3.cfg"
    weightPath = "./backup/2019_12_22_yolo-obj_v3_18000.weights"
    metaPath = "./x64/Release/data/obj.data"
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("test.mp4")
    cap = cv2.VideoCapture("x64/Release/data/test_01-40_03-17_1440x1080.mp4")
    cap.set(3, 1280)
    cap.set(4, 720)
    out = cv2.VideoWriter(
        "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10.0,
        (darknet.network_width(netMain), darknet.network_height(netMain)))
    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                    darknet.network_height(netMain),3)
    while True:
        prev_time = time.time()
        ret, frame_read = cap.read()
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
        #arr = Array('i', range(10))
        #detections= darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
        del manager_detections[:]                       #need to be cleared every iterration
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
        manager_detections.append(detections)
        image = cvDrawBoxes(detections, frame_resized)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        shm_image[:] = image[:]
        #mpimage = Array ('d', image)
        #print("a",type(image))
        #print(image)
        cv2.imshow('Demo', image)
        #print(image.dtype)

        cv2.waitKey(3)
    cap.release()
    out.release()

def second_visualization():
    existing_shm = shared_memory.SharedMemory(name='psm_c013ddb7')
    image = np.ndarray((416,416,3), dtype=np.uint8, buffer=existing_shm.buf)
    while True:
        #print (manager_detections)
        #print(type(c))
        cv2.imshow('second_visualization', image)
        cv2.waitKey(3)
        #time.sleep(1)



process10 = Process(target=second_visualization )
process10.daemon = True
process10.start()


if __name__ == "__main__":
    YOLO()
