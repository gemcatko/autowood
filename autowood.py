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
from pyimagesearch.centroidtracker import CentroidTracker
from dev_env_vars import *

shm = shared_memory.SharedMemory(create=True, size=6520800, name='psm_c013ddb7')
shm_image = np.ndarray((416,416,3), dtype=np.uint8, buffer=shm.buf)


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
        #print(detections)
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

def convert_bounding_boxes_form_Yolo_Centroid_format(results):
    # clean rect so it is clean an can be filled with new detection from frame\
    # later used in conversion_to_x1y1x2y2 . Conversion from yolo format to Centroid Format
    # rects are needed for centroid to work. They need to be cleared every time
    rects = []

    #if len(results) <= 1: # check if array is not empty, for prevention of crashing in later stage
    #    return []
    try:
        for oneresult in results:   #unpacking
            for cat, score, bounds in oneresult:    # unpacking
                x, y, w, h = bounds
                """
                convert from yolo format to cetroid format
                Yolo output:
                [(b'person', 0.9299755096435547, (363.68475341796875, 348.0577087402344, 252.04286193847656, 231.17266845703125)), (b'vase', 0.3197628855705261, (120.3013687133789, 405.3641357421875, 40.76551055908203, 32.07142639160156))]
                [(b'mark', 0.9893345236778259, (86.11815643310547, 231.90643310546875, 22.100597381591797, 54.182857513427734)), (b'mark', 0.8441593050956726, (225.28382873535156, 234.5716094970703, 14.333066940307617, 53.428749084472656)), (b'edge', 0.6000953316688538, (377.6446838378906, 254.71759033203125, 8.562969207763672, 18.379894256591797)), (b'edge', 0.5561915636062622, (388.4414367675781, 211.0662841796875, 10.678437232971191, 15.206807136535645)), (b'edge', 0.44139474630355835, (377.0844421386719, 150.8873748779297, 9.128596305847168, 18.9124755859375)), (b'crack', 0.28897273540496826, (268.6462707519531, 169.00457763671875, 253.9573516845703, 34.764007568359375))]]
                """
                # calculate bounding box for every object from YOLO for centroid purposes
                box = np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
                # append to list of  bounding boxes for centroid
                rects.append(box.astype("int"))
        return rects
    except:
        print("There was a problem with extrection from result:")
        return rects

def second_visualization(net_width,net_heigth):
    existing_shm = shared_memory.SharedMemory(name='psm_c013ddb7')
    image = np.ndarray((net_width,net_heigth,3), dtype=np.uint8, buffer=existing_shm.buf)
    ct = CentroidTracker(maxDisappeared=20)
    while True:

        cv2.imshow('second_visualization', image)
        results = manager_detections
        #print(results)
        rects = convert_bounding_boxes_form_Yolo_Centroid_format(results)
        #print(rects)
        ct_objects = ct.update(rects)
        #idresults = update_resutls_for_id(results)
        #orderedDict([(0, array([1003, 476])), (1, array([271, 612])), (2, array([987, 751])), (3, array([327, 611])),(4, array([570, 608])), (5, array([383, 617]))])
        cv2.waitKey(3)
        #time.sleep(1)

class YObject:
    # use for creating objects from Yolo.
    # def __init__(self, centroid_id, category, score, bounds):
    def __init__(self, id, category, score, bounds, s_distance):
        # copy paste functionality of  detect_object_4_c
        self.id = id
        self.category = category
        self.score = score
        self.bounds = bounds
        self.position_on_trail = s_distance
        self.is_detected_by_detector = True
        self.ignore = False
        self.is_picture_saved = False
        self.ready_for_blink_start = False
        self.ready_for_blink_end = False

    def draw_object_bb_and_class(self):
        """
        Draw objects name to CV2 frame  using cv2 only if  detected by detector
        :return: none
        """
        if self.is_detected_by_detector or id in (item for sublist in idresults for item in sublist):
            x, y, w, h = self.bounds
            # draw what is name of the object
            cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), blue, 4)
            cv2.putText(frame, str(self.category), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))

    def draw_object_score(self):
        """
        Draw objects score to CV2 frame  using cv2 only if still detected by detector
        :return: none
        """
        if self.is_detected_by_detector or id in (item for sublist in idresults for item in sublist):
            x, y, w, h = self.bounds
            cv2.putText(frame, str(round(self.score, 2)), (int(x - 20), int(y - 20)), cv2.FONT_HERSHEY_COMPLEX, 1, azzure)

    def draw_object_id(self):
        """
        Drae object Id to CV2 frame only if still detected by detector
        :return:
        """
        if self.is_detected_by_detector or id in (item for sublist in idresults for item in sublist):
            x, y, w, h = self.bounds
            cv2.putText(frame, str(self.id), (int(x - 30), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (magenta))

    def draw_object_position_on_trail(self):
        """
        Drae object Id to CV2 frame only if still detected by detector
        :return:
        """
        if self.is_detected_by_detector or id in (item for sublist in idresults for item in sublist):
            x, y, w, h = self.bounds
            x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
            #position_on_trail_for_screen = round(self.position_on_trail + (x_rel * size_of_one_screen_in_dpi), 1)
            position_on_trail_for_screen = round((x_rel * size_of_one_screen_in_dpi)  )
            cv2.putText(frame, str(position_on_trail_for_screen), (int(x), int(y + 25)), cv2.FONT_HERSHEY_COMPLEX, 1, yellow)

    def detect_rim_and_propagate_back_to_yolo_detections(self):
        """
        # find rim and back propagate to detection from Yolo in next loop
        :return:
        """
        global rim_results
        try:
            # if rim is not detected delete rim_results so it will not be appended to detection from youlo in next loop
            if objekty[id].detect_rim(object_for_rim_detection, distance_of_second_edge) == False:
                del rim_results
            # detect_rim return True hten you need to update
            else:
                hcategory, hscore, hbounds = objekty[id].detect_rim(object_for_rim_detection,
                                                                    distance_of_second_edge)
                # in rim_results is rim stored so in can be inported to detection from Yolo in next loop
                rim_results = hcategory.encode("utf-8"), hscore, hbounds

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            # print (message)

    def save_picure_of_every_detected_object(self, file_name="detected_objects"):
        """
        :param folder name need to be suplied:
        """
        if self.is_picture_saved == False:
            save_picture_to_file(file_name)
            self.is_picture_saved = True

process10 = Process(target=second_visualization, args=(416,416) )
process10.daemon = True
process10.start()


if __name__ == "__main__":
    YOLO()
