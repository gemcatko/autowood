#https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
#https: // www.pyimagesearch.com / 2015 / 12 / 21 / increasing - webcam - fps -with-python - and -opencv /
# import the necessary packages
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class YObject:
    # z Yola ide odresult a v idrusulte su id, cat, score, bounds
    # def __init__(self, centroid_id, category, score, bounds):
    def __init__(self, id, category, score, bounds):
        # co vychadza z jola [(1, b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (4, b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]

        # centroid_id , detected_category, score, object_position_center_x ,object_position_center_y ,width w, height_h
        # copy paste functionality of  detect_object_4_c
        self.id = id
        self.category = category
        self.score = score
        self.bounds = bounds
    def show_objects(self):
        print("bounds:",self.id, self.category, self.score, self.bounds)

    def detect_object_4_cm(self, object_to_detect):

        ##chnage format to utf-8### object_to_check ## how width ########### where is triger margin################### check if is not id.1 already in in triger list
        if self.category.decode("utf-8") == object_to_detect:
            print("object_to_detect:",object_to_detect)
            logging.debug('mas tam pesonu')

trigerlist = [(4.1, 1551555880.4178755, 4.2, 1551555880.576961), (11.1, 1551555884.1779869, 11.2, 1551555884.252769), (5.1, 1551555885.0371258, 5.2, 1551555885.2632303)]

idresults= [(1, b'person', 0.9972826838493347, (646.4600219726562, 442.1628112792969, 1113.6322021484375, 609.4992065429688)), (4, b'bottle', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422)),(5, b'notebook', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
"""
id_begining = 11.1
time_begining = 1551555884.1779869
id_ending = 11.2
time_ending = 1551555884.252769
new_time_begining = 1.111111
new_time_ending = 1.99999

print(trigerlist[1])
trigerlist[1] = id_begining, new_time_begining, id_ending, new_time_ending
print(trigerlist[1])
print(trigerlist.index((id_begining, new_time_begining, id_ending, new_time_ending)))
"""
object_to_detect = "person"
objekty = {}
for id, category, score, bounds in idresults:
    objekty[id] = YObject(id, category, score, bounds)
    objekty[id].show_objects()


idresults= [(1, b'person', 0.11111, (111.4600219726562, 1111.1628112792969, 1111.6322021484375, 111.4992065429688)), (4, b'bottle', 0.44444, (44444.3851318359375, 4444.22744750976562, 444.9032287597656, 444.8708953857422)),(5, b'notebook', 0.5920438170433044, (315.3851318359375, 251.22744750976562, 298.9032287597656, 215.8708953857422))]
for id, category, score, bounds in idresults:
    objekty[id] = YObject(id, category, score, bounds)
    objekty[id].show_objects()
    objekty[id].detect_object_4_cm(object_to_detect)

    print(objekty[id].id)

for k, v in objekty.items():
    print( f"key: {k} value: {v}" )



