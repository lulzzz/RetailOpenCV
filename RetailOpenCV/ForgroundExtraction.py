import numpy as np
import cv2
import config as cf
from copy import copy
import logging
from datetime import datetime

class ForgroundExtraction(object):
    """Forground extraction"""


    def __init__(self, algo, frame_dim):
        self.nb_frame = 0
        self._algo = algo

        self.fgmask_m1 = np.zeros((int(frame_dim[0]),int(frame_dim[1])), dtype=np.uint8)
        self.fgmask = np.zeros((int(frame_dim[0]),int(frame_dim[1])), dtype=np.uint8)

        self.frame_dim = frame_dim

        if (self._algo == 0):
            self.fgbg_m1 = cv2.BackgroundSubtractorMOG()  
            self.fgbg = cv2.BackgroundSubtractorMOG2(0, 20, False)   
        elif (self._algo == 1):
            self.fgbg = cv2.BackgroundSubtractorMOG()  
        elif (self._algo == 2):
            self.fgbg = cv2.BackgroundSubtractorMOG2(0, 20, False)   
            

    def update(self, frame, nb_frame):
        #MOG
        if (self._algo == 0):
            if self.nb_frame < cf.TRAIN_FRAMES:
                self.fgmask_m1 = self.fgbg_m1.apply(frame, learningRate = cf.LR)  
                self.fgmask = self.fgbg.apply(frame, learningRate = cf.LR)   
                self.fgmask_m1 = cv2.morphologyEx(self.fgmask_m1, cv2.MORPH_OPEN, cf.o_kernel)
                self.fgmask_m1 = cv2.morphologyEx(self.fgmask_m1, cv2.MORPH_CLOSE, cf.c_kernel,iterations=1)
                self.nb_frame += 1  
                return self.fgmask_m1
            else:
                self.fgmask = self.fgbg.apply(frame, learningRate = cf.LR)   
                self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_OPEN, cf.o_kernel)
                self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_CLOSE, cf.c_kernel,iterations=1)
                self.nb_frame += 1  
                return self.fgmask
        elif (self._algo == 1)|(self._algo == 2):
            self.fgmask = self.fgbg.apply(frame, learningRate = cf.LR)   
            self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_OPEN, cf.o_kernel, iterations=2)
            self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_CLOSE, cf.c_kernel,iterations=1)
            #self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_OPEN, cf.o_kernel, iterations=1)
            return self.fgmask 
        elif(self._algo == 3):
            mask32 = np.zeros(self.frame_dim, dtype=np.float32)
            cv2.accumulateWeighted(frame, mask32, 0.05)
            avg_show = cv2.CreateImage(cv.GetSize(frame),8,3) 
            cv2.ConvertScaleAbs(mask32,self.fgmask)
            return self.fgmask