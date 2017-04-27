import cv2
import numpy as np
from datetime import datetime
from random import randint
import os
import time
from detection_config_settings import DetectionConfig


'''
'
'  VIDEO AQUISITION
'
'''

#VIDEO_SOURCE = "http://96.10.1.168/mjpg/1/video.mjpg"

#VIDEO_SOURCE = 1

#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute10\\cam2.avi"




#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute22\\cam2.avi"

#VIDEO_SOURCE = "..\\dataset\\lego960\\05\\lego.mp4"

#VIDEO_SOURCE = "..\\dataset\\chutes\\chute14\\cam2.avi"



#VIDEO_SOURCE = "C:\\Users\\Olivier Staub\\Documents\\ComputerVision_Detect_Body\\videoset\\chute16\\cam2.avi"

#VIDEO_SOURCE = 1

#VIDEO_SOURCE = "rtsp://admin:Azemlk123@192.168.1.31/play2.sdp"


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



VIDEO_SOURCE = "..\\dataset\\street\\08\\street960.mp4"
#VIDEO_SOURCE = "..\\dataset\\chutesLab\\03\\10.avi"


MAX_LONGER_SIDE = 960

SET_WEBCAM_WIDTH = 960
SET_WEBCAM_HEIGHT = 540

ACTIVE_CONFIG_SET = "street"
dC = DetectionConfig(ACTIVE_CONFIG_SET)



#foreground extraction
ALGO = 2
LR = 0.002
TRAIN_FRAMES = 80



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

DIR_ZONES = "..\dataset\zones"
#DIR_ZONES = "../dataset/zones"

'''
'
'  API CONFIG
'

'''

USE_SENDING_THREAD = False
SEND_DATA = False
API_GET_CAM_ID = ""
API_POST_RESULTS = "http://hub-cargo.azurewebsites.net/api/hublog/notify"
API_DEBUG = True
API_SLEEP_TIME = 5 #in seconds, can be a float




'''
'
'  PROCESSING CONFIG
'
'''

#tracking
TRACKING_VERBOSE = False


#zones detection
ZONES_DETECTION = True
ZONES_DETECTION_VERBOSE = True

#grouping
USE_GROUPS = False
REFRESH_POSITION_IN_GROUP = 6

#haar detector
HAAR_DETECTOR_MARGIN = 20
haar_detector = []
haar_detector.append(("cascade\\5024\\cascade_15_5024.xml", 1.5, 6, "car"))


'''
'
'  DRAWING CONFIG
'
'''

DISPLAYED_FRAME = 1

DRAW_CONFIG = False

DRAW_ZONES_DETECTION = False
DRAW_ZONES_IO = False
DRAW_ZONES_PORTAL = False

DRAW_PERSONS = True
DRAW_PERSONS_WAITING = True
DRAW_GROUPS = True
DRAW_PERSON_PATH_TAIL = True
DRAW_PERSON_PATH_TAIL_LENGTH = 500

DRAW_HEAT_MAP = False
HEAT_MAP_CELL_SIZE = 10


SHOW_FG = False

PLAYBACK_LENGTH = 750


LOGO_FILE = "logo.png"
INIT_FILE = "init.png"



'''
'
'  OUTPUT FILES
'
'''

#sent json payloads logs
OUTPUTFILE = open("out.json", "w")

#rendered vide file
RENDER_VIDEO = False
def OUTPUT_VIDEO(sourceName):
    return "out_{}.avi".format(sourceName)

PERF_STATS = False

EXPORT_HEATMAPJS_DATA = True


#donnee generales partagees

T_START = time.time()

FONT = cv2.FONT_HERSHEY_SIMPLEX

ANOTATION_COLOR = (0,255,0)
BORDER_BACKGROUND_COLOR = (0,0,0)
BORDER_TEXT_COLOR = (0,0,0)

to_be_sent = []


def get_camera_id():
    '''
    res = requests.get(cf.API_GET_CAM_ID)
    if res.status_code == 200:
        return res.json()['id']
    '''
    return 'test'

CAMERA_ID = get_camera_id()


#Filled at init source in order to determine limits and min/max sizes
CURRENT_FRAME_SIZE = 0


# Operateurs morphologiques

FG_O_OP = 2    #10 #opening
FG_C_OP = 4    #15 #closing

#chutelab
FG_O_OP = 1    #10 #opening
FG_C_OP = 5    #15 #closing


STR_ELEMENT = cv2.MORPH_ELLIPSE

o_kernel = cv2.getStructuringElement(STR_ELEMENT,(FG_O_OP,FG_O_OP))
c_kernel = cv2.getStructuringElement(STR_ELEMENT,(FG_C_OP,FG_C_OP))  


#Minimum contour size for detection



DEAD_ZONE_Y = 15
DEAD_ZONE_X = 12

NO_SEE_FRAMES_BEFORE_DEATH = 150
NO_SEE_FRAMES_BEFORE_DEATH_BORDERS = 5

ALPHA = 0.5


'''
'
'  HISTOGRAMS
'
'''

ql = 32
channels = [0,1,2]
ranges = [0, 256, 0, 256, 0, 256]
histsize = [ql for i in range(0,3)]
hist_lr = 0.6 

REFRESH_HIST = 6


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

''' Street Config '''
'''
CNT_MIN = 5
MIN_SIZE_CNT_PERS = 10

MAX_DIST_CENTER_X = 60
MAX_DIST_CENTER_Y = 30

MAX_PERS_SIZE_X = 220
MAX_PERS_SIZE_Y = 150

MIN_PERS_SIZE_X = 5
MIN_PERS_SIZE_Y = 10
'''


''' Lego Config '''
'''
CNT_MIN = 10
MIN_SIZE_CNT_PERS = 10

MAX_DIST_CENTER_X = 80
MAX_DIST_CENTER_Y = 80

MAX_PERS_SIZE_X = 180
MAX_PERS_SIZE_Y = 180

MIN_PERS_SIZE_X = 25
MIN_PERS_SIZE_Y = 25
'''


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





'''
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
'''

#FRAME LIMITS (KILLING ZONE)




    