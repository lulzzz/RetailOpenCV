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

VIDEO_SOURCE = 0

#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute10\\cam2.avi"

VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\street\\01\\street960.mp4"

#VIDEO_SOURCE = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute22\\cam2.avi"



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

FG_O_OP=2    #10 #opening
FG_C_OP=8    #15 #closing

STR_ELEMENT=cv2.MORPH_ELLIPSE

o_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_O_OP,FG_O_OP))
c_kernel=cv2.getStructuringElement(STR_ELEMENT,(FG_C_OP,FG_C_OP))  


#Minimum contour size for detection
'''
MAX_DIST_CENTRE = 180
MAX_PERS_SIZE = 300
MIN_PERS_SIZE = 50
'''


''' Chutes Config '''
'''
CNT_MIN = 30
MIN_SIZE_CNT_PERS = 30

MAX_DIST_CENTER_X = 160
MAX_DIST_CENTER_Y = 180

MAX_PERS_SIZE_X = 260
MAX_PERS_SIZE_Y = 300

MIN_PERS_SIZE_X = 40
MIN_PERS_SIZE_Y = 60
'''

''' Lego Config '''


CNT_MIN = 5
MIN_SIZE_CNT_PERS = 10

MAX_DIST_CENTER_X = 60
MAX_DIST_CENTER_Y = 30

MAX_PERS_SIZE_X = 220
MAX_PERS_SIZE_Y = 150

MIN_PERS_SIZE_X = 5
MIN_PERS_SIZE_Y = 10



#FRAME LIMITS (KILLING ZONE)

DEAD_ZONE_Y = 15
DEAD_ZONE_X = 12

NO_SEE_FRAMES_BEFORE_DEATH = 100

ALPHA = 0.5


    