import time
import traceback
import sys
from pydarknet import Detector, Image
import cv2
import logging

Xresolution = 640
Yresolution = 480
id=0
cell_phone = []
field_of_view = 40 #field of view in cm for camera
x_norm_last = 0
y_norm_last = 0

#TODO how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light
#TODO Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3
#TODO give objecs uniqe ID
#TODO calculate sped of objects
#TODO Show found erros with ID on separate screen


def chyba_one_mark_small(cat, score, x, y, w, h, ):
    catdecoded = cat.decode("utf-8")
    x_norm, y_norm, w_norm, h_norm,volume_norm = calculate_volume_norm(x, y, w, h)
    #W_norm is used_for triger how big error to detect
    if catdecoded == "cell phone" and w_norm <= 1:
        #left line from camera view at object green
        cv2.line(frame, (int(x-w/2),int(y-h/2)),(int(x-w/2),int(y+h/2)),(0,128,0),10,10)
        #right line_from camera view at object orange
        cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(0,128,255),10,10)
        is_near_by_object(cat, score, x, y, w, h)
        get_uniqe_id2(cat,score, x, y, w, h)
        #test na zaciatok vychadzania detekovane objektu zo zaberu. Test v 90% obrazovej plochy
        if (x_norm + w_norm/2) > 0.90:
            print("sprav znacku zaciatok koniec ")
            cv2.line(frame, (int(x+w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,255),10)
            pass
    else:
        pass

def is_near_by_object (cat, score, x, y, w, h):
    global x_norm_last
    global y_norm_last

    x_norm = x / Xresolution
    y_norm = y / Yresolution

    if (abs(x_norm - x_norm_last ) <= 0.05) and (abs(y_norm - y_norm_last) <= 0.05):
        print("Je to ten isty object:dif:", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last))

    if (abs(x_norm - x_norm_last ) > 0.05) or (abs(y_norm - y_norm_last) > 0.05):
        print("nie je  ten isty objekt  ", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last))
        get_uniqe_id2(cat, score, x, y, w, h)

    x_norm_last = x_norm
    y_norm_last = y_norm
    pass

def get_uniqe_id2(cat , score, x , y , w , h):
    cell_phone.append(Object(cat,score, x, y, w, h))
    #print(cell_phone[(len(cell_phone)-1)].x_norm)
    pass

def calculate_velocity (id, x, y, w, h ):
    #
    pass


def calculate_volume_norm(x, y, w, h):
    x_norm = x / Xresolution
    y_norm = y / Yresolution
    w_norm = w / Xresolution
    h_norm = h / Yresolution
    volume_norm = w_norm * h_norm
    return x_norm, y_norm, w_norm, h_norm,volume_norm

class Employee:
    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay
        self.email = first + '.' + last + '@company.com'
    def fullname(self):
        return '{} {}'.format(self.first, self.last)

emp_1 = Employee('Marek','Solcanky', 60000 )
emp_2 = Employee('Gem','Sol', 30000 )

print(emp_1.email)
print(emp_2.email)
print(emp_1.fullname())

class Object:
    def __init__(self,cat,score, x, y, w, h):
        self.cat = cat
        self.score = score
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_norm = x / Xresolution
        self.y_norm = y / Yresolution
    def smakes(self):
        return '{} {}'.format(self.x, "smakes")
    def update_x_y(self):
        if (abs(self.x_norm - self.x_norm_last ) <= 0.05) and (abs(self.y_norm - self.y_norm_last) <= 0.05):
            print("Je to ten isty object:dif:", abs(self.x_norm - self.x_norm_last), abs(self.y_norm - self.y_norm_last))
        pass

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
            print(results)
            #print(results.cat.count("b'cell phone"))

            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                chyba_one_mark_small(cat, score, x, y, w, h, )



            cv2.imshow("preview", frame)
            #print(results)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break