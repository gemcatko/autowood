import logging
import multiprocessing
import subprocess
import threading
import time
from typing import List, Any, Union

from pydarknet import Detector, Image
import cv2
import numpy as np

# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker
from dev_env_vars import *
from multiprocessing import Process, Value, Queue

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )
import datetime
# subprocess.Popen(['sudo', 'chmod', '666', '/dev/ttyUSB0'])
from magneto import Magneto
#from draw_trail_visualization import draw_trail_visualization


### Imports end here
### Class definitions
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

    def do_not_use_detect_object(self, object_to_detect, triger_margin, how_big_object_max, how_big_object_min):
        """
        :param object_to_detect:
        :param triger_margin:
        :return:
        """
        x, y, w, h = self.bounds
        x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
        ##chnage format to utf-8### object_to_check ## how width ########### where is triger margin################### check if is not id.1 already in in triger list
        if self.category == object_to_detect and how_big_object_max >= w_rel >= how_big_object_min and (
                x_rel + (w_rel / 2)) > triger_margin and self.ready_for_blink_start == False:
            print('Sprav znacky for zaciatok ID .1', self.id)
            # draw purple line on the screens it is just for visual check when call for blink
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 255), 10)
            self.ready_for_blink_start = True
            # position of begin blink
            position_indpi_begin = s_distance.value  # this is from magneto the apsolut distance
            position_indpi_begin = position_indpi_begin + saw_offset + (
                        (x_rel + (w_rel / 2)) * size_of_one_screen_in_dpi)
            triger = id + 0.1, position_indpi_begin
            # save_picture_to_file("detected_errors")
            logging.debug("triger_slow_loop%s", triger)
            trigerlist.append(triger)
            try:
                # add to trigerlist id.01, time when right blink and id.02 time left blink to
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

        if self.category == object_to_detect and how_big_object_max >= w_rel >= how_big_object_min and (
                x_rel - (w_rel / 2)) > triger_margin and self.ready_for_blink_end == False:
            print('Sprav znacky for end .2 ID', self.id)
            # draw purple line on the screens it is just for visual check when call for blink
            cv2.line(frame, (int(x - w / 2), int(y - h / 2)), (int(x - w / 2), int(y + h / 2)), (255, 0, 255), 10)
            self.ready_for_blink_end = True
            # position of end blink
            position_indpi_end = s_distance.value  # this is from magneto the apsolut distance
            position_indpi_end = position_indpi_end + saw_offset + ((x_rel + (w_rel / 2)) * size_of_one_screen_in_dpi)
            # add to trigerlist id.02 time end blink
            triger = id + 0.2, position_indpi_end
            # save_picture_to_file("detected_errors")
            logging.debug("triger_slow_loop%s", triger)
            trigerlist.append(triger)
            try:
                # add to trigerlist id.01, time when right blink and id.02 time left blink to
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

    def detect_rim(self, edge, max_dist_of_2nd_edge):
        """
        rim is defined by 2 edges close enough
        :param edge: category you would like use for rim detection
        :param max_dist_of_2nd_edge for example 0.5 fo 50% of the screen
        :return: true
        """
        if self.category == edge:
            x, y, w, h = self.bounds
            x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
            # loop over detections from yolo and check if there is another edge near by
            for id, category, score, bounds in idresults:
                # is it not the same object? and it is edge?
                if id != self.id and category.decode("utf-8") == edge:
                    xx, yy, ww, hh = bounds
                    xx_rel, yy_rel, ww_rel, hh_rel, aarea_rel = calculate_relative_coordinates(xx, yy, ww, hh)
                    # is second edge close enought ?)
                    if (((x_rel - xx_rel) ** 2) + ((y_rel - yy_rel) ** 2)) ** (0.5) < max_dist_of_2nd_edge:
                        # calculate rim properties
                        new_rim_score = (self.score + score) / 2
                        new_rim_x = (x + xx) / 2
                        new_rim_y = (y + yy) / 2
                        # new_rim_w = (w + ww)
                        # new_rim_h = (h + hh)
                        new_rim_w = abs(x - xx)
                        new_rim_h = abs(y - yy)
                        new_rim_bounds = new_rim_x, new_rim_y, new_rim_w, new_rim_h
                        # create_new_object_with_id(id, category, score, bounds)
                        new_category_rim = "rim"
                        return new_category_rim, new_rim_score, new_rim_bounds
                    else:
                        return False
                else:
                    return False

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
        if self.is_picture_saved == False:
            save_picture_to_file(file_name)
            self.is_picture_saved = True

    def ignore_error_in_error_and_create_new_object(self):
        global aou_results
        if self.category == "error":
            boundsA = self.bounds
            for id, category, score, bounds in idresults:
                if (category.decode("utf-8") == "error") and not self.id == id:
                    boundsB = bounds
                    if get_bounding_box_around_area_ower_union(boundsA, boundsB):
                        bounding_box_around_area_ower_union = get_bounding_box_around_area_ower_union(boundsA, boundsA)
                        score_bounding_box_around_area_ower_union = (self.score + score) / 2
                        category_bounding_box_around_area_ower_union = "BB_around_AOU"
                        self.ignore = True
                        aou_results = category_bounding_box_around_area_ower_union.encode(
                            "utf-8"), score_bounding_box_around_area_ower_union, bounding_box_around_area_ower_union
                        return aou_results

    def stamp(self, object_to_stamp):
        x, y, w, h = self.bounds
        x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
        if self.category == object_to_stamp:
            # position_indpi_begin = s_distance.value + (((x_rel + (w_rel / 2)) * size_of_one_screen_in_dpi)
            # position_indpi_end = s_distance.value + (((x_rel - (w_rel / 2)) * size_of_one_screen_in_dpi)
            stamplist.append(stamp)


