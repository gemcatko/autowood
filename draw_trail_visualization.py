import numpy as np
import cv2


from dev_env_vars import *
def convert_from_xywh_to_xAyAxByB_format(bounds):
    """

    :param bounds: bounds of in format xywh
    :return: return x1x2y1y2  format
    """

    x, y, w, h = bounds
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return box



def draw_trail_visualization(objeky,s_distance):
    trail_visualization = np.zeros((int(Yresolution / scale_trail_visualization), Xresolution * 2, 3),
                                   dtype="uint8")
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #xA = xA + objekty[id].position_on_trail
        #xB = xB + objekty[id].position_on_trail
        xA = xA + (objekty[id].position_on_trail / size_of_one_screen_in_dpi * Xresolution)
        xB = xB + (objekty[id].position_on_trail / size_of_one_screen_in_dpi * Xresolution)
        if objekty[id].category == "error":
            cv2.rectangle(trail_visualization, (int(xA), int(yA / scale_trail_visualization)),
                          (int(xB), int(yB / scale_trail_visualization)), red)
        else:
            cv2.rectangle(trail_visualization, (int(xA), int(yA / scale_trail_visualization)),(int(xB), int(yB / scale_trail_visualization)), green)
    cv2.imshow("Trail_visualization", trail_visualization)
