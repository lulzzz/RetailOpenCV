import cv2
import numpy as np
from datetime import datetime
from random import randint
import os
import time

'''
'
'  CONFIG DATA
'
'''

#donnee generales partagees

T_START = time.time()

FONT = cv2.FONT_HERSHEY_SIMPLEX
ANOTATION_COLOR = (0,255,0)

to_be_sent = []


#API endpoints
API_GET_CAM_ID = ""
API_POST_RESULTS = ""

OUTPUTFILE = fichier = open("out.json", "w")

def get_camera_id():
    '''
    res = requests.get(cf.API_GET_CAM_ID)
    if res.status_code == 200:
        return res.json()['id']
    '''
    return 'test'

CAMERA_ID = get_camera_id()

#Aquisition

MAX_LONGER_SIDE = 960

#Filled at init source in order to determine limits and min/max sizes
CURRENT_FRAME_SIZE = 0


#Forground Extraction Config

ALGO = 2
LR = 0.0015

TRAIN_FRAMES = 300


# Operateurs morphologiques

FG_O_OP=4    #10 #opening
FG_C_OP=8    #15 #closing

STR_ELEMENT=cv2.MORPH_ELLIPSE



o_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_O_OP,FG_O_OP))
c_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_C_OP,FG_C_OP))  


#Contour detection
CNT_MIN = 100


#Person criteria
'''
MAX_DIST_CENTRE = 180
MAX_PERS_SIZE = 300
MIN_PERS_SIZE = 50
'''
MIN_SIZE_CNT = 100


MAX_DIST_CENTER_X = 180
MAX_DIST_CENTER_Y = 180

MAX_PERS_SIZE_X = 250
MAX_PERS_SIZE_Y = 300

MIN_PERS_SIZE_X = 40
MIN_PERS_SIZE_Y = 80



ALPHA = 0.5


DIR_ZONES = "/Users/Olivier/GitHub/Retail/chute/zones"