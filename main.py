import logging
import multiprocessing
import subprocess
import threading
import time
from pydarknet import Detector, Image
import cv2
import numpy as np
from mpoint.mpoint import Mpoint, feed_queue
# import Mpoint from mpoint.mpoint
# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker
from dev_env_vars import *
from multiprocessing import Process, Value, Queue

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )
import datetime


# TODO calculate speed of objects integrate mpoint
# TODO Store image detections as thumbnails(small images) somewhere

class YObject:
    # use for creating objects from Yolo.
    # def __init__(self, centroid_id, category, score, bounds):
    def __init__(self, id, category, score, bounds):
        # copy paste functionality of  detect_object_4_c
        self.id = id
        self.category = category
        self.score = score
        self.bounds = bounds
        self.is_on_screen = True
        self.is_picture_saved = False
        self.ready_for_blink_start = False
        self.ready_for_blink_end = False

    def draw_object_and_id(self):
        """
        Draw objects on screen using cv2
        :return: none
        """
        x, y, w, h = self.bounds
        cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (125, 125, 125), 4)
        # draw what is name of the object
        # cv2.putText(frame, str(category), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
        cv2.putText(frame, str(self.category), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
        # Draw ID dot
        # TODO finish
        # Draw id number text
        # TODO finish

    def detect_object(self, object_to_detect, triger_margin, how_big_object_max, how_big_object_min):
        """
        :param object_to_detect:
        :param triger_margin:
        :return:
        """
        x, y, w, h = self.bounds
        x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
        ##chnage format to utf-8### object_to_check ## how width ########### where is triger margin################### check if is not id.1 already in in triger list
        if self.category == object_to_detect and how_big_object_max >= w_rel >= how_big_object_min and (x_rel + (w_rel / 2)) > triger_margin and self.ready_for_blink_start == False:
            print('Sprav znacky for zaciatok ID', self.id)
            # draw purple line on the screens it is just for visual check when call for blink
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 255), 10)
            self.ready_for_blink_start = True
            # position of begin blink
            dis_x, dis_y = m_point.get_distance()
            position_indpi_begin = dis_y + saw_offset + ((x_rel + (w_rel / 2)) * size_of_one_screen_in_dpi)
            triger = id + 0.1, position_indpi_begin
            #save_picture_to_file("detected_errors")
            logging.debug("triger_slow_loop%s", triger)
            trigerlist.append(triger)
            try:
                # add to trigerlist id.01, time when right blink and id.02 time left blink to
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

        if self.category == object_to_detect and how_big_object_max >= w_rel >= how_big_object_min and (x_rel - (w_rel / 2)) > triger_margin and self.ready_for_blink_end == False:
            print('Sprav znacky for end ID', self.id)
            # draw purple line on the screens it is just for visual check when call for blink
            cv2.line(frame, (int(x - w / 2), int(y - h / 2)), (int(x - w / 2), int(y + h / 2)), (255, 0, 255), 10)
            self.ready_for_blink_end = True
            # position of end blink
            dis_x, dis_y = m_point.get_distance()
            position_indpi_end = dis_y + saw_offset + ((x_rel + (w_rel / 2)) * size_of_one_screen_in_dpi)
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



    def detect_rim(self, edge, distance_of_second_edge):
        """
        rim is defined by 2 edges close enough
        :param edge: category you would like use for rim detection
        :param distance_of_second_edge for example 0.5 fo 50% of the screen
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
                    if (((x_rel - xx_rel) ** 2) + ((y_rel - yy_rel) ** 2)) ** (0.5) < distance_of_second_edge:
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
        global hresults
        try:
            # if rim is not detected delete hresults so it will not be appended to detection from youlo in next loop
            if objekty[id].detect_rim(object_for_rim_detection, distance_of_second_edge) == False:
                del hresults
            # detect_rim return True hten you need to update
            else:
                hcategory, hscore, hbounds = objekty[id].detect_rim(object_for_rim_detection,
                                                                    distance_of_second_edge)
                # in hresults is rim stored so in can be inported to detection from Yolo in next loop
                hresults = hcategory.encode("utf-8"), hscore, hbounds

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            # print (message)

    def save_picure_of_every_detected_object(self, file_name="detected_objects"):
        if self.is_picture_saved == False:
            save_picture_to_file(file_name)
            self.is_picture_saved = True

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
        dis_x, dis_y = m_point.get_distance()
        #for id_begining, begin_distance, id_ending, end_distance in trigerlist:
        for id_begining, begin_distance in trigerlist:
            if begin_distance <= abs(dis_y) and not (any(id_begining in sublist for sublist in alreadyBlinkedList)):
                alreadyBlinkedTriger = id_begining, begin_distance
                alreadyBlinkedList.append(alreadyBlinkedTriger)
                blink_once()
                # needed thus the function know which object was already blinked and which not

                logging.debug('id_begining blink_once() called for blink, alreadyBlinkedList:%s', alreadyBlinkedList)
            """
            if end_distance <= abs(dis_y) and not (any(id_ending in sublist for sublist in alreadyBlinkedList)):
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


