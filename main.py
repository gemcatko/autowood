import time
import traceback
import sys
from pydarknet import Detector, Image
import cv2
import logging
import weakref

Xresolution = 640
Yresolution = 480
cell_phone = []
list_chyba = []
field_of_view = 40 #field of view in cm for camera
x_norm_last = 0
y_norm_last = 0
move_treshold = 0.05
idd= 0

#TODO how to triger saw https://www.sick.com/es/en/registration-sensors/luminescence-sensors/lut9/lut9b-11626/p/p143229  (light? maybe) SEMI TRANSPARENT GLASS WITH WARM WHITE LED OR red light
#TODO Solve how to triger sensor from code? => https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup check if possible with python 3
#TODO give objecs uniqe ID
#TODO calculate speed of objects
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
        ("Je to ten isty object:   dif:", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last), x_norm,x_norm_last )
        pass
    if (abs(x_norm - x_norm_last ) > 0.05) or (abs(y_norm - y_norm_last) > 0.05):
        ("nie je  ten isty objekt  ", abs(x_norm - x_norm_last), abs(y_norm - y_norm_last), x_norm,x_norm_last)
        pass

    x_norm_last = x_norm
    y_norm_last = y_norm
    pass

def get_uniqe_id2(cat , score, x , y , w , h):
    x_norm_last, y_norm_last, w_norm_last, h_norm_last ,volume_norm_last = calculate_volume_norm(x, y, w, h)
    cell_phone.append(Object(cat,score, x, y, w, h))
    print("len(cell_phone)",len(cell_phone))
    #for i in range(len(cell_phone)-1):
        #cell_phone[i].is_it_old(i)
     #   cell_phone[i].is_near_by_object(x_norm_last, y_norm_last)
        #TODO  na tom to to pada cell_phone[i].is_near_by_object(x_norm_last, y_norm_last)
    cell_phone[len(cell_phone)-1].is_near_by_object2()



    pass

def for_cyklus(cat , score, x , y , w , h):
    for i in range(len(cell_phone)):
        if (cell_phone[i].is_near_by_object()) == True:
            #delete last created object in cell_phone[]
            del cell_phone [-1]
            Object.id = Object.id -1
        break
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

class Object:
    id = -1
    global y_norm_last
    global x_norm_last
    #x_norm_last = 0
    #y_norm_last = 0
    def __init__(self, cat, score, x, y, w, h):
        self.cat = cat
        self.score = score
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_norm = x / Xresolution
        self.y_norm = y / Yresolution
        Object.id += 1
        self.id = Object.id
        self.creation_time=time.time()
    def smakes(self):
        return '{} {}'.format(self.x, "smakes")

    def is_near_by_object(self,x_norm_last,y_norm_last):
        #if (abs(self.x_norm - Object.x_norm_last ) <= 0.05) and (abs(self.y_norm - Object.y_norm_last) <= 0.05):
        if (abs(self.x_norm - x_norm_last ) <= 0.05) and (abs(self.y_norm - y_norm_last) <= 0.05):
            print("Je to ten isty object:dif:", abs(self.x_norm - x_norm_last), abs(self.y_norm - y_norm_last), " ako id:", self.id)
            #Object.x_norm_last = self.x_norm
            #Object.y_norm_last = self.y_norm
            del cell_phone [-1]
            Object.id = Object.id -1
            return True
        else:
            print("Nie je to ten isty object:dif:", abs(self.x_norm - x_norm_last), abs(self.y_norm - y_norm_last), " ako id:", self.id )
            #Object.x_norm_last = self.x_norm
            #Object.y_norm_last = self.y_norm
            self.is_it_old()
            return False

    def is_near_by_object2(self):
            if (abs(self.x_norm - cell_phone[i].x_norm) <= 0.1) :
                print("najdeny objekt", abs(self.x_norm - cell_phone[i].x_norm))
                print("self.x_norm", abs(self.x_norm))
                print("cell_phone[i].x_norm", cell_phone[i].x_norm)
                #cell_phone[i].x_norm = self.x_norm
                cell_phone[i] = cell_phone.pop()
                return True
            else:
                print("nee_najdeny", abs(self.x_norm - cell_phone[i].x_norm))
                return False
            pass

