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

def dpi_to_pixels(dpi):
     return (Xresolution / size_of_one_screen_in_dpi) * dpi

def draw_trail_visualization(objeky,s_distance):
    trail_visualization = np.zeros((int(Yresolution / scale_trail_visualization), Xresolution * 2, 3),
                                   dtype="uint8")
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        if objekty[id].is_detected_by_detector == False:
            visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
            visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
            if objekty[id].category == "error" or objekty[id].category == "eye" or  objekty[id].category == "crack":
                cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                              (int(visualization_xB), int(yB / scale_trail_visualization)), red)
            #else:
            #    cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
            #                  (int(visualization_xB), int(yB / scale_trail_visualization)), green)

        "#TODO draw objects if not detected anymore"

    cv2.imshow("Trail_visualization", trail_visualization)
