###################### VARS : ######################################################################################

# set resolution taken from webcam it need to match reality!or relative calculations will not work
#Xresolution = 640  #used for setting input camera resolution
#Yresolution = 480   #used for setting input camera resolution

Xresolution = 1280  #used for setting input camera resolution
Yresolution = 720   #used for setting input camera resolution

#Xresolution = 1920  #used for setting input camera resolution
#Yresolution = 1080  #used for setting input camera resolution

scale_trail_visualization = 4 # how much compact trail visualization heigth
# from where to take a video videofile
video_filename = "test_01-40_03-17_1440x1080.mp4"
#video_filename = "VID_20190711_065005.mp4"
video_filename_path = "/home/automateit/Projects/darknet-alexeyAB/darknet/x64/Release/data/" + video_filename

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
size_of_one_screen_in_dpi = 400 # one screen view in angles , the value need to be calibrated when angle or distance or zoom of camera changes
saw_offset = 50 # saw senzor ofset in dpi (camera field of vision)
objekty = {}  # it is storing all detection from program startup

how_big_object_max_small = 0.9  # detect object from how_big_object_min_small to how_big_object_max_small size of screen
how_big_object_min_small = 0.05 # detect object from how_big_object_min_small to how_big_object_max_small size of screen
#max_dist_of_2nd_edge = 0.4 # max distance of second edge to create rim object
# virtual position of triger relative to camera
#triger_margin = 0.6  # place on screen where it is detecting objects
number_of_deleted_objects = 0 # used  for main is to be deleted
#number_of_max_detection_per_trail = 5  #if more detection on trail firstly detected will be removed

#Yolo configuration for net
"""
object_for_rim_detection = "orange"
object_to_detect = "cell phone"
yolov3_cfg = "cfg/yolov3.cfg"
cat_encoding = "utf-8"
yolov_weights = "weights/yolov3.weights"
obj_data = "cfg/coco.data"
detection_treshold = 0.15
"""

#Alternative configuration for net
#object_for_rim_detection = "edge"
object_to_detect = "error"
cat_encoding = "utf-8"

#yolov3_cfg = "cfg/2019_09_07_yolo-obj_v3.cfg"
#yolov3_cfg = "cfg/2019_12_09_yolo-obj_v3.cfg"
#yolov3_cfg = "cfg/2019_12_24_yolo-obj_v3.cfg"
yolov3_cfg = "cfg/2019_12_22_yolo-obj_v3.cfg"                       #used only by main
#yolov_weights = "weights/2019_03_31_yolo-obj_v3_6904.weights"
#yolov_weights = "weights/2019_09_07_yolo-obj_v3_7139.weights"
#yolov_weights = "weigh ts/2019_12_09_yolo-obj_v3_final.weights"
yolov_weights = "weights/2019_12_22_yolo-obj_v3_18000.weights"      #used only by main

configPath = "./x64/Release/data/2019_12_22_yolo-obj_v3.cfg"    #used only by autowood
weightPath = "./backup/2019_12_22_yolo-obj_v3_18000.weights"    #used only by autowood
metaPath = "./x64/Release/data/obj.data"                        #used only by autowood
network_width = 416
network_heigth = 416

Xres = network_width
Yres = network_heigth

obj_data = "cfg/obj.data"
detection_treshold = 0.3     # percentage which detection to consider

#Colors
black=(0,0,0)
white = (255,255,255)
red = (0,0,255)
green = (0,255,0)
blue = (255, 0, 0)
aqua = (0,255,255)
fuchsia = (255,0,255)
maroon = (128,0,0)
navy = (0,0,128)
olive = (128,128,0)
purple = (128,0,128)
teal = (0,128,128)
yellow = (255,255,0)
azzure = (255, 255, 0)
brown = (19, 69,139)
magenta = (255, 0, 255)
orange =(0, 128, 255)

font_size =0.7              # used for drawing on screen
delay_off_whole_program = 0 # speed of whole program it gives delay to YOLO loop
max_Yobject = 50            # maxinimum amount of objects to keep im memory older than the mentioned number will be deleted
error_next_possible_blink_min = 50   # value in angles from magneto
second_next_possible_blink_min = 100 # value in angles from magneto




