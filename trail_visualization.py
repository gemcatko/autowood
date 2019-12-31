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

def blink_once_double():
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

def draw_trail_visualization(objekty,s_distance):
    start_time = time.time()


    trail_visualization = np.zeros((int(Yres / scale_trail_visualization), Xres * 2, 3),
                                   dtype="uint8")
    saw_senzor_ofset_from_screen_pixels = int(Xres + dpi_to_pixels(saw_offset))
    #draw position of senzor with purple line
    cv2.line(trail_visualization, (int(Xres + dpi_to_pixels(saw_offset) ), int(1)), (int(Xres + dpi_to_pixels(saw_offset)), int(Yres/scale_trail_visualization)), (255, 0, 255), 10)

    cv2.putText(trail_visualization, str(saw_senzor_ofset_from_screen_pixels),(int(Xres + dpi_to_pixels(saw_offset)), int(Yres/scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, 1,
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

        #draw secondclass as brown collor
        if objekty[id].category == "secondclass" or objekty[id].category == "zapar" or objekty[id].category == "darksecondclass" or objekty[id].category == "edge" or objekty[id].category == "darksecondclass" or objekty[id].category == "mark":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), brown, 2)
            cv2.putText(trail_visualization, str(objekty[id].id),
                        (int(visualization_xA), int(yB / scale_trail_visualization)), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (magenta))
    #cv2.imshow("Trail_visualization", trail_visualization)
    end_time = time.time()
    show_fps(start_time, end_time, trail_visualization)
    return trail_visualization

def faster_loop_2(faster_loop2_blikaj_first,s_distance):

    while True:
        start_time_loop = time.time()





        end_time_loop = time.time()
        # check for how long took execution the loop and log if it is too long
        last_loop_duration = end_time_loop - start_time_loop
        #if (last_loop_duration) > 0.010:
            #logging.debug('loopTrigerlistThread duration %s:', end_time_loop - start_time_loop)

def convert_from_xywh_to_xAyAxByB_format(bounds):
    """

    :param bounds: bounds of in format xywh
    :return: return x1x2y1y2  format
    """

    x, y, w, h = bounds
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return box

def check_on_vysialization (trail_visualization,objekty,s_distance):
    global faster_loop2_blikaj_error
    global faster_loop2_blikaj_second
    global next_possible_blink
    global next_possible_blink_second
    global last_blinked_class

    """
    loopa ktra bude stale bezat a bude mat udaj kedy moze ist najblizss dalsi blik
    :param blikaj:
    :param trieda:
    :return: is returning next possible blick
    """

    # fire mark if first on magenta line
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        #draw error, eye, crack, rot, and crust as red color
        if objekty[id].category == "error" or objekty[id].category == "eye" or objekty[id].category == "crack" or objekty[id].category == "rot" or objekty[id].category == "crust" :
            if (visualization_xB > saw_senzor_ofset_from_screen_pixels) and (visualization_xA < saw_senzor_ofset_from_screen_pixels):
                faster_loop2_blikaj_error = 1
                break
            faster_loop2_blikaj_error = 0
            #print ("neblikaj error")

    cv2.putText(trail_visualization, str(faster_loop2_blikaj_error), (int(10), int(30)),
                cv2.FONT_HERSHEY_COMPLEX, 1, red)

    # fire mark if second class on magenta line
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        # calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        if objekty[id].category == "secondclass" or objekty[id].category == "zapar" or objekty[id].category == "darksecondclass" or objekty[id].category == "edge" or objekty[id].category == "darksecondclass" or objekty[id].category == "mark":
            if (visualization_xB > saw_senzor_ofset_from_screen_pixels) and (visualization_xA < saw_senzor_ofset_from_screen_pixels):
                faster_loop2_blikaj_second = 1
                break
            faster_loop2_blikaj_second = 0
    # siganlyze on screen if second class found
    cv2.putText(trail_visualization, str(faster_loop2_blikaj_second), (int(10), int(60)),cv2.FONT_HERSHEY_COMPLEX, 1, brown)
    cv2.imshow("Trail_visualization", trail_visualization)

    # try:
    # needed because qtrigerlist is not always having object inside
    # @TODO tu zisti preco nedava sharovanu value s druheho procesu !!!!!
    # blikaj =  faster_loop2_blikaj_error.value
    # logging.debug("trigerlist%s", blikaj)

    # except:
    # is setting speed of the loop in case 0.0005 it is 2000 times per second
    # except is not executed if qtrigerlist is have data
    # time.sleep(0.0005)

    # if for error
    if (faster_loop2_blikaj_error== 1) and (s_distance.value < next_possible_blink):
        print("Ferror:", faster_loop2_blikaj_error, faster_loop2_blikaj_second)
        blink_once()
        next_possible_blink = (s_distance.value - 50)
        next_possible_blink_second = next_possible_blink
        logging.debug('Next_possible_blink_error is :%s', next_possible_blink)
        last_blinked_class = "error"

    # if for second class
    if ((faster_loop2_blikaj_second == 1) and (s_distance.value < next_possible_blink_second) and (
            faster_loop2_blikaj_error == 0)):  # and (last_blinked_class != "second")
        print("FSecond:", faster_loop2_blikaj_error, faster_loop2_blikaj_second)
        blink_once_double()  # TODO nahrad toto blink once when you will have more stable s_distance
        next_possible_blink_second = (s_distance.value - 100)
        last_blinked_class = "second"
        logging.debug('Next_possible_blink_second is :%s', next_possible_blink_second)
        # TODO check maybe where the second  class is ending

    # If first class
    if (faster_loop2_blikaj_error == 0) and (faster_loop2_blikaj_second == 0) and (
            s_distance.value < next_possible_blink_second) and (last_blinked_class == "second"):
        print("FFirst:", faster_loop2_blikaj_error, faster_loop2_blikaj_second)
        blink_once()
        last_blinked_class = "first"
        # TODO check if folowing  wood is not contaning any error or second class

def show_fps(start_time, end_time,name_of_frame):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(name_of_frame, str(FPS), (int(Xres*2 - 80), int(Yres/4 - 10)), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 100, 255))
    #print(FPS)
    return FPS

faster_loop2_blikaj_error = 0
faster_loop2_blikaj_second = 0
faster_loop2_blikaj_first = 0
next_possible_blink = 0
next_possible_blink_second = 0
last_blinked_class = "error"  # need to be set for as if below is checking it
saw_senzor_ofset_from_screen_pixels = int(Xres + dpi_to_pixels(saw_offset))

if __name__=="__main__":
    try:
        # print ("#draw_trail_visualization(objekty, s_distance)")
        # draw_trail_visualization(objekty, s_distance)
        check_on_vysialization(draw_trail_visualization(objekty, s_distance),objekty)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)