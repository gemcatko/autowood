import threading    # needed blink stick
import subprocess   # needed for blink stick

import cv2
import numpy as np
from dev_env_vars import *
import multiprocessing
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )


class BlinkStickThread(threading.Thread):
    def run(self):
        '''Starting blinkStick to blink once in Separate Thread'''
        subprocess.Popen(["python2", "BlinkStick.py"])
        pass


class BlinkStickThreadDouble(threading.Thread):
    def run(self):
        '''Starting blinkStick to blink once in Separate Thread'''
        subprocess.Popen(["python2", "BlinkStickDouble.py"])
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

def blink_double():
    """
    Is using threading for blinking once, create tread for BlinkStick.py (python2.7)

    """
    try:
        # os.system('python2 BlinkStick.py') # najpomalsie
        # subprocess.Popen(["python2", "BlinkStick.py"]) #troska ryclesie
        thread = BlinkStickThreadDouble()
        thread.daemon = True
        thread.start()
    except:
        print("BlinkStickDouble exception occurred ")
    pass

def dpi_to_pixels(dpi):
    """
    :param dpi: angle in dpi which you would like to convert to pixels . It is using global variable size_of_one_screen_in_dpi which is defined in dev_env_wars
    :return: pixels
    """
    return (Xres / size_of_one_screen_in_dpi) * dpi

def convert_from_xywh_to_xAyAxByB_format(bounds):
    """

    :param bounds: bounds of in format xywh
    :return: return x1x2y1y2  format
    """

    x, y, w, h = bounds
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return box

def show_fps(start_time, end_time,name_of_frame):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(name_of_frame, str(FPS), (int(Xres*2 - 80), int(Yres/4 - 10)), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 100, 255))
    #print(FPS)
    return FPS

def show_magneto_distance(name_of_frame,s_distance):
    """
    IT is using s_distance.value which is actual sum of angles from magneto
    The funktion need to be called every frame you want to sho something
    :return:
    """
    cv2.putText(name_of_frame, str(s_distance.value), (int(Xres*2 -150), int( 30)), cv2.FONT_HERSHEY_COMPLEX, 1, blue)

