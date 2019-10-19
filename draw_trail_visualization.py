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
    """

    :param dpi: angle in dpi which you would like to convert to pixels . It is using global variable size_of_one_screen_in_dpi which is defined in dev_env_wars
    :return: pixels
    """
    return (Xresolution / size_of_one_screen_in_dpi) * dpi

def draw_trail_visualization(objeky,s_distance):
    trail_visualization = np.zeros((int(Yresolution / scale_trail_visualization), Xresolution * 2, 3),
                                   dtype="uint8")
    position_of_saw_senzor = dpi_to_pixels(s_distance.value) + dpi_to_pixels(saw_offset)
    cv2.line(trail_visualization, (int(Xresolution + dpi_to_pixels(saw_offset) ), int(1)), (int(Xresolution + dpi_to_pixels(saw_offset)), int(Yresolution/scale_trail_visualization)), (255, 0, 255), 10)
    for id in objekty:
        xA, yA, xB, yB = convert_from_xywh_to_xAyAxByB_format(objekty[id].bounds)
        #if objekty[id].is_detected_by_detector == False or True:
        #calcculate begining xA and endig xB of rectangle in trai_visualization
        visualization_xA = xA + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        visualization_xB = xB + dpi_to_pixels(objekty[id].position_on_trail) - dpi_to_pixels(s_distance.value)
        #draw error, eye, crack, rot, and crust as red color
        if objekty[id].category == "error" or objekty[id].category == "eye" or objekty[id].category == "crack" or objekty[id].category == "rot" or objekty[id].category == "crust":
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),(int(visualization_xB), int(yB / scale_trail_visualization)), red, 3)
            cv2.putText(trail_visualization, str(objekty[id].position_on_trail), (int(visualization_xA), int(yB / scale_trail_visualization)),cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
        #draw secondclass as brown collor
        elif objekty[id].category == "secondclass" or objekty[id].category == "zapar" or objekty[id].category == "darksecondclass" :
            cv2.rectangle(trail_visualization, (int(visualization_xA), int(yA / scale_trail_visualization)),
                          (int(visualization_xB), int(yB / scale_trail_visualization)), brown, 2)

        elif  visualization_xA < position_of_saw_senzor and visualization_xB > position_of_saw_senzor:
            print ("Blikaj")
            #todo cisla idu do minusu takzetreba prekopat porvnanavanie
    cv2.imshow("Trail_visualization", trail_visualization)
