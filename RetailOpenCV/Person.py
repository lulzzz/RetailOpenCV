import numpy as np
import cv2
import config as cf
import tools as tl
import random
import uuid
import time



class Person(object):
    """description of class"""



    def __init__(self, nb_frame, vs, liste_contours):
        self.time = time.time()
        #self.liste_contours = [(nb_frame, liste_contours, self.time)]
       
        self.age = 1
        self.last_frame_seen = nb_frame
        self.in_group = "0"
        self.group = None
        #self.last_position = self.calculate_position(liste_contours)

        self.couleur, self.couleur_dark = tl.random_color()
        #self.liste_positions = [(self.position_last_frame(nb_frame), nb_frame)]
        self.uuid = str(uuid.uuid4())
        self.puuid = self.uuid[0:6]

        self.alive = True

        self.data = [[nb_frame, liste_contours, (0,0), self.time]]
        self.liste_zones = []
        #born position saves whther the item was born on the side of the frame or in the middle of it
        #0 for border zones
        #1 for the rest of the frame
        self.born_position = 0
        self.mask = self.current_mask(vs.new_size)
        self.hist = cv2.calcHist(cv2.split(vs.current_frame), cf.channels, self.mask, cf.histsize, cf.ranges)/cv2.countNonZero(self.mask)
        self.log = []
        self.last_position = 0,0
        self.item_haar_detected = []


    def update(self, nb_frame, liste_contours, vs, persons):
        t = time.time()
        #self.liste_contours.append((nb_frame, liste_contours, t))
        self.age += 1
        self.last_frame_seen = nb_frame
        self.mask = self.current_mask(vs.new_size)
        if ((nb_frame%cf.REFRESH_HIST) == 0) & (self.in_group == "0"):
            self.hist = (1 - cf.hist_lr) * self.hist + cf.hist_lr * cv2.calcHist(cv2.split(vs.current_frame), cf.channels, self.mask, cf.histsize, cf.ranges)/cv2.countNonZero(self.mask)
        self.data.append([nb_frame, liste_contours, (0,0), t])


    def update_position(self, groups, VideoSource):
        self.last_frame_position = self.calculate_position(self.data[-1][1], groups=groups, vs=VideoSource)
        self.last_position = self.last_frame_position
        self.data[-1][2] = self.last_frame_position
        #self.liste_positions.append((self.last_frame_position, VideoSource.nb_frame))


    def calculate_position(self, liste_contours, groups=None, vs=None):

        if self.in_group == "0":
            return tl.calculate_position(liste_contours)
        
        else:         
            if vs.nb_frame%cf.REFRESH_POSITION_IN_GROUP == 0:
                #prob = tl.histBackproj(group, self)
                #A0 = cv2.countNonZero(self.mask)
                #zero = time.time()*1000
                A0 = sum([cv2.contourArea(c) for c in self.data[-1][1]])
                #un = time.time()*1000
                P0 = float(A0) / self.group.tot_none_zeros
                #deux = time.time()*1000
                Px0 = self.hist / A0
                #trois = time.time()*1000
                P0x = Px0*P0 / self.group.tot_post_prob
                #quatre = time.time()*1000
                prob = np.uint8(P0x*255)
                #cinq = time.time()*1000

                #b,g,r = cv2.split(vs.current_frame/(256/cf.ql))
                div = np.divide(vs.current_frame, (256/cf.ql))
                b,g,r = div[:,:,0], div[:,:,1], div[:,:,2]
                #b,g,r = cv2.split()
                #six=time.time()*1000
                #B = np.uint8(prob[b.ravel(),g.ravel(), r.ravel()])  
                #B = prob[b.ravel(),g.ravel(), r.ravel()]  
                B = prob[b.reshape(-1),g.reshape(-1), r.reshape(-1)]  
                #sept = time.time()*1000
                dst = B.reshape(vs.current_frame.shape[:2])
                #huit = time.time()*1000
                dst = cv2.bitwise_and(dst, dst, mask = self.mask)
                #neuf = time.time()*1000
                #cv2.imshow("{}".format(self.puuid), cv2.resize(dst, (int(dst.shape[1]/2), int(dst.shape[0]/2))))
                M = cv2.moments(dst)
                #dix = time.time()*1000

    
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    #print "{}: {} {}".format(self.puuid, cx, cy)
                    res = (cx,cy)
                else:
                    res = self.last_position

                #onze = time.time()*1000
                #print "0:{} 1:{} 2:{} 3:{} 4:{} 5:{} 6:{} 7:{} 8:{} 9:{} 10:{}".format(un-zero, deux-un, trois-deux, quatre-trois, cinq-quatre, six-cinq, sept-six, huit-sept, neuf-huit, dix-neuf, onze-dix)
            else:
                res = self.last_position


            return res
           


    def position_last_frame(self):
        return self.last_position

    def bbox_last_frame(self, nb_frame):
        #if self.liste_contours[-1][0] == nb_frame:
        if self.data[-1][0] == nb_frame:
            x_min = min([tl.xmin(c) for c in self.data[-1][1]])
            x_max = max([tl.xmax(c) for c in self.data[-1][1]])
            y_min = min([tl.ymin(c) for c in self.data[-1][1]])
            y_max = max([tl.ymax(c) for c in self.data[-1][1]])

            w = x_max - x_min
            h = y_max - y_min

            return (x_min, y_min, w, h)
    

    def contour_last_frame(self, nb_frame):
        if self.data[-1][0] == nb_frame:
            return self.data[-1][1]
        '''
        if self.liste_contours[-1][0] == nb_frame:
            return self.liste_contours[-1][1]
        '''

    def last_contour(self):
        return self.data[-1][1]

    def set_last_contour(self, contour):
        self.data[-1][1] = contour
        

    def last_bbox(self):
    
        process = [(tl.xmin(c), tl.xmax(c), tl.ymin(c), tl.ymax(c)) for c in self.data[-1][1]]
        x_min, x_max, y_min, y_max = min(process, key=lambda c1:c1[0])[0], max(process, key=lambda c1:c1[1])[1], min(process, key=lambda c1:c1[2])[2], max(process, key=lambda c1:c1[3])[3]

        '''
        x_min = min([tl.xmin(c) for c in self.data[-1][1]])
        x_max = max([tl.xmax(c) for c in self.data[-1][1]])
        y_min = min([tl.ymin(c) for c in self.data[-1][1]])
        y_max = max([tl.ymax(c) for c in self.data[-1][1]])
        '''

        w = x_max - x_min
        h = y_max - y_min

        return (x_min, y_min, w, h)
    

    def exists_at_last_frame(self, nb_frame):
        if (self.data[-1][0] == nb_frame):
            return True
        else:
            return False

    def last_seen_frame(self):
        return self.last_frame_seen
    
    
    def last_zone(self):
        if len(self.liste_zones)==0:
            return 0
        else:
            return self.liste_zones[-1][0] 

    def last_zone_id(self):
        if len(self.liste_zones) == 0:
            return 0
        else:
            return self.liste_zones[-1][2] 
    

    def add_zone(self, zone, nb_frame, zone_id):
        self.liste_zones.append((zone, nb_frame, zone_id))
        
    def current_mask(self, video_size):
        mask = np.zeros((int(video_size[1]), int(video_size[0]), 1), dtype=np.uint8)
        cv2.drawContours(mask, self.data[-1][1], -1, (255,255,255), -1)
        return mask
        

    def add_event(self, nb_frame, event, zone):
        self.log.append((nb_frame, event, zone))

    def add_haar_detection(self, nb_frame, kind):
        #print "{} is a {} !".format(self.puuid, kind)
        self.item_haar_detected.append((nb_frame, kind))

    def nb_haar_detection(self, kind):
        #return len(self.item_haar_detected)
        #print "{} {}".format(self.puuid, len([nb_frame for nb_frame, k in self.item_haar_detected if k == kind]))
        return len([nb_frame for nb_frame, k in self.item_haar_detected if k == kind])



    '''
    def close_from_borders(self,  video_dim):
        x, y  = self.data[-1][2]
        w, h = int(video_dim[0]), int(video_dim[1])
        if (x < cf.DEAD_ZONE_X) | (x > (w - cf.DEAD_ZONE_X)):
            return True            
        if (y < cf.DEAD_ZONE_Y) | (y > (h - cf.DEAD_ZONE_Y)):
            return True
        return False
    '''


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