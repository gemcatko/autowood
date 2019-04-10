import logging
import multiprocessing
import subprocess
import threading
import time
from pydarknet import Detector, Image

import cv2
import numpy as np

from mpoint.mpoint import Mpoint
# for manual see: https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
from pyimagesearch.centroidtracker import CentroidTracker

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

# DONE how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light => red led
# DONE Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3 => https://shop.blinkstick.com/
# DONE give objecs uniqe ID
# TODO calculate speed of objects integarde mpoint
# TODO Store image detections as thumbnails(small images) somewhere


class YObject:
    # z Yola ide idresult a v idrusulte su id, cat, score, bounds
    # def __init__(self, centroid_id, category, score, bounds):
    def __init__(self, id, category, score, bounds):
        # centroid_id , detected_category, score, object_position_center_x ,object_position_center_y ,width w, height_h
        # copy paste functionality of  detect_object_4_c
        self.id = id
        self.category = category
        self.score = score
        self.bounds = bounds
        #self.x,self.y,self.w,self.h = bounds
        self.is_on_screen = True
        self.ready_for_blink = False

    def draw_object_and_id(self):
        """
        Draw objects on screen using cv2
        :return: none
        """
        x, y, w, h = self.bounds
        cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (125, 125, 125),4)
        # draw what is name of the object
        #cv2.putText(frame, str(category), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
        cv2.putText(frame, str(self.category), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
        #Draw ID dot
        #TODO finish
        #Draw id number text
        #TODO finish

    def detect_object(self, object_to_detect,triger_margin,how_big_object_max, how_big_object_min):
        """
        :param object_to_detect:
        :param triger_margin:
        :return:
        """
        x,y,w,h = self.bounds
        x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
        ##chnage format to utf-8### object_to_check ## how width ########### where is triger margin################### check if is not id.1 already in in triger list
        if self.category == object_to_detect and how_big_object_max >= w_rel >= how_big_object_min and (x_rel + (w_rel / 2)) > triger_margin and self.ready_for_blink == False :
            print('Sprav znacky for ID',self.id)
            # draw purple line on the screens it is just for visual check when call for blink
            cv2.line(frame, (int(x + w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (255, 0, 255), 10)
            self.ready_for_blink = True
            #TODO separate blinking somewhere here
            # time of right blink
            time_begining = time.time() + delay + ((1 - (x_rel + (w_rel / 2))) * duration_1screen_s)
            # time of left blink
            time_ending = time_begining + ((1 - (x_rel - (w_rel / 2))) * duration_1screen_s)
            # add to trigerlist id.01, time when right blink and id.02 time left blink
            triger = id + 0.1, time_begining, id + 0.2, time_ending
            trigerlist.append(triger)
            try:
                #add to trigerlist id.01, time when right blink and id.02 time left blink to
                qtrigerlist.put(trigerlist)
            except:
                print("Main thread exception occurred qtrigerlist.put(trigerlist)")

    def detect_hrana(self, edge, distance_of_second_edge):
        """
        hrana is defined by 2 edges close enough
        :param edge: category you would like use for hrana detection
        :param distance_of_second_edge for example 0.5 fo 50% of the screen
        :return: true
        """
        already_founded_second_edge = -1
        if self.category == edge:
            x, y, w, h = self.bounds
            x_rel, y_rel, w_rel, h_rel, area_rel = calculate_relative_coordinates(x, y, w, h)
            # loop over detections from yolo and check if there is another edge near by
            for id, category, score, bounds in idresults:
                # is it not the same object? and it is edge?
                if id != self.id and category.decode("utf-8")  == edge:
                    xx, yy, ww, hh = bounds
                    xx_rel, yy_rel, ww_rel, hh_rel, aarea_rel = calculate_relative_coordinates(xx, yy, ww, hh)
                    # is second edge close enought ?
                    if abs(x_rel - xx_rel) + abs(y_rel - yy_rel) < distance_of_second_edge:
                        new_hrana_id = -1*(self.id + id)
                        new_hrana_score = (self.score + score)/2
                        new_hrana_x = (x + xx) /2
                        new_hrana_y = (y + yy) /2
                        new_hrana_w = (w + ww) /2
                        new_hrana_h = (h + hh) /2
                        new_hrana_bounds = new_hrana_x, new_hrana_y, new_hrana_w, new_hrana_h
                        #create_new_object_with_id(id, category, score, bounds)
                        new_category_hrana = "hrana"
                        return new_hrana_id, new_category_hrana, new_hrana_score, new_hrana_bounds
                    else:
                        return False
                else:
                    return False

    def check_if_on_screen(self):
        for id, category, score, bounds in idresults:
            if id in idresults:
                self.is_on_screen == False



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

def count_objects_in_frame(object_to_check):
    number_of_object_to_check = 0
    for cat, score, bounds in results:
        if cat.decode("utf-8") == object_to_check:
            number_of_object_to_check = number_of_object_to_check + 1
        cv2.putText(frame, str(number_of_object_to_check), (int(Xresolution - 20), int(Yresolution-20)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
    return number_of_object_to_check

def show_fps(start_of_loop, end_of_loop):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(frame, str(FPS), (int(Xresolution - 20), int(Yresolution - 40)),cv2.FONT_HERSHEY_COMPLEX, 1, (255, 100, 255))
    return FPS

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
        if (last_loop_duration) > 0.010:
            logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)
        # need to be on the end to improve measurement
        absolut_end_time_loop = time.time()
        absolut_last_loop_duration = absolut_end_time_loop - start_time_loop

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


if __name__ == "__main__":

    ###################### VARS : ######################################################################################

    # set resolution taken from webcam
    Xresolution = 480
    Yresolution = 320
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
    objekty = {}
    #
    how_big_object_max_small = 0.9
    how_big_object_min_small = 0.05
    object_for_hrana_detection = "orange"
    distance_of_second_edge = 0.5

    # set web cam properties width and height, working for USB for webcam
    cap = cv2.VideoCapture(0)

    #static video file
    #video_filename = "MOV_2426.mp4"
    #cap = cv2.VideoCapture(video_filename)
    cap.set(3, Xresolution)
    cap.set(4, Yresolution)
    # virtual position of triger relative to camera
    triger_margin = 0.8
    object_to_detect = "cell phone"
    # initialize our centroid tracker and frame dimensions
    ct = CentroidTracker(maxDisappeared=5)
    (H, W) = (None, None)

    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0,bytes("cfg/coco.data", encoding="utf-8"), )
    #net = Detector(bytes("cfg/2019_02_11_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2019_03_15_yolo-obj_3200.weights", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )

    # Start loop for blinking in separate process


    # initialize shared vars for speed/movement x,y
    s_x = multiprocessing.Value('i', 0)
    s_y = multiprocessing.Value('i', 0)

    # create instance of Process subclass Mpoint and pass shared values vars
    mp = Mpoint(shared_x=s_x, shared_y=s_y)
    mp.start()

    # Shared queue for list with ids to blink
    qtrigerlist = multiprocessing.Queue()
    qtrigerlist.put(trigerlist)
    process1 = multiprocessing.Process(target=faster_loop_trigerlist, args=(qtrigerlist, s_x, s_y))
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
            results = net.detect(dark_frame, thresh=0.7)
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
            #loop over all object and ttry
            for id, category, score, bounds in idresults:
                try:
                    # if objekt already exists, update it
                    if objekty[id].id == id:
                        #
                        objekty[id].category = category.decode("utf-8")
                        objekty[id].score = score
                        objekty[id].bounds = bounds
                except:
                    #create new object if not existing
                    objekty[id] = YObject(id, category.decode("utf-8"), score, bounds)

#                objekty[id].draw_object_and_id()
#                objekty[id].detect_object(object_to_detect, triger_margin, how_big_object_max_small, how_big_object_min_small)

                # find rim and back propagate to detection from Yolo in next loop
                try:
                    # if hrana is not detected delete hresults so it will not be appended to detection from youlo in next loop
                    if objekty[id].detect_hrana(object_for_hrana_detection, distance_of_second_edge) == False:
                        del hresults
                    # detect_hrana return True hten you need to update
                    else:
                        do_not_use_id, hcategory, hscore, hbounds = objekty[id].detect_hrana(object_for_hrana_detection,distance_of_second_edge)
                        # in hresults is rim stored so in can be inported to detection from Yolo in next loop
                        hresults = hcategory.encode("utf-8"), hscore, hbounds

                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    #"print (message)"
                objekty[id].draw_object_and_id()
                objekty[id].detect_object(object_to_detect, triger_margin, how_big_object_max_small, how_big_object_min_small)

            #TODO fix: count_objects_in_frame("cell phone")
            #TODO Here you can write yor own function which will be using class or another object oriented aproach, use !!!! idresults !!!! variable. You can do whatever you like just do not change existing code. make Class when it see "Apple it give back true use idresults: "
            #TODO Detection for errors which are longer then XX(probably 15) cm
            end_time = time.time()
            show_fps(start_time, end_time)
        cv2.imshow("preview", frame)
        #print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break
