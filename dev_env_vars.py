###################### VARS : ######################################################################################

# set resolution taken from webcam it need to match reality!or relative calculations will not work
#Xresolution = 640
#Yresolution = 480

Xresolution = 640
Yresolution = 480

cell_phone = []
list_chyba = []
# Used by pLoopTrigerlist  to communicate with main loop format is [(2.1, 1551338571.7396123, 2.2, 1551338571.9881353), (3.1, 1551338578.9405866, 3.2, 1551338579.1024451), (0.1, 1551338586.2836142, 0.2, 1551338586.4773874)]
trigerlist = []
idresults = []
# Used by pLoopTrigerlist  to confirm object was marked  format is [(2.1, 1551338571.7396123), (2.2, 1551338571.9881353), (3.1, 1551338578.9405866), (3.2, 1551338579.1024451), (0.1, 1551338586.2836142), (0.2, 1551338586.4773874)]
#fastTrigerList shall be deleted in future releases
alreadyBlinkedTriger =[]
alreadyBlinkedList = []
#field_of_view = 0.3  # field of view in m for camera
#x_norm_last = 0
#y_norm_last = 0
size_of_one_screen_in_dpi = 150
delay = 1  # time in s to delay marking, can be use to set distance of sensing camera from BliknStick.
saw_offset = 150
objekty = {}  # it is storing all detection from program startup

how_big_object_max_small = 0.9  # detect object from how_big_object_min_small to how_big_object_max_small size of screen
how_big_object_min_small = 0.05 # detect object from how_big_object_min_small to how_big_object_max_small size of screen
distance_of_second_edge = 0.4 # max distance of second edge to create rim object
# virtual position of triger relative to camera
triger_margin = 0.6  # place on screen where it is detecting objects

#Yolo configuration for net
object_for_rim_detection = "orange"
object_to_detect = "cell phone"
yolov3_cfg = "cfg/yolov3.cfg"
cat_encoding = "utf-8"
yolov_weights = "weights/yolov3.weights"
obj_data = "cfg/coco.data"
detection_treshold = 0.5


#Alternative configuration for net
#object_for_rim_detection = "edge"
#object_to_detect = "error"
#yolov3_cfg = "cfg/2019_03_31_yolo-obj_v3.cfg"
#cat_encoding = "utf-8"
#yolov_weights = "weights/2019_03_31_yolo-obj_v3_7000.weights"
##obj_data = "cfg/obj.data"
#detection_treshold = 0.30

