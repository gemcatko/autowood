from dev_env_vars import *
from pydarknet import Detector, Image
import cv2
from dev_env_vars import *
import time
import multiprocessing
from multiprocessing import Process, Value, Queue

def show_fps(start_time, end_time):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    cv2.putText(frame, str(FPS), (int(Xresolution - 80), int(Yresolution - 40)), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 100, 255))
    return FPS


def darknet(yolov3_cfg, yolov_weights, cat_encoding, obj_data, q_picture):

    net = Detector(bytes(yolov3_cfg, encoding=cat_encoding), bytes(yolov_weights, encoding=cat_encoding), 0,
                   bytes(obj_data, encoding=cat_encoding), )
    while True:
        try:
            dark_frame = q_picture.get()
            results = net.detect(dark_frame, thresh=detection_treshold)

        except:
            print("exeption in darknet ocured")




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
    p = Process(target=darknet, args=(yolov3_cfg, yolov_weights, cat_encoding, obj_data,q_picture,))
    p.start()



    ########################## MAIN LOOP ###############################################################################

    while True:
        start_time=time.time()
        r, frame = cap.read(0)
        if r:
            # start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            q_picture.put(dark_frame)
            # This are the function parameters of detect:
            # Possible inputs: def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            # call Yolo34
            #results = net.detect(dark_frame, thresh=detection_treshold)
            del dark_frame
        #cv2.imshow("preview", frame)
        # print("Elapsed Time:",end_time-start_time)
        k = cv2.waitKey(1)
        end_time=time.time()
        show_fps(start_time,end_time)
        cv2.imshow("preview", frame)
        if k == 0xFF & ord("q"):
            break


