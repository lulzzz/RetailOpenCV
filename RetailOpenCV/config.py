import cv2
import numpy as np
from datetime import datetime
from random import randint
import os
import time



'''
'
'  VIDEO SOURCE
'
'''

VIDEO_SOURCE = " http://96.10.1.168/mjpg/video.mjpg"

VIDEO_SOURCE = 0

#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute10\\cam2.avi"

VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\street\\01\\street960.mp4"

#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute22\\cam2.avi"

VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\GitHub\\RetailOpenCV\\dataset\\lego\\04\\lego960.mp4"

#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\ComputerVision_Detect_Body\\videoset\\chute16\\cam2.avi"

#VIDEO_SOURCE = 1

#VIDEO_SOURCE="C:\\Users\\Olivier Staub\\Pictures\\Camera Roll\\WIN_20170314_17_59_20_Pro.mp4"

#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\footage\\ex1.mp4"
#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\footage\\cafet.MOV"
#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\footage\\cafet2.mp4"
#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\footage\\foot1.mp4"


#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\footage\\cafet2.mp4"
#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\footage\\cafet.mov"


#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\street\\01\\street960.mp4"


#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\chute\\23\\cam2.avi"
#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\chute\\02\\cam2.avi"
#VIDEO_SOURCE="C:\\Users\\Olivier\\Documents\\retail\\chute\\14\\cam3.avi"


#VIDEO_SOURCE = "/Users/Olivier/GitHub/Retail/chute/01/cam8.avi"
#VIDEO_SOURCE = "/Users/Olivier/GitHub/Retail/footage/cafet2.mp4"

SET_WEBCAM_WIDTH = 960
SET_WEBCAM_HEIGHT = 540



'''
'
'  ZONES DIRECTORY
'
'''

DIR_ZONES = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\zones"
DIR_ZONES = "C:\\Users\\Olivier-Laforge\\Documents\\GitHub\\RetailOpenCV\\dataset\\zones"
#DIR_ZONES = "/Users/Olivier/GitHub/Retail/chute/zones"
#DIR_ZONES=""

#DIR_ZONES = "C:\\Users\\Olivier\\Documents\\retail\\RetailOpenCV\\dataset\\zones"



'''
'
'  API CONFIG
'
'''

SEND_DATA = False
API_GET_CAM_ID = ""
API_POST_RESULTS = "http://cargo-hub.azurewebsites.net/api/hublog/notify"
API_DEBUG = True
API_SLEEP_TIME=5
OUTPUTFILE = open("out.json", "w")

LOGO_FILE = "logo.png"
INIT_FILE = "init.png"


'''
'
'  DRAWING CONFIG
'
'''
DRAW_CONFIG = True
DRAW_ZONES = True
DRAW_PERSONS = True
DRAW_PERSON_PATH_TAIL = True
DRAW_PERSON_PATH_TAIL_LENGTH = 400




#donnee generales partagees

T_START = time.time()

FONT = cv2.FONT_HERSHEY_SIMPLEX

ANOTATION_COLOR = (0,255,0)
BORDER_BACKGROUND_COLOR = (0,0,0)
BORDER_TEXT_COLOR = (0,0,0  )

to_be_sent = []



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
LR = 0.002

TRAIN_FRAMES = 200


# Operateurs morphologiques

FG_O_OP=3    #10 #opening
FG_C_OP=5    #15 #closing

STR_ELEMENT=cv2.MORPH_ELLIPSE

o_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_O_OP,FG_O_OP))
c_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_C_OP,FG_C_OP))  


#Minimum contour size for detection
'''
MAX_DIST_CENTRE = 180
MAX_PERS_SIZE = 300
MIN_PERS_SIZE = 50
'''
'''
CNT_MIN = 0
MIN_SIZE_CNT_PERS = 0

MAX_DIST_CENTER_X = 0
MAX_DIST_CENTER_Y = 0

MAX_PERS_SIZE_X = 0
MAX_PERS_SIZE_Y = 0

MIN_PERS_SIZE_X = 0
MIN_PERS_SIZE_Y = 0
'''
''' Chutes Config '''
'''
CNT_MIN = 30
MIN_SIZE_CNT_PERS = 30

MAX_DIST_CENTER_X = 160
MAX_DIST_CENTER_Y = 210

MAX_PERS_SIZE_X = 280
MAX_PERS_SIZE_Y = 340

MIN_PERS_SIZE_X = 30
MIN_PERS_SIZE_Y = 50
'''

