
import numpy as np
import cv2 as cv
import time

cap = cv.VideoCapture(0)
codec	=	cv.VideoWriter_fourcc(	"M", "J", "P", "G"	)
cap.set(cv.CAP_PROP_FPS, 60)           # FPS60FPS
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280) # set resolutionx1280
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720) # set resolutiony720
cap.set(cv.CAP_PROP_FOURCC,codec)

print(cap.get(cv.CAP_PROP_FPS))
print(cap.get(cv.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

def show_fps(start_time, end_time):
    duration_of_loop = end_time - start_time
    FPS = round(1 / duration_of_loop, 1)
    print(FPS)
    #cv.putText(frame, str(FPS), (int(Xresolution - 80), int(Yresolution - 40)), cv.FONT_HERSHEY_COMPLEX, 1,(255, 100, 255))
    return FPS

while(True):
    start_time =time.time()
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv.imshow('frame',gray)
    end_time = time.time()
    show_fps(start_time, end_time)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()