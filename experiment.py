#https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
#https: // www.pyimagesearch.com / 2015 / 12 / 21 / increasing - webcam - fps -with-python - and -opencv /
# import the necessary packages

trigerlist = [(4.1, 1551555880.4178755, 4.2, 1551555880.576961), (11.1, 1551555884.1779869, 11.2, 1551555884.252769), (5.1, 1551555885.0371258, 5.2, 1551555885.2632303)]

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