def draw_ids_on_screens(objects):
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


def draw_yolo_output_on_screen(results):
    """

    :param results: results from Yolo34
    :return: none
    """
    # for every detection in results do use this loop for drawing
    for cat, score, bounds in results:
        x, y, w, h = bounds
        cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 0))
        cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))


def update_objekty_if_on_screen(objekty):
    """
    :param objekty:
    Is updating all objects store in objekty if is on screen or not
    :return:
    """
    for YObject in objekty:
        if objekty[YObject].id not in idresults:
            objekty[YObject].is_on_screen = False


def get_path_filename_datetime(folder_name):
    # Use current date to get a text file name.
    return folder_name + "/" + str(datetime.datetime.now()) + ".jpg"


def save_picture_to_file(folder_name):
    rr, oneframe = cap.read()
    cv2.imwrite(get_path_filename_datetime(folder_name), oneframe)


if __name__ == "__main__":

    ################################ SETUP #############################################################################
    """"""
    cap = cv2.VideoCapture(0)  # set web cam properties width and height, working for USB for webcam
    # video_filename = "MOV_2426.mp4"                                        # use if you want to use static video file
    # cap = cv2.VideoCapture(video_filename)
    cap.set(3, Xresolution)
    cap.set(4, Yresolution)

    # initialize our centroid tracker and frame dimensions
    ct = CentroidTracker(maxDisappeared=20)
    # (H, W) = (None, None)

    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes(yolov3_cfg, encoding=cat_encoding), bytes(yolov_weights, encoding=cat_encoding), 0,
                   bytes(obj_data, encoding=cat_encoding), )

    # Start loop for blinking in separate process

    # initialize shared vars for speed/movement x,y
    s_x = Value('i', 0)
    s_y = Value('i', 0)
    s_distance_x = Value('l', 0)
    s_distance_y = Value('l', 0)
    s_queue = Queue()

    # create process to feed queue
    p = Process(target=feed_queue, args=(s_queue, "/dev/input/mice"))
    p.start()

    # create instance of Process subclass Mpoint and pass shared values vars
    m_point = Mpoint(shared_x=s_x, shared_y=s_y, shared_d_x=s_distance_x, shared_d_y=s_distance_y, shared_queue=s_queue,
                     loop_delay=0.001, filename="/dev/input/mice")
    m_point.start()

    # Shared queue for list with ids to blink
    qtrigerlist = multiprocessing.Queue()
    qtrigerlist.put(trigerlist)
    # Start faster_loop_trigerlist in separate process and processor so it is not delayed by main process
    # process1 = multiprocessing.Process(target=faster_loop_trigerlist, args=(qtrigerlist, s_x, s_y, ))
    process1 = multiprocessing.Process(target=faster_loop_trigerlist_distance, args=(qtrigerlist,))
    process1.daemon = True
    process1.start()

    ########################## MAIN LOOP ###############################################################################

    while True:
        start_time = time.time()
        r, frame = cap.read()
        if r:
            # start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            # call Yolo34
            results = net.detect(dark_frame, thresh=detection_treshold)
            try:
                results.append(hresults)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                # "print (message)"

            del dark_frame
            rects = convert_bounding_boxes_form_Yolo_Centroid_format(results)
            objects = ct.update(rects)
            draw_ids_on_screens(objects)
            # PUTT all detected objects with ids to idresults list
            idresults = update_resutls_for_id(results)
            # Loop over all objects which are detected by Yolo+id
            for id, category, score, bounds in idresults:
                try:
                    # if Yobjekt with specifict id already exists, update it
                    if objekty[id].id == id:
                        objekty[id].category = category.decode("utf-8")
                        objekty[id].score = score
                        objekty[id].bounds = bounds
                except:
                    # create new object if not existing
                    objekty[id] = YObject(id, category.decode("utf-8"), score, bounds)

                objekty[id].detect_rim_and_propagate_back_to_yolo_detections()
                objekty[id].draw_object_and_id()
                objekty[id].detect_object(object_to_detect, triger_margin, how_big_object_max_small,
                                          how_big_object_min_small)
                objekty[id].save_picure_of_every_detected_object()
            update_objekty_if_on_screen(objekty)
            # show distance of mouse sensor on screen
            cv2.putText(frame, str(m_point.get_distance()), (int(Xresolution - 200), int(Yresolution - 80)),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 255))
            show_count_of_objects_in_frame("error")
            end_time = time.time()
            show_fps(start_time, end_time)
        # print("Distance {}".format(m_point.get_distance()))
        cv2.imshow("preview", frame)
        # print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