class Chyba:
    _instances = set()
    def __init__(self,idd, cat, score, x_norm, y_norm, w_norm, h_norm):
        self.idd = idd
        self.cat = cat
        self.score = score
        self.x_norm = x_norm
        self.y_norm = y_norm
        self.w_norm = w_norm
        self.h_norm = h_norm
        self.creation_time=time.time()
        self._instances.add(weakref.ref(self))
        #self.idd = Chyba.idd
        pass

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

def count_objects_in_frame(object_to_check):
    number_of_object_to_check = 0
    for cat, score, bounds in results:
        if cat.decode("utf-8") == object_to_check:
            number_of_object_to_check = number_of_object_to_check + 1
    return  number_of_object_to_check

def hokus_pokus():
    global idd
    if int(count_objects_in_frame('cell phone')) == 1:
        if str(cat.decode("utf-8")) == "cell phone":

            x_norm, y_norm, w_norm, h_norm, volume_norm = calculate_volume_norm(x, y, w, h)
            idd = idd + 1
            list_chyba.append(Chyba(idd,cat,score,x_norm, y_norm, w_norm, h_norm))
            for i in range(len(list_chyba)-1):
                if (abs(list_chyba[i].x_norm - list_chyba[len(list_chyba)-1].x_norm) <= move_treshold):
                    # obj.update_pos
                    if (len(list_chyba) > 1) and (len(list_chyba) < 3):
                        print("idd:",list_chyba[i].idd,"len(list_chyba)",len(list_chyba),"nearby",list_chyba[i].cat,abs(list_chyba[i].x_norm - list_chyba[len(list_chyba)-1].x_norm))
                        list_chyba[i].cat, list_chyba[i].score, list_chyba[i].x_norm, list_chyba[i].y_norm, list_chyba[i].w_norm, list_chyba[i].h_norm = list_chyba[len(list_chyba)-1].cat, list_chyba[len(list_chyba)-1].score, list_chyba[len(list_chyba)-1].x_norm, list_chyba[len(list_chyba)-1].y_norm, list_chyba[len(list_chyba)-1].w_norm, list_chyba[len(list_chyba)-1].h_norm
                        del list_chyba[len(list_chyba)-1]
                        idd = idd - 1
                    if (len(list_chyba)) >= 3:
                        print("idd:", list_chyba[i].idd, "len(list_chyba)", len(list_chyba), "not nearby",
                              list_chyba[i].cat, abs(list_chyba[i].x_norm - list_chyba[len(list_chyba) - 1].x_norm))
                        del list_chyba[len(list_chyba)-1]

if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)
    net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"), bytes("weights/yolov3.weights", encoding="utf-8"), 0, bytes("cfg/coco.data", encoding="utf-8"), )
    #net = Detector(bytes("cfg/2018_12_15_yolo-obj.cfg", encoding="utf-8"), bytes("weights/2018_12_15_yolo-obj_2197.backup", encoding="utf-8"), 0, bytes("cfg/obj.data", encoding="utf-8"), )
    cap = cv2.VideoCapture(0)

    while True:
        r, frame = cap.read()
        if r:
            #start_time = time.time()
            # Only measure the time taken by YOLO and API Call overhead
            dark_frame = Image(frame)
            #This are the function parameters of detect:
            #def detect(self, Image image, float thresh=.5, float hier_thresh=.5, float nms=.45):
            results = net.detect(dark_frame, thresh=.1)
            del dark_frame
            
            for cat, score, bounds in results:
                x, y, w, h = bounds
                cv2.rectangle(frame, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,0))
                cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
                chyba_one_mark_small(cat, score, x, y, w, h, )
                cv2.putText(frame, str(count_objects_in_frame("cell phone")), (int(Xresolution - 50), int(Yresolution - 50)), cv2.FONT_HERSHEY_COMPLEX, 1, (150, 150,150))

                #hokus_pokus()

            cv2.imshow("preview", frame)
            #print(results)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break