''' Lego Config '''

CNT_MIN = 20
MIN_SIZE_CNT_PERS = 20

MAX_DIST_CENTER_X = 60
MAX_DIST_CENTER_Y = 30

MAX_PERS_SIZE_X = 220
MAX_PERS_SIZE_Y = 150

MIN_PERS_SIZE_X = 5
MIN_PERS_SIZE_Y = 10



''' Live config '''

'''
CNT_MIN = 5
MIN_SIZE_CNT_PERS = 5

MAX_DIST_CENTER_X = 50
MAX_DIST_CENTER_Y = 50

MAX_PERS_SIZE_X = 300
MAX_PERS_SIZE_Y = 200

MIN_PERS_SIZE_X = 5
MIN_PERS_SIZE_Y = 5
'''

ACTIVE_CONFIG_SET = "lego"

config_set = {}
        
config_set['chute'] = {
                'CNT_MIN': 30,
                'MIN_SIZE_CNT_PERS': 30,
                'MAX_DIST_CENTER_X': 160,
                'MAX_DIST_CENTER_Y': 210,
                'MAX_PERS_SIZE_X': 280, 
                'MAX_PERS_SIZE_Y': 340,
                'MIN_PERS_SIZE_X': 30,
                'MIN_PERS_SIZE_Y': 50 
            }

config_set['lego'] = {
                'CNT_MIN': 5,
                'MIN_SIZE_CNT_PERS': 10,
                'MAX_DIST_CENTER_X': 60,
                'MAX_DIST_CENTER_Y': 30,
                'MAX_PERS_SIZE_X': 220, 
                'MAX_PERS_SIZE_Y': 150,
                'MIN_PERS_SIZE_X': 5,
                'MIN_PERS_SIZE_Y': 10 
            }

config_set['livefeed'] = {
                'CNT_MIN': 5,
                'MIN_SIZE_CNT_PERS': 5,
                'MAX_DIST_CENTER_X': 50,
                'MAX_DIST_CENTER_Y': 50,
                'MAX_PERS_SIZE_X': 300, 
                'MAX_PERS_SIZE_Y': 200,
                'MIN_PERS_SIZE_X': 5,
                'MIN_PERS_SIZE_Y': 5
            }


def add_config_set(VideoSource, cnt_min, min_size_cnt_pers, max_dist_center_x, max_dist_center_y, max_pers_size_x, max_pers_size_y, min_pers_size_x, min_pers_size_y):
    temp = {}
        
    temp['CNT_MIN'] = cnt_min
    temp['MIN_SIZE_CNT_PERS'] = min_size_cnt_pers

    temp['MAX_DIST_CENTER_X'] = max_dist_center_x
    temp['MAX_DIST_CENTER_Y'] = max_dist_center_y

    temp['MAX_PERS_SIZE_X'] = max_pers_size_x
    temp['MAX_PERS_SIZE_Y'] = max_pers_size_y

    temp['MIN_PERS_SIZE_X'] = min_pers_size_x
    temp['MIN_PERS_SIZE_Y'] = min_pers_size_y

    config_set.append(temp)


def apply_config_set(setname, videoDim):
    width, height = videoDim
    if config_set[setname]:
        CNT_MIN = config_set[setname]['CNT_MIN']
        MIN_SIZE_CNT_PERS = config_set[setname]['MIN_SIZE_CNT_PERS']
        MAX_DIST_CENTER_X = config_set[setname]['MAX_DIST_CENTER_X']
        MAX_DIST_CENTER_Y = config_set[setname]['MAX_DIST_CENTER_Y']
        MAX_PERS_SIZE_X = config_set[setname]['MAX_PERS_SIZE_X']
        MAX_PERS_SIZE_Y = config_set[setname]['MAX_PERS_SIZE_Y']
        MIN_PERS_SIZE_X = config_set[setname]['MIN_PERS_SIZE_X']
        MIN_PERS_SIZE_Y = config_set[setname]['MIN_PERS_SIZE_Y']


#FRAME LIMITS (KILLING ZONE)

DEAD_ZONE_Y = 15
DEAD_ZONE_X = 12

NO_SEE_FRAMES_BEFORE_DEATH = 250
NO_SEE_FRAMES_BEFORE_DEATH_BORDERS = 5

ALPHA = 0.5


    