import numpy as np
import cv2
import config as cf
import arg_parser as parse
import tools as tl
#import cython_tools as ctl
from datetime import datetime
import time
import logging
from Source import Source
from ForgroundExtraction import ForgroundExtraction
from Person import Person
from Zones import Zones
import math
from copy import copy
import json
import requests
import threading
import time
import os
from multiprocessing import Process, TimeoutError
from detection_config_settings import DetectionConfig
import random





def main():

    VIDEO_SOURCE = "..\\dataset\\street\\08\\street960.mp4"

    
    args = parse.parser()


    if args.input:
        if args.input == "0":
            input_video = 0
        elif args.input == "1":
            input_video = 1
        else:
            input_video = args.input
    else:
        input_video = VIDEO_SOURCE
    
    video = Source(VIDEO_SOURCE)

    #car_cascade = cv2.CascadeClassifier("car_cascade_10.xml")
    #car_cascade = cv2.CascadeClassifier("cascade\data3014\cascade.xml")
    car_cascade = cv2.CascadeClassifier("cascade\\5024\\cascade_15_5024.xml")
    #car_cascade = cv2.CascadeClassifier("cascade\\data5024900020000\\cascade_14_5024_10k20k_haar.xml")
    
    #car_cascade = cv2.CascadeClassifier("cascade\\large_LBP\\large8.xml")
    #ciseaux_cascade = cv2.CascadeClassifier("cascade\\ciseaux\\data\\cascade_ciseaux_25_4040_LBP.xml")

    while(True):

        ret, frame = video.next_frame()

        #break at the end of the video 
        if not ret:
            print('End of video')
            break

        #break on key press
        key = cv2.waitKey(1)

        if key == 27:
            print("Exiting...")
            break   


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cars = car_cascade.detectMultiScale(gray, 1.5, 6)

        #cars = car_cascade.detectMultiScale(gray, 10, 10)
            
        #30 14            
        #cars = car_cascade.detectMultiScale(gray, 4, 4)
            
        #cars = car_cascade.detectMultiScale(gray, 2,2)

        #cars = car_cascade.detectMultiScale(gray, 10, 12)

        #cars = car_cascade.detectMultiScale(gray, 4, 8)


        for x,y,w,h in cars:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)


        cv2.imshow("ML", frame)
        print "\r{}".format(video.nb_frame),


    video.release()
    cv2.destroyAllWindows()
    print "bye."



if __name__ == "__main__":
    main()
