import numpy as np
import cv2
import config as cf
import tools as tl
import random
import uuid
import time



class Person(object):
    """description of class"""



    def __init__(self, nb_frame, liste_contours):
        self.time = time.time()
        self.liste_contours = [(nb_frame, liste_contours, self.time)]
       
        self.age = 1
        self.last_frame_seen = nb_frame

        M = cv2.moments(liste_contours[0])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        self.centroid = cx,cy

        self.couleur, self.couleur_dark = tl.random_color()

        self.liste_positions = [(self.position_last_frame(nb_frame), nb_frame)]

        self.uuid = str(uuid.uuid4())
        self.puuid = self.uuid[0:6]

        self.liste_zones = []

        self.alive = True


        #self.zone = zones.in_zones(self.position_last_frame(nb_frame))

        #cf.to_be_sent.append((str(self.uuid), self.zone, self.zone, tl.time()))
        #print('{} {} appears in zone: {}'.format(tl.time(), str(self.uuid), self.zone))



    def update(self, nb_frame, liste_contours):
        t = time.time()
        self.liste_contours.append((nb_frame, liste_contours, t))

        self.age += 1
        self.last_frame_seen = nb_frame

        M = cv2.moments(liste_contours[0])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        self.centroid = cx,cy
    
        last_frame_position = self.position_last_frame(nb_frame)

        self.liste_positions.append((last_frame_position, nb_frame))

        #new_zone = zones.in_zones(self.position_last_frame(nb_frame))

        #cf.to_be_sent.append((str(self.uuid), last_frame_position[0], last_frame_position[1], tl.time()))
        '''
        if (self.zone != new_zone):
            if (self.zone == -1):
                print("{} {} enters zone: {}".format(tl.time(), str(self.uuid), new_zone))
            elif(new_zone == -1):
                print("{} {} exits zone: {}".format(tl.time(), str(self.uuid), self.zone))

            cf.to_be_sent.append((str(self.uuid), self.zone, new_zone, tl.time()))
        

        self.zone = new_zone
        '''

        #self.liste_zones.append((0, nb_frame))

    def position_last_frame(self, nb_frame):
        (bbx,bby,bbw,bbh) = self.bbox_last_frame(nb_frame)
        center_bbox = int(bbx+(bbw/2)), int(bby+(bbh/2))
        
        if self.liste_contours[-1][0] == nb_frame:
                    
            M = cv2.moments(self.liste_contours[-1][1][0])
            if M['m00']!=0:
                center_larger_aera = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            else:
                center_larger_aera = 0,0

        res_x = min(center_larger_aera[0], center_bbox[0])+int(abs(center_larger_aera[0]-center_bbox[0])/2)
        previsous_y = min(center_larger_aera[1], center_bbox[1])+int(abs(center_larger_aera[1]-center_bbox[1])/2)
        temp_res_y = [center_larger_aera[1], center_bbox[1], bby+bbh, tl.ymax(self.liste_contours[-1][1][0])]
        res_y = int(sum(temp_res_y)/len(temp_res_y))

        return res_x , res_y
   

    def bbox_last_frame(self, nb_frame):
        if self.liste_contours[-1][0] == nb_frame:
            x_min = min([tl.xmin(c) for c in self.liste_contours[-1][1]])
            x_max = max([tl.xmax(c) for c in self.liste_contours[-1][1]])
            y_min = min([tl.ymin(c) for c in self.liste_contours[-1][1]])
            y_max = max([tl.ymax(c) for c in self.liste_contours[-1][1]])

            w = x_max - x_min
            h = y_max - y_min

            return (x_min, y_min, w, h)
    

    def contour_last_frame(self, nb_frame):
        if self.liste_contours[-1][0] == nb_frame:
            return self.liste_contours[-1][1]
        

    def exists_at_last_frame(self, nb_frame):
        if (self.liste_contours[-1][0] == nb_frame):
            return True
        else:
            return False


    def last_zone(self):
        if len(self.liste_zones)==0:
            return 0
        else:
            return self.liste_zones[-1][0] 


    def add_zone(self, zone, nb_frame):
        self.liste_zones.append((zone, nb_frame))
        
    def close_from_borders(self,  video_dim):
        x, y  = self.liste_positions[-1][0]
        w, h = int(video_dim[0]), int(video_dim[1])
        if (x < cf.DEAD_ZONE_X) | (x > (w - cf.DEAD_ZONE_X)):
            return True            
        if (y < cf.DEAD_ZONE_Y) | (y > (h - cf.DEAD_ZONE_Y)):
            return True
        return False

    '''
    def position(self, nb_frame):
        (bbx,bby,bbw,bbh) = self.bbox_last_frame(nb_frame)
        center_bbox = int(bbx+(bbw/2)), int(bby+(bbh/2))
        
        for l in self.liste_contours:
            if l[0] == nb_frame:
                M = cv2.moments(l[1][0])
                if M['m00']!=0:
                    center_larger_aera = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                else:
                    center_larger_aera = 0,0

        return min(center_larger_aera[0], center_bbox[0])+int(abs(center_larger_aera[0]-center_bbox[0])/2) , min(center_larger_aera[1], center_bbox[1])+int(abs(center_larger_aera[1]-center_bbox[1])/2)         
    '''

    '''
    def exists_at_frame(self, nb_frame):
        for n,l in self.liste_contours:
            if n == nb_frame:
                return True
        return False
    '''

    '''
    def mask(self, im_size):
        mask = np.zeros(im_size, dtype=np.uint8)
        if len(contours)>0:
            mask = cv2.drawContours(mask, contours, 0, 1, -1)
        return mask
    '''

    '''
    def contour(self, nb_frame):
        for nb,c in self.liste_contours:
            if nb==nb_frame:
                return c
    '''
    
        
    '''
    def bbox(self, nb_frame):
        for l in self.liste_contours:
            if l[0] == nb_frame:
                x_min = min([cf.xmin(c) for c in l[1]])
                x_max = max([cf.xmax(c) for c in l[1]])
                y_min = min([cf.ymin(c) for c in l[1]])
                y_max = max([cf.ymax(c) for c in l[1]])

                w = x_max - x_min
                h = y_max - y_min

                return (x_min, y_min, w, h)
    '''