class Trail:
    def __int__(self, objekty):
        self.objekty = objekty

    def draw_trail_detection_visualization(self):
        trail_visualization = np.zeros((int(Yresolution / scale_trail_visualization), Xresolution * 2, 3),
                                       dtype="uint8")
        for Yobject in self.objekty:
            xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(Yobject.bounds)
            xA = xA + Yobject.position_on_trail
            xB = xB + Yobject.position_on_trail
            cv2.rectangle(trail_visualization, (int(xA), int(yA / scale_trail_visualization)),
                          (int(xB), int(yB / scale_trail_visualization)), green)
            cv2.imshow("Trail_visualization", trail_visualization)


class BlinkStickThread(threading.Thread):
    def run(self):
        '''Starting blinkStick to blink once in Separate Thread'''
        subprocess.Popen(["python2", "BlinkStick.py"])
        pass


### Funktions
def convert_from_xywh_to_xAyAxByB_format(bounds):
    """

    :param bounds: bounds of in format xywh
    :return: return x1x2y1y2  format
    """

    x, y, w, h = bounds
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return box


def convert_from_xAyAxByB_to_xywh_format(bounds):
    xA, yA, xB, yB = bounds
    x = (xA + xB) / 2
    y = (yA + yB) / 2
    w = abs(xA - xB)
    h = abs(yA - yB)
    xywhBox = [x, y, w, h]  # type: List[Union[float, Any]]
    return xywhBox


def bb_intersection_over_union(boundsA, boundsB):
    """

    :param boundsA: in yolo format(xywh)
    :param boundsB: in yolo format(xywh)
    :return: IoU
    """

    boxA, boxB = convert_from_xywh_to_xAyAxByB_format(boundsA), convert_from_xywh_to_xAyAxByB_format(boundsB)

    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    # return the intersection over union value
    return iou


def get_bounding_box_around_area_ower_union(boundsA, boundsB):
    """

    :param boxA: xywh
    :param boxB: xywh
    :return: xAyAxByB
    """
    # bb_intersection_over_union need to bigger as 0 thats how you know objects overlap each other
    if bb_intersection_over_union(boundsA, boundsB) > 0:
        boxA, boxB = convert_from_xywh_to_xAyAxByB_format(boundsA), convert_from_xywh_to_xAyAxByB_format(boundsB)
        xA = min(boxA[0], boxB[0])
        yA = min(boxA[1], boxB[1])
        xB = max(boxA[2], boxB[2])
        yB = max(boxA[3], boxB[3])
        bbox_of_area_ower_union = [xA, yA, xB, yB]
        bbox_of_area_ower_union = convert_from_xAyAxByB_to_xywh_format(bbox_of_area_ower_union)

        return bbox_of_area_ower_union
    else:
        return False


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


def show_count_of_objects_in_frame(object_to_check):
    number_of_object_to_check = 0
    for cat, score, bounds in results:
        if cat.decode("utf-8") == object_to_check:
            number_of_object_to_check = number_of_object_to_check + 1
        cv2.putText(frame, str(number_of_object_to_check), (int(Xresolution - 20), int(Yresolution - 20)),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
    return number_of_object_to_check


def show_fps(start_time, end_time):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(frame, str(FPS), (int(Xresolution - 80), int(Yresolution - 40)), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 100, 255))
    return FPS


def show_magneto_distance():
    """
    IT is using s_distance.value which is actual sum of angles from magneto
    The funktion need to be called every frame you want to sho something
    :return:
    """
    cv2.putText(frame, str(s_distance.value), (int(Xresolution - 250), int(Yresolution - 80)),
                cv2.FONT_HERSHEY_COMPLEX, 1, blue)


def faster_loop_trigerlist_distance(qtrigerlist):
    """
    Loop for trigering small error in another process running faster then main loop in separate process it is interconnected with main process with trigerlist and shared_x, shared_y
    :param qtrigerlist, shared_x, shared_y:
    :return:nothing

    """
    while True:
        start_time_loop = time.time()
        try:
            # needed because qtrigerlist is not always having object inside
            trigerlist = qtrigerlist.get_nowait()
            logging.debug("trigerlist%s", trigerlist)

        except:
            # is setting speed of the loop in case 0.0005 it is 2000 times per second
            # except is not executed if qtrigerlist is have data
            time.sleep(0.0005)
        # print("Distance {}".format(m_point.get_distance()))

        distance = s_distance.value
        # for id_begining, begin_distance, id_ending, end_distance in trigerlist:
        for id_begining, begin_distance in trigerlist:
            if begin_distance <= abs(distance) and not (any(id_begining in sublist for sublist in alreadyBlinkedList)):
                alreadyBlinkedTriger = id_begining, begin_distance
                alreadyBlinkedList.append(alreadyBlinkedTriger)
                blink_once()
                # needed thus the function know which object was already blinked and which not

                logging.debug('id_begining blink_once() called for blink, alreadyBlinkedList:%s', alreadyBlinkedList)
            """
            if end_distance <= abs(distance) and not (any(id_ending in sublist for sublist in alreadyBlinkedList)):
                alreadyBlinkedTriger = id_ending, end_distance
                # needed thus the function know which object was already blinked and which not
                alreadyBlinkedList.append(alreadyBlinkedTriger)
                blink_once()
                logging.debug('id_ending blink_once() called for blink alreadyBlinkedList:%s', alreadyBlinkedList)
            """
        end_time_loop = time.time()
        # check for how long took execution the loop and log if it is too long
        last_loop_duration = end_time_loop - start_time_loop
        if (last_loop_duration) > 0.010:
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)

def faster_loop_2(faster_loop2_blikaj, faster_loop2_trieda):

    """
    loopa ktra bude stale bezat a bude mat udaj kedy moze ist najblizss dalsi blik
    :param blikaj:
    :param trieda:
    :return: is returning next possible blick
    """
    next_possible_blink = 0
    while True:
        start_time_loop = time.time()
        try:
            # needed because qtrigerlist is not always having object inside
            #@TODO tu zisti preco nedava sharovanu value s druheho procesu !!!!!
            blikaj =  faster_loop2_blikaj.value
            #logging.debug("trigerlist%s", blikaj)

        except:
            # is setting speed of the loop in case 0.0005 it is 2000 times per second
            # except is not executed if qtrigerlist is have data
            time.sleep(0.0005)


        if blikaj and (s_distance.value < next_possible_blink):
            blink_once()
            next_possible_blink = (s_distance.value - 50)
            logging.debug('Next_possible_blink is :%s', next_possible_blink)
        end_time_loop = time.time()
        # check for how long took execution the loop and log if it is too long
        last_loop_duration = end_time_loop - start_time_loop
        if (last_loop_duration) > 0.010:
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)
        #return next_possible_blink


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


def convert_bounding_boxes_form_Yolo_Centroid_format(results):
    # clean rect so it is clean an can be filled with new detection from frame\
    # later used in conversion_to_x1y1x2y2 . Conversion from yolo format to Centroid Format
    # rects are needed for centroid to work. They need to be cleared every time
    rects = []
    for cat, score, bounds in results:
        x, y, w, h = bounds
        """
        convert from yolo format to cetroid format
        Yolo output:
        [(b'person', 0.9299755096435547, (363.68475341796875, 348.0577087402344, 252.04286193847656, 231.17266845703125)), (b'vase', 0.3197628855705261, (120.3013687133789, 405.3641357421875, 40.76551055908203, 32.07142639160156))]
        centroid input: 
        [array([145, 153, 248, 274]), array([113, 178, 148, 224])]
        """
        # calculate bounding box for every object from YOLO for centroid purposes
        box = np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
        # append to list of  bounding boxes for centroid
        rects.append(box.astype("int"))
    return rects


def dddraw_ids_on_screens(objects):  # DO not use! it was changed to sraw_object_id()
    """

    :param objects:  from cetroid tracker
    :return: none
    """

    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


def draw_yolo_output_on_screen(results):  # DO not use! it was changed to draw_object_bb_and_class(self):
    """

    :param results: results from Yolo34
    :return: none
    """
    # for every detection in results do use this loop for drawing
    for cat, score, bounds in results:
        x, y, w, h = bounds
        cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0))
        cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))


def update_objekty_if_not_detected(objekty):
    """
    :param objekty:
    Is updating all objects store in objekty if not in in idresults list from detector
    :return:
    """
    for id in objekty:
        # id in (item for sublist in idresults for item in sublist) is returning True or False good explanation is https://www.geeksforgeeks.org/python-check-if-element-exists-in-list-of-lists/
        if not id in (item for sublist in idresults for item in sublist):
            objekty[id].is_detected_by_detector = False
            #objekty[id].position_on_trail = s_distance.value


def get_path_filename_datetime(folder_name):
    # Use current date to get a text file name.
    return folder_name + "/" + str(datetime.datetime.now()) + ".jpg"


def save_picture_to_file(folder_name):
    rr, oneframe = cap.read()
    cv2.imwrite(get_path_filename_datetime(folder_name), oneframe)


def convert_from_xywh_to_xAyAxByB_format(bounds):
    """

    :param bounds: bounds of in format xywh
    :return: return x1x2y1y2  format
    """

    x, y, w, h = bounds
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return box

def dpi_to_pixels(dpi):
    """
    :param dpi: angle in dpi which you would like to convert to pixels . It is using global variable size_of_one_screen_in_dpi which is defined in dev_env_wars
    :return: pixels
    """
    return (Xresolution / size_of_one_screen_in_dpi) * dpi


def draw_trail_visualization(objeky,s_distance):
    global faster_loop2_blikaj
    global faster_loop2_trieda
    trail_visualization = np.zeros((int(Yresolution / scale_trail_visualization), Xresolution * 2, 3),
                                   dtype="uint8")
    saw_senzor_ofset_from_screen_pixels = int(Xresolution + dpi_to_pixels(saw_offset))
    #draw position of senzor with purple line
    cv2.line(trail_visualization, (int(Xresolution + dpi_to_pixels(saw_offset) ), int(1)), (int(Xresolution + dpi_to_pixels(saw_offset)), int(Yresolution/scale_trail_visualization)), (255, 0, 255), 10)

    cv2.putText(trail_visualization, str(saw_senzor_ofset_from_screen_pixels),(int(Xresolution + dpi_to_pixels(saw_offset)), int(Yresolution/scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, 1,
                magenta)
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        #draw error, eye, crack, rot, and crust as red color
        if objekty[id].category == "error" or objekty[id].category == "eye" or objekty[id].category == "crack" or objekty[id].category == "rot" or objekty[id].category == "crust":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),(int(visualization_xB), int(yB / scale_trail_visualization)), red, 3)
            # draw objekty[id].position_on_trail
            cv2.putText(trail_visualization, str(objekty[id].id), (int(visualization_xA), int(yB / scale_trail_visualization)),cv2.FONT_HERSHEY_COMPLEX, 1, (magenta))
            # visualization_xB is start location of error and visualization_xA end of error
            if(visualization_xB > saw_senzor_ofset_from_screen_pixels) and (visualization_xA < saw_senzor_ofset_from_screen_pixels):
                print ("Blikaj error xB xA")
                objekty[id].ready_for_blink_start = True
                #blink_once()
                faster_loop2_blikaj = multiprocessing.Value('i', 1)
                faster_loop2_trieda = "error"
                #@TODO vygeneruj znacky

            else:
                faster_loop2_blikaj = multiprocessing.Value('i', 0)
                faster_loop2_trieda = "error"
                print ("!!!neblikaj error xB xA")


        #draw secondclass as brown collor
        elif objekty[id].category == "secondclass" or objekty[id].category == "zapar" or objekty[id].category == "darksecondclass" or objekty[id].category == "edge":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), brown, 2)
            cv2.putText(trail_visualization, str(objekty[id].id),
                        (int(visualization_xA), int(yB / scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (magenta))

    cv2.imshow("Trail_visualization", trail_visualization)





if __name__ == "__main__":

    ################################ SETUP #############################################################################
    # USE if video from file. video_filename  fefinition is located in  dev_env_vars.py
    # cap = cv2.VideoCapture(video_filename)

    # USE if  webcam

    cap = cv2.VideoCapture(0)  # set web cam properties width and height, working for USB for webcam
    cap.set(3, Xresolution)
    cap.set(4, Yresolution)
    ##Use webcam with high frame rate
    codec = cv2.VideoWriter_fourcc("M", "J", "P", "G")
    cap.set(cv2.CAP_PROP_FPS, 50)  # FPS60FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Xresolution)  # set resolutionx of webcam
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Yresolution)  # set resolutiony of webcam
    cap.set(cv2.CAP_PROP_FOURCC, codec)
    print(cap.get(cv2.CAP_PROP_FPS))
    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # initialize our centroid tracker and frame dimensions
    ct = CentroidTracker(maxDisappeared=20)
    # (H, W) = (None, None)

    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes(yolov3_cfg, encoding=cat_encoding), bytes(yolov_weights, encoding=cat_encoding), 0,
                   bytes(obj_data, encoding=cat_encoding), )

    # Start loop for blinking in separate process
    # initialize shared var for distance for magneto
    # sudo chmod 666 /dev/ttyUSB0
    s_distance = Value('l', 0)
    # create instance of Process subclass Magneto and pass shared value var
    sensor_process = Magneto(shared_distance=s_distance)
    sensor_process.start()

    # Shared queue for list with ids to blink
    qtrigerlist = multiprocessing.Queue()
    qtrigerlist.put(trigerlist)
    # Start faster_loop_trigerlist in separate process and processor so it is not delayed by main process
    # process1 = multiprocessing.Process(target=faster_loop_trigerlist, args=(qtrigerlist, s_x, s_y, ))
    process1 = multiprocessing.Process(target=faster_loop_trigerlist_distance, args=(qtrigerlist,))
    process1.daemon = True
    #process1.start()
    faster_loop2_blikaj = multiprocessing.Value('i',0)
    faster_loop2_trieda = "ziadna"
    process2 = multiprocessing.Process(target=faster_loop_2, args=(faster_loop2_blikaj, faster_loop2_trieda,))
    process2.daemon = True
    process2.start()

    ########################## MAIN LOOP ###############################################################################

    while True:
        start_time = time.time()
        r, frame = cap.read(0)
        if r:
            # start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            # call Yolo34
            results = net.detect(dark_frame, thresh=detection_treshold)
            try:
                # update results for rim if founded in previous picture
                # results.append(rim_results)
                results.append(aou_results)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                # "print (message)"

            del dark_frame
            rects = convert_bounding_boxes_form_Yolo_Centroid_format(results)
            objects = ct.update(rects)
            # draw_ids_on_screens(objects)            # PUTT all detected objects with ids to idresults list
            idresults = update_resutls_for_id(results)
            # Loop over all objects which are detected by Yolo+id
            for id, category, score, bounds in idresults:
                try:
                    # if Yobjekt with specific id already exists, update it
                    # TODO # to je mozno chyba,co sa stane z objektami ktorych id je este na zobrazene ale nuz je objekt dissapeared
                    if objekty[id].id == id: #and objekty[id].category == category.decode("utf-8"):
                        if objekty[id].category == category.decode("utf-8"):
                            objekty[id].category = category.decode("utf-8")
                            objekty[id].score = score
                            objekty[id].bounds = bounds
                            objekty[id].position_on_trail = s_distance.value
                            objekty[id].is_detected_by_detector = True

                except:
                    # create new object if not existing
                    objekty[id] = YObject(id, category.decode("utf-8"), score, bounds, s_distance.value)

            for id in objekty:
                objekty[id].detect_rim_and_propagate_back_to_yolo_detections()
                # TODO #Figure out if ignore_error_in_error_and_create_new_object() is working - it is partly
                # objekty[id].ignore_error_in_error_and_create_new_object()
                objekty[id].draw_object_bb_and_class()
                objekty[id].draw_object_score()
                objekty[id].draw_object_id()
                objekty[id].draw_object_position_on_trail()
                # objekty[id].do_not_use_detect_object(object_to_detect, triger_margin, how_big_object_max_small,how_big_object_min_small)
                # objekty[id].save_picure_of_every_detected_object()
            update_objekty_if_not_detected(objekty)
            try:
                #print ("#draw_trail_visualization(objekty, s_distance)")
                draw_trail_visualization(objekty, s_distance)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
            # show distance of mouse sensor on screen
            show_magneto_distance()
            show_count_of_objects_in_frame("error")
            # used for counting the show_fps
            end_time = time.time()
            show_fps(start_time, end_time)

        cv2.imshow("preview", frame)
        # print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
