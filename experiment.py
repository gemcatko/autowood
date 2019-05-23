#####Prerequzities
#sudo mount -t tmpfs -o rw,size=500M tmpfs /mnt/ramdisk

from dev_env_vars import *
from pydarknet import Detector, Image
import cv2
from dev_env_vars import *
import time
import multiprocessing
from multiprocessing import Process, Value, Queue
import os


import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )

def show_fps(start_time, end_time):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(frame, str(FPS), (int(Xresolution - 80), int(Yresolution - 40)), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 100, 255))
    return FPS


def darknet(yolov3_cfg, yolov_weights, cat_encoding, obj_data, ):

    net = Detector(bytes(yolov3_cfg, encoding=cat_encoding), bytes(yolov_weights, encoding=cat_encoding), 0,
                   bytes(obj_data, encoding=cat_encoding), )
    while True:
        if check_if_image_complete("/mnt/ramdisk/","frame.jpg"):
            read_frame = cv2.imread("/mnt/ramdisk/frame.jpg")
            dark_frame = Image(read_frame)
            results = net.detect(dark_frame, thresh=detection_treshold)
            print("Results:", results)
            del dark_frame


def check_handle(path_file_to_check):
    f = path_file_to_check
    if os.path.exists(f):
        try:
            os.rename(f, f)
            print('Access on file "' + f + '" is available!')
            return True
        except OSError as e:
            print('Access-error on file "' + f + '"! \n' + str(e))
            return False

def check_if_image_complete(path,file):
    path = path
    file = file

    with open(os.path.join(path, file), 'rb') as f:
        check_chars = f.read()[-2:]
    if check_chars != b'\xff\xd9':
        print('Not complete image')
        return False
    else:
        #imrgb = cv2.imread(os.path.join(path, file), 1)
        return True



if __name__ == "__main__":

    ################################ SETUP #############################################################################
    """"""
    cap = cv2.VideoCapture(0)  # set web cam properties width and height, working for USB for webcam
    # video_filename = "MOV_2426.mp4"                                        # use if you want to use static video file
    # cap = cv2.VideoCapture(video_filename)
    cap.set(3, Xresolution)
    cap.set(4, Yresolution)

    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    #net = Detector(bytes(yolov3_cfg, encoding=cat_encoding), bytes(yolov_weights, encoding=cat_encoding), 0, bytes(obj_data, encoding=cat_encoding), )

    q_picture = multiprocessing.Queue()
    q_results = multiprocessing.Queue()
    p = Process(target=darknet, args=(yolov3_cfg, yolov_weights, cat_encoding, obj_data,))
    p.start()
    ########################## MAIN LOOP ###############################################################################

    while True:
        start_time=time.time()
        r, frame = cap.read(0)
        if r:
            # start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            cv2.imwrite("/mnt/ramdisk/frame.jpg", frame)
            ##read_frame = cv2.imread("/mnt/ramdisk/frame.jpg")
            ##dark_frame = Image(read_frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            # call Yolo34
            ##results = net.detect(dark_frame, thresh=detection_treshold)
            ##print("Results:",results)
            """

            try:
                print("q_results:",q_results.get_nowait())
            except:
                time.sleep(0.01)
                print("exeption in main tread ecored")

            ##del dark_frame
            """
        #cv2.imshow("preview", frame)
        # print("Elapsed Time:",end_time-start_time)

        k = cv2.waitKey(1)
        end_time=time.time()
        show_fps(start_time,end_time)
        cv2.imshow("preview", frame)
        if k == 0xFF & ord("q"):
            break