def draw_trail_visualization(objekty,s_distance):
    start_time = time.time()
    trail_visualization = np.zeros((int(Yres / scale_trail_visualization), Xres * 2, 3),
                                   dtype="uint8")
    saw_senzor_ofset_from_screen_pixels = int(Xres + dpi_to_pixels(saw_offset))
    #draw position of senzor with magenta line
    cv2.line(trail_visualization, (int(Xres + dpi_to_pixels(saw_offset) ), int(1)), (int(Xres + dpi_to_pixels(saw_offset)), int(Yres/scale_trail_visualization)), (255, 0, 255),3)
    cv2.putText(trail_visualization, str(saw_senzor_ofset_from_screen_pixels),(int(Xres + dpi_to_pixels(saw_offset)), int(Yres/scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, font_size,
                magenta)
    for id in objekty:
        #xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        #draw error, eye, crack, rot, and crust as red color
        if objekty[id].category == "error" or objekty[id].category == "eye" or objekty[id].category == "crack" or objekty[id].category == "rot" or objekty[id].category == "crust" or objekty[id].category == "badedge":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),(int(visualization_xB), int(yB / scale_trail_visualization)), red, 3)
            cv2.putText(trail_visualization, str(objekty[id].id), (int(visualization_xA), int(yB / scale_trail_visualization)),cv2.FONT_HERSHEY_COMPLEX, font_size, (magenta))
            # visualization_xB is start location of error and visualization_xA end of error
        if objekty[id].category == "secondclass" or objekty[id].category == "steamywood" or objekty[id].category == "darksecondclass" :
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), brown, 2)
            cv2.putText(trail_visualization, str(objekty[id].id),
                        (int(visualization_xA), int(yB / scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, font_size,
                        (magenta))
        if objekty[id].category == "edge" :
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), green, 2)
            cv2.putText(trail_visualization, str(objekty[id].id),
                        (int(visualization_xA), int(yB / scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, font_size,(magenta))
        if objekty[id].category == "mark":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), azzure, 2)
            cv2.putText(trail_visualization, str(objekty[id].id),
                        (int(visualization_xA), int(yB / scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, font_size,(magenta))
    #cv2.imshow("Trail_visualization", trail_visualization)
    end_time = time.time()
    show_fps(start_time, end_time, trail_visualization)
    show_magneto_distance(trail_visualization,s_distance)
    return trail_visualization

def check_on_vysialization (trail_visualization,objekty,s_distance):
    global blink_error
    global blink_second
    global error_next_possible_blink
    global second_next_possible_blink
    global last_blinked_class

    """
    loopa ktra bude stale bezat a bude mat udaj kedy moze ist najblizss dalsi blik
    :param blikaj:
    :param trieda:
    :return: is returning next possible blick
    """

    # Fire mark if first on magenta line
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        if objekty[id].category == "error" or objekty[id].category == "eye" or objekty[id].category == "crack" or objekty[id].category == "rot" or objekty[id].category == "crust" or objekty[id].category == "badedge" :
            if (visualization_xB > saw_senzor_ofset_from_screen_pixels) and (visualization_xA < saw_senzor_ofset_from_screen_pixels):
                blink_error = 1
                break
            blink_error = 0
            #print ("neblikaj error")
    # siganlyze on screen if second class found
    cv2.putText(trail_visualization, "1st C:" + str(blink_error), (int(Xres), int(15)), cv2.FONT_HERSHEY_COMPLEX, font_size, red)

    # Fire mark if second class on magenta line
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        # calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        if objekty[id].category == "secondclass" or objekty[id].category == "steamywood" or objekty[id].category == "darksecondclass":
            if (visualization_xA < saw_senzor_ofset_from_screen_pixels) and (visualization_xB > saw_senzor_ofset_from_screen_pixels):
                blink_second = 1
                break
            blink_second = 0
    # siganlyze on screen if second class found
    cv2.putText(trail_visualization, "2st C:" + str(blink_second), (int(Xres), int(100)), cv2.FONT_HERSHEY_COMPLEX, font_size, brown)
    #cv2.imshow("Trail_visualization", trail_visualization)

    # if for error
    if (blink_error == 1):
        if (s_distance.value < error_next_possible_blink):
            print("Ferror:", blink_error, blink_second)
            blink_once()
            error_next_possible_blink =(s_distance.value - error_next_possible_blink_min)
            second_next_possible_blink = error_next_possible_blink
            logging.debug('Next_possible_blink_error is :%s', error_next_possible_blink)
            last_blinked_class = "error"
    if (blink_error == 1):
        cv2.line(trail_visualization, (int(Xres + dpi_to_pixels(saw_offset)) + (error_next_possible_blink - s_distance.value), 0),
                 (int(Xres + dpi_to_pixels(saw_offset)) + (error_next_possible_blink - s_distance.value),
                  int(Yres / scale_trail_visualization)), red, 2)


    # if second class do blink
    if ((blink_second == 1)  and (blink_error == 0)):  # and (last_blinked_class != "second")
        #second_next_possible_blink = int( visualization_xA - 10)
        if (s_distance.value < second_next_possible_blink) and not (last_blinked_class == "second"):    # pravdepodobne uz vobec nepotrebujes next posible blik tak sah ho treba zbavit
            print("FSecond:", blink_error, blink_second)
            blink_double()  # TODO nahrad toto blink once when you will have more stable s_distance
            second_next_possible_blink = (s_distance.value - second_next_possible_blink_min)
            last_blinked_class = "second"
            logging.debug('Next_possible_blink_second is :%s', second_next_possible_blink)
            # TODO check maybe where the second  class is ending

    #do drawing on trail_visualization  if second class blink
    xcor=int(Xres + dpi_to_pixels(saw_offset)) + (second_next_possible_blink - s_distance.value + second_next_possible_blink_min)
    if ((blink_second == 1)  and (blink_error == 0)):  # and (last_blinked_class != "second")
        cv2.line(trail_visualization, (xcor, 0), (xcor,int(Yres / scale_trail_visualization)), brown, 2)
        cv2.line(trail_visualization, (xcor + 8, 0), (xcor + 8,int(Yres / scale_trail_visualization)), brown, 2)

    # If First class after second class found
    if (blink_error == 0) and (blink_second == 0) and (
            s_distance.value < second_next_possible_blink) and (last_blinked_class == "second"):
        # check if second class is not at actual Yolo detecetios or on trail before sensor
        print("FFirst:", blink_error, blink_second)
        blink_once()
        last_blinked_class = "first"
    # If First class after second class make drawing on trail_visualization
    if (blink_error == 0) and (blink_second == 0) and (s_distance.value > second_next_possible_blink) and (last_blinked_class == "second"):
        cv2.line(trail_visualization,
                 (int(Xres + dpi_to_pixels(saw_offset)) + (second_next_possible_blink - s_distance.value), 0), (
                     int(Xres + dpi_to_pixels(saw_offset)) + (second_next_possible_blink - s_distance.value),
                     int(Yres / scale_trail_visualization)), green, 2)
        # TODO check if folowing  wood is not contaning any error or second class


    #cv2.line(trail_visualization, (next_possible_blink-s_distance.value,0), (next_possible_blink-s_distance.value,int(Yres/4)), orange, 1)
    cv2.imshow("Trail_visualization", trail_visualization)


def check_on_vysualization_what_to_blick(trail_visualization,objekty,class_to_check,at_what_position_to_check):
    return


blink_error = 0
blink_second = 0
faster_loop2_blikaj_first = 0
error_next_possible_blink = 0
second_next_possible_blink = 0
last_blinked_class = "error"  # need to be set for as if below is checking it
saw_senzor_ofset_from_screen_pixels = int(Xres + dpi_to_pixels(saw_offset))     # in pixels

if __name__=="__main__":
    try:
        check_on_vysialization(draw_trail_visualization(objekty, s_distance),objekty)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)