import config as cf
import cv2
import numpy as np
from datetime import datetime
from random import random, randint
import os
import sys
from copy import copy
from Source import Source
from ForgroundExtraction import ForgroundExtraction
from Person import Person
import json
import requests
#from numba import jit
import math


def xmax(cnt):
    return tuple(cnt[cnt[:,:,0].argmax()][0])[0] 

def xmin(cnt):
    return tuple(cnt[cnt[:,:,0].argmin()][0])[0] 

def ymax(cnt):
    return tuple(cnt[cnt[:,:,1].argmax()][0])[1] 

def ymin(cnt):
    return tuple(cnt[cnt[:,:,1].argmin()][0])[1] 

def xmax_point(cnt):
    return tuple(cnt[cnt[:,:,0].argmax()][0])

def xmin_point(cnt):
    return tuple(cnt[cnt[:,:,0].argmin()][0])

def ymax_point(cnt):
    return tuple(cnt[cnt[:,:,1].argmax()][0])

def ymin_point(cnt):
    return tuple(cnt[cnt[:,:,1].argmin()][0])

'''
def post_results(data):
    send_json = json.dumps(data)
    cf.OUTPUTFILE.write("\n"+send_json)
    print(send_json)
    headers = {'Content-type':'application/json'}
    try:
        res = requests.post(cf.API_POST_RESULTS, data=send_json, headers=headers)
        if res.status_code == 200:
            print("API {}".format(res.text))
            return True
    except Exception as e:
        msg = "Exception is:\n %s \n" % e
        print(msg)
'''
    
    

def compare_contour_aera(cnt1, cnt2):
    if cv2.contourArea(cnt1) < cv2.contourArea(cnt2):
        return 1
    elif cv2.contourArea(cnt1) > cv2.contourArea(cnt2):
        return -1
    else:
        return 0

def center_contour(cnt):
    M = cv2.moments(cnt)
    if M['m00']!=0:
        return int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    else:
       return 0,0

def bbox(liste_contours):
    x_min = min([xmin(c) for c in liste_contours])
    x_max = max([xmax(c) for c in liste_contours])
    y_min = min([ymin(c) for c in liste_contours])
    y_max = max([ymax(c) for c in liste_contours])

    xw = x_max - x_min
    yh = y_max - y_min

    return (x_min, y_min, xw, yh)

def bbox_overlap_x(bbox1, bbox2):
    return max(bbox1[0], bbox2[0])<min(bbox1[0]+bbox1[2], bbox2[0]+bbox2[2])

def bbox_overlap_y(bbox1, bbox2):
    return max(bbox1[1], bbox2[1])<min(bbox1[1]+bbox1[3], bbox2[1]+bbox2[3])

def bbox_overlap(bbox1, bbox2):
    return bbox_overlap_x(bbox1, bbox2) & bbox_overlap_y(bbox1, bbox2)

def distance(pt1, pt2):
    return int(math.sqrt(pow(pt1[0]-pt2[0], 2)+pow(pt1[1]-pt2[1], 2)))


def search_person_on_frame(contours):
       
    res_temp = []
    ref = copy(contours[0])
    temp = copy(contours)
    contours.pop(0)
    #contours.remove(contours[0])

    centre_ref = center_contour(ref)
    res_temp.append(ref)

    for i,c in enumerate(temp):
        if i != 0:
            #calcul distance between the biggest area and the others
            centre_c = center_contour(c)
                        
            #dist = distance(centre_ref, centre_c)
            dist_x = abs(centre_ref[0] - centre_c[0])
            dist_y = abs(centre_ref[1] - centre_c[1])

            #check whether the contour is far from the biggest detected
            if (dist_x < cf.dC.max_dist_center_x()) & (dist_y < cf.dC.max_dist_center_y()):

                #check whether adding this contour would create a too big overall area for it to be a person
                minx_temp = min(min([xmin(cnt) for cnt in res_temp]), xmin(c))
                maxx_temp = max(max([xmax(cnt) for cnt in res_temp]), xmax(c))
                width = maxx_temp - minx_temp

                miny_temp = min(min([ymin(cnt) for cnt in res_temp]), ymin(c))
                maxy_temp = max(max([ymax(cnt) for cnt in res_temp]), ymax(c))
                height = maxy_temp - miny_temp

                if (width > cf.dC.min_pers_size_x()) & (width < cf.dC.max_pers_size_x()):
                    if (height > cf.dC.min_pers_size_y()) & (height < cf.dC.max_pers_size_y()):
                        #if no consider the contour as part of the person
                        res_temp.append(copy(c))
                        for j,cnt in enumerate(contours):
                            if len(cnt) == len(c):
                                if (cnt == c).all():            
                                    contours.pop(j)
                                    break
    
    x_min = min([xmin(c) for c in res_temp])
    x_max = max([xmax(c) for c in res_temp])
    y_min = min([ymin(c) for c in res_temp])
    y_max = max([ymax(c) for c in res_temp])

    xw = x_max - x_min
    yh = y_max - y_min

    sum_area = 0
    for c in res_temp:
        sum_area += cv2.contourArea(c)

    if (xw > cf.dC.min_pers_size_x()) & (xw < cf.dC.max_pers_size_x()) & (yh < cf.dC.max_pers_size_y()) & (yh > cf.dC.min_pers_size_y()) & (sum_area > cf.dC.min_size_cnt_pers()):
        return True,res_temp
    else:
        return False,[]

#@jit
def update_persons(persons, nb_frame, persons_on_frame):
    

    if len(persons) == 0:
        for pf in persons_on_frame:
            persons.append(Person(nb_frame, pf))
        '''
        else:
                if len(persons_on_frame) > 0:
                    persons[0].update(nb_frame, persons_on_frame[0]) 
        '''

        
    else:
        working_temp_p_on_frame = copy(persons_on_frame)
        for p in persons:
            if p.alive:
                for i,pf in enumerate(working_temp_p_on_frame):
                    if bbox_overlap(bbox(pf), bbox(p.liste_contours[-1][1])):
                        p.update(nb_frame, pf)
                        working_temp_p_on_frame.pop(i)
        for pf in working_temp_p_on_frame:
            persons.append(Person(nb_frame, pf))


def kill(zones, persons, i, p, nb_frame, backup):
    p.alive = False;
    previous_zone_id = p.last_zone_id()	
    previous_zone = p.last_zone()
    #p.add_zone(0, nb_frame)
    cf.to_be_sent.append((str(p.uuid), 1, previous_zone_id, time()))
    if previous_zone_id != 1:
        zones.inc_out(previous_zone)
    
    if p.age < 50:
        backup.append(copy(p))
        persons.pop(i)
    

def check_for_deaths(zones, persons, new_size, nb_frame, backup):
    count_alive = 0
    count_dead = 0
    for i,p in enumerate(persons):
        if p.alive:
            count_alive += 1
            if nb_frame - p.last_frame_seen > cf.NO_SEE_FRAMES_BEFORE_DEATH:
                kill(zones, persons, i, p, nb_frame, backup)
                print("{} {} {} dies    {} age {}".format(nb_frame, time(), p.puuid, p.last_zone(), p.age))
            if p.close_from_borders(new_size) & (( nb_frame - p.last_frame_seen) > cf.NO_SEE_FRAMES_BEFORE_DEATH_BORDERS):
                kill(zones, persons, i, p, nb_frame, backup)
                print("{} {} {} dies    {} age {}".format(nb_frame, time(), p.puuid, p.last_zone(), p.age))
        
        elif not p.alive:
            count_dead += 1
            
    #print('{} persons: {} alive {} dead ({} dead backup)'.format(len(persons), count_alive, count_dead, len(backup)))

def search_for_diseppeared_persons(persons, VideoSource):
    res = []
    for p in persons:
        #print('test {} {} {}'.format(p.last_seen_frame(), VideoSource.nb_frame -1, p.age))
        if p.last_seen_frame() == (VideoSource.nb_frame - 1):
            if p.age > 100:

                x,y,w,h = bbox(p.liste_contours[-100][1])

                cnt = []
                points = []
                points.append([x,y])
                points.append([x+w,y])
                points.append([x+w,y+h])
                points.append([x,y+h])

                for point in points:
                    cnt.append([point])

                res.append(([np.array(cnt)], p.puuid))        
    return res

def update_persons_zones(persons, nb_frame, zones):
    for p in persons:
        if p.alive:
            if p.exists_at_last_frame(nb_frame):
                
                previous_zone = p.last_zone()
                previous_zone_id = p.last_zone_id()

                new_zone, new_zone_id = zones.in_zones(p.position_last_frame(nb_frame))

                if previous_zone == 0:
                    p.add_zone(new_zone, nb_frame, new_zone_id)
                    time_appear = time()
                    cf.to_be_sent.append((str(p.uuid), 0, new_zone_id, time_appear))
                    cf.to_be_sent.append((str(p.uuid), 2, new_zone_id, time_appear))
                    print('{} {} {} appears {}'.format(nb_frame, time(), p.puuid, new_zone))
                    if (new_zone != 1):
                        zones.inc_in(new_zone)

                else:
                    if previous_zone == new_zone:
                        p.add_zone(new_zone, nb_frame, new_zone_id)

                    else:
                        if (previous_zone == 1):
                            print('{} {} {} enters  {}'.format(nb_frame, time(), p.puuid, new_zone))
                            cf.to_be_sent.append((str(p.uuid), 2, new_zone_id, time()))
                            zones.inc_in(new_zone)

                        elif (new_zone == 1):
                            print('{} {} {} leaves  {}'.format(nb_frame, time(), p.puuid, previous_zone))
                            cf.to_be_sent.append((str(p.uuid), 3, previous_zone_id, time()))
                            zones.inc_out(previous_zone)

                        else:
                            print('{} {} {} leaves  {}'.format(nb_frame, time(), p.puuid, previous_zone))
                            print('{} {} {} enters  {}'.format(nb_frame, time(), p.puuid, new_zone))
                            #print('{} {} {} leaves  {} and enters {}'.format(nb_frame, time(), str(p.uuid), previous_zone, new_zone))
                            #cf.to_be_sent.append((str(p.uuid), "leaves", previous_zone, time()))
                            cf.to_be_sent.append((str(p.uuid), 3, previous_zone_id, time()))
                            cf.to_be_sent.append((str(p.uuid), 2, new_zone_id, time()))
                            zones.inc_out(previous_zone)
                            zones.inc_in(new_zone)


                        p.add_zone(new_zone, nb_frame, new_zone_id)
                        
            
                



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


def hsv_to_bgr(h,s,v):
    c = v * s
    x = c * (1 - abs( ((float(h)/float(60))%float(2)) - 1))
    m = v - c
    
    if 0 <= h & h < 60:
        r = c
        g = x
        b = 0    
    if 60 <= h & h < 120:
        r = x
        g = c
        b = 0   
    if 120 <= h & h < 180:
        r = 0
        g = c
        b = x   
    if 180 <= h & h < 240:
        r = 0
        g = x
        b = c   
    if 240 <= h & h < 300:
        r = x
        g = 0
        b = c   
    if 300 <= h & h < 360:
        r = c
        g = 0
        b = x

    return int((b+m)*255), int((g+m)*255), int((r+m)*255)   

def random_color():
    #return np.uint8([[0,0,255]])
    #return cv2.cvtColor(np.ndarray.tolist(cv2.convertScaleAbs(np.random.rand(1,3)*255))[0], cv2.COLOR_HSV2BGR)      
    h = randint(0,359)
    return (hsv_to_bgr(h, 1, 1) , hsv_to_bgr(h, 1, 0.5))

def random_color_zones():
    #return np.uint8([[0,0,255]])
    #return cv2.cvtColor(np.ndarray.tolist(cv2.convertScaleAbs(np.random.rand(1,3)*255))[0], cv2.COLOR_HSV2BGR)      
    rand = randint(64, 192)
    return (rand, rand, rand)

def time():
    return str(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"));


def heat_log(min, max, val):
    if max != min:
        x = ((5.0*float(val))/(float(max)-float(min))) - float(min)
        return 1 - (1 / (math.exp(x)))
    return 0

def heat_linear(min, max, val):
    if max != min:
        return ((float(val))/(float(max)-float(min))) - float(min)
    return 0

def heatMap(persons, VideoSource):

    frame = copy(VideoSource.avg_frame)

    '''
    for x in range(int(VideoSource.new_size[0])/20):
        cv2.line(frame, (x*20, 0), (x*20, int(VideoSource.new_size[1])), (255,255,255), 1, cv2.CV_AA)

    for y in range(int(VideoSource.new_size[1])/20):
        cv2.line(frame, (0, y*20), (int(VideoSource.new_size[0]), y*20), (255,255,255), 1, cv2.CV_AA)
    '''

    nb_pos_per_spot = np.zeros((int(VideoSource.new_size[1])/cf.HEAT_MAP_CELL_SIZE, int(VideoSource.new_size[0])/cf.HEAT_MAP_CELL_SIZE), np.uint8)
    
    for p in persons:
        for pos, nb_frame in p.liste_positions:
            nb_pos_per_spot[pos[1]/cf.HEAT_MAP_CELL_SIZE, pos[0]/cf.HEAT_MAP_CELL_SIZE] += 1
    
    max = np.amax(nb_pos_per_spot)
    min = np.amin(nb_pos_per_spot)
    
    image = np.ones((cf.HEAT_MAP_CELL_SIZE, cf.HEAT_MAP_CELL_SIZE, 3), np.uint8)
    image[:,:] = (0,0,255)

    #frame[20:40, 20:40] = image

    #cv2.addWeighted(image, 0.5, frame[20:40, 20:40], 0.5, 0, frame[20:40, 20:40])
    '''
    print("HEAT MAP")
    print(nb_pos_per_spot.shape)
    print(frame.shape)

    print(max)
    print(min)
    '''
    for y in range(nb_pos_per_spot.shape[0]):
        for x in range(nb_pos_per_spot.shape[1]):

            alpha = heat_linear(min, max, nb_pos_per_spot[y,x])/2 + heat_log(min, max, nb_pos_per_spot[y,x])/2
            #alpha = 0.5
            #temp = frame[x*20:x*20+20, y*20:y*20+20]
            #print("{} {} {} {}".format(y,x, nb_pos_per_spot[y,x],alpha))
            cv2.addWeighted(image, alpha, frame[y*cf.HEAT_MAP_CELL_SIZE:y*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE, x*cf.HEAT_MAP_CELL_SIZE:x*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE], 1 - alpha, 0, frame[y*cf.HEAT_MAP_CELL_SIZE:y*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE, x*cf.HEAT_MAP_CELL_SIZE:x*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE])
            #cv2.putText(frame, "{}".format(nb_pos_per_spot[y,x]), (x*20, y*20+20), cf.FONT, 0.5 , (255,255,255), 1, cv2.CV_AA)
            #frame[x*20:x*20+20, y*20:y*20+20]

    return frame

    

    


