import numpy as np
import cv2
import time
import config as cf


class Contour(object):
    """description of class"""



def find_contours(fg_mask):

    contours,hierarchy = cv2.findContours( fg_mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        #Convert in Contour and remove little ones
        contours=[cnt.view(Contour) for cnt in contours if cv2.contourArea(cnt) > cf.CNT_MIN] #Only keep the big enough
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        return contours
    else :
        return []
