import time
import traceback
import sys
from pydarknet import Detector, Image
import cv2
import logging

Xresolution = 640
Yresolution = 480

def chyba_one_mark_small(cat, score, x, y, w, h, ):
    catdecoded = cat.decode("utf-8")
    x_norm, y_norm, w_norm, h_norm,volume_norm = calculate_volume(x, y, w, h)
    if catdecoded == "cell phone" and w_norm <= 0.3:

        #left line from camera view at object green
        cv2.line(frame, (int(x-w/2),int(y-h/2)),(int(x-w/2),int(y+h/2)),(0,128,0),10,10)
        #right line_from camera view at object orange
        cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(0,128,255),10,10)
        #print(int(x_norm + w_norm/2))
        #print(x_norm + w_norm/2)
        # test na zaciatok vychadzania detekovane objektu zo zaberu. Test v 90% obrazovej plochy
        if (x_norm + w_norm/2) > 0.90:
            print("sprav znacku zaciatok koniec ")
            cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,255),10)
            pass
    else:
        pass

def calculate_volume(x,y,w,h):
    x_norm = x / Xresolution
    y_norm = y / Yresolution
    w_norm = w / Xresolution
    h_norm = h / Yresolution
    volume_norm = w_norm * h_norm
    return x_norm, y_norm, w_norm, h_norm,volume_norm


if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)

    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0, bytes("cfg/coco.data", encoding="utf-8"), )
    #net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    cap = cv2.VideoCapture(0)

    while True:
        r, frame = cap.read()
        if r:
            start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            #This are the function parameters of detect:
            #def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.1)
            del dark_frame
            end_time = time.time()
            #print("Elapsed Time:",end_time-start_time)
            #print(results)

            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                chyba_one_mark_small(cat, score, x, y, w, h, )
            cv2.imshow("preview", frame)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break