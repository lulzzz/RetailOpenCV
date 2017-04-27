import cv2
import numpy as np
import config as cf
import random
from datetime import datetime
import time
from copy import copy

class Source(object):

    """Manages video sources"""



    def __init__(self, path, display_frame_number=True, display_frame_dim=True):
        self.path = path
        self.nb_frame = 0

        self.display_frame_number = display_frame_number
        self.display_frame_dim = display_frame_dim

        self.camera = cv2.VideoCapture(path)
        self.original_size = self.camera.get(3), self.camera.get(4) 

        print("Original size: {} x {}".format(self.camera.get(3), self.camera.get(4)))

        if (path == 0):
            self.camera.set(3, cf.SET_WEBCAM_WIDTH)
            self.camera.set(4, cf.SET_WEBCAM_HEIGHT)

        if (path == 1):
            self.camera.set(3, cf.SET_WEBCAM_WIDTH)
            self.camera.set(4, cf.SET_WEBCAM_HEIGHT)
            
        self.original_size = self.camera.get(3), self.camera.get(4)

        print("Ajusted size: {} x {}".format(self.camera.get(3), self.camera.get(4)))


        self.new_size = self.video_dim()

        print("Render size: {} x {}".format(self.new_size[0], self.new_size[1]))

        cf.CURRENT_FRAME_SIZE = self.new_size
        self.current_frame = np.zeros((int(self.video_dim()[0]), int(self.video_dim()[1])), dtype=np.uint8)
        self.first_frame = np.zeros((int(self.video_dim()[0]), int(self.video_dim()[1])), dtype=np.uint8)
        self.avg_frame = np.zeros((int(self.video_dim()[1]), int(self.video_dim()[0]), 3), dtype=np.uint8)


        self.nb_total_frame = 0
        if (path != 0) & (path != 1):
            self.nb_total_frame = self.camera.get(7)

    def next_frame(self):
        (ret, frame) = self.camera.read()

        if self.path == 0 & ret == False:
            for i in range (10):
                (ret, frame) = self.camera.read()
                if ret:
                    break
            
        
        if ret:
            self.nb_frame += 1

            if (self.original_size != self.new_size):
                frame = self.resize(frame)

            if self.path == 0:
                frame = cv2.flip(frame, 1)  

            self.current_frame = frame

            if self.nb_frame == 1:
                self.first_frame = copy(frame)

            if self.nb_frame < self.nb_total_frame:
                alpha = 0.02
                cv2.addWeighted(frame, alpha, self.avg_frame, 1-alpha, alpha, self.avg_frame)

            if self.nb_frame == 1:
                cv2.imwrite('out.png', frame)

            if self.nb_frame == self.nb_total_frame - 1:
                cv2.imwrite('avg.png', self.avg_frame)

            self.current_frame = frame

        return ret,frame

    '''
    def frame_with_annotation(self):
        lignes = []
        temp = copy(self.current_frame)
        
        if self.display_frame_dim:
            lignes.append(str(int(self.new_size[0]))+"x"+str(int(self.new_size[1])))

        if self.display_frame_number:
            lignes.append("Frame " + str(self.nb_frame))
        lignes.append("FPS "+str(round(self.nb_frame/(time.time()-cf.T_START),2)))
        for ligne in enumerate(lignes):
            cv2.putText(temp,ligne[1],(0,12*(ligne[0]+1)+3*ligne[0]), cf.FONT, 0.5,cf.ANOTATION_COLOR,2)
        
        return temp
    '''
        
    def video_dim(self):
        width, height = self.original_size

        if (width > height) & (width > cf.MAX_LONGER_SIDE):
            height = int(cf.MAX_LONGER_SIDE * height / width)
            width = cf.MAX_LONGER_SIDE

        if (height > width) & (height>cf.MAX_LONGER_SIDE):
            width = int(cf.MAX_LONGER_SIDE  * width / height)
            height = cf.MAX_LONGER_SIDE

        return int(width), int(height)
        

    def resize(self, frame):
        return cv2.resize(frame, self.video_dim(), interpolation=cv2.INTER_CUBIC)

    def release(self):
        self.camera.release()
