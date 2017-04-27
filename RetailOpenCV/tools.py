import config as cf
import cv2
import numpy as np
from datetime import datetime
import random
import os
import sys
from copy import copy
from Source import Source
from ForgroundExtraction import ForgroundExtraction
from Person import Person
from Group import Group
import json
import requests
import math
import json
import uuid
import time as ti


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

def compare_contour(cnt1, cnt2):
    if len(cnt1) == len(cnt2):
        return (cnt1 == cnt2).all()
    else:
        return False

def compare_contours_lists(liste1, liste2):
    try:
        if len(liste1) == len(liste2):
            test = []
            #for i in range(len(liste1)):
                #test.append(compare_contour(liste1[i], liste2[i]))
            for l1, l2 in zip(liste1, liste2):
                test.append(compare_contour(l1, l2))
            return all(test)
        else:
            return False   
    except:
        return False


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


def bbox_overlap_aera(bbox1, bbox2):
    w = min(bbox1[0]+bbox1[2], bbox2[0]+bbox2[2]) - max(bbox1[0], bbox2[0])
    h = min(bbox1[1]+bbox1[3], bbox2[1]+bbox2[3]) - max(bbox1[1], bbox2[1])
    return w*h


def contours_intersect(liste1, mask, vs):
    mask1 = np.zeros((vs.new_size[1], vs.new_size[0]), np.uint8)
    cv2.drawContours(mask1, liste1, -1, (255,255,255), -1)
    intersect = cv2.bitwise_and(mask1, mask)
    if cv2.countNonZero(intersect):
        return True
    else:
        return False

    '''
    for c1 in liste1:
        temp = np.vstack(c1).squeeze()
        for x,y in temp:
            for c2 in liste2:
                if cv2.pointPolygonTest(c2 ,(x,y), False) > 0:
                    return True            

    for c2 in liste2:
        temp = np.vstack(c2).squeeze()
        for x,y in temp:
            for c1 in liste1:
                if cv2.pointPolygonTest(c1, (x,y), False) > 0:
                    return True

    return False
    '''

def max_area(liste):
    max = 0,0
    for i,item in enumerate(liste):
        if item[0] > max[0]:
            max = item[0],item[1]

    return max


def distance(pt1, pt2):
    return int(math.sqrt(pow(pt1[0]-pt2[0], 2)+pow(pt1[1]-pt2[1], 2)))


def calculate_position(list_contours):
    bbx_min = min([xmin(c) for c in list_contours])
    bbx_max = max([xmax(c) for c in list_contours])
    bby_min = min([ymin(c) for c in list_contours])
    bby_max = max([ymax(c) for c in list_contours])

    bbw = bbx_max - bbx_min
    bbh = bby_max - bby_min

    center_bbox = int(bbx_min+(bbw/2)), int(bby_min+(bbh/2))

    M = cv2.moments(list_contours[0])
    if M['m00']!=0:
        center_larger_area = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    else:
        center_larger_area = 0,0

    temp_res_x = [center_larger_area[0], center_bbox[0]]
    res_x = int(sum(temp_res_x)/len(temp_res_x))

    #res_x = min(center_larger_aera[0], center_bbox[0])+int(abs(center_larger_aera[0]-center_bbox[0])/2)

    #previsous_y = min(center_larger_aera[1], center_bbox[1])+int(abs(center_larger_aera[1]-center_bbox[1])/2)
    #temp_res_y = [center_larger_aera[1], center_bbox[1], bby+bbh, tl.ymax(liste_contours[0])]
    
    temp_res_y = [center_larger_area[1], center_bbox[1]]
    res_y = int(sum(temp_res_y)/len(temp_res_y))

    return res_x , res_y
    


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
            if (dist_x < cf.dC.max_dist_center_x) & (dist_y < cf.dC.max_dist_center_y):

                #check whether adding this contour would create a too big overall area for it to be a person
                minx_temp = min(min([xmin(cnt) for cnt in res_temp]), xmin(c))
                maxx_temp = max(max([xmax(cnt) for cnt in res_temp]), xmax(c))
                width = maxx_temp - minx_temp

                miny_temp = min(min([ymin(cnt) for cnt in res_temp]), ymin(c))
                maxy_temp = max(max([ymax(cnt) for cnt in res_temp]), ymax(c))
                height = maxy_temp - miny_temp

                if (width > cf.dC.min_pers_size_x) & (width < cf.dC.max_pers_size_x):
                    if (height > cf.dC.min_pers_size_y) & (height < cf.dC.max_pers_size_y):
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

    if (xw > cf.dC.min_pers_size_x) & (xw < cf.dC.max_pers_size_x) & (yh < cf.dC.max_pers_size_y) & (yh > cf.dC.min_pers_size_y) & (sum_area > cf.dC.min_size_cnt_pers):
        return True,res_temp
    else:
        return False,[]


#@jit
def update_persons_with_groups(persons, nb_frame, persons_on_frame, VideoSource, groups, timings):
    
    working_temp_p_on_frame = zip(copy(persons_on_frame), [uuid.uuid4() for i in xrange(len(persons_on_frame))])
    update_candidate = []

    
    working_masks = []
    for i, (pf, uid) in enumerate(working_temp_p_on_frame):
        mask1 = np.zeros((VideoSource.new_size[1], VideoSource.new_size[0]), np.uint8)
        cv2.drawContours(mask1, pf, -1, (255,255,255), -1)
        working_masks.append(mask1)
    

    timings['UP_first_loop'] = ti.time()
    for j,p in enumerate(persons):
        update_candidate.append([])    
        for i,(pf, uid) in enumerate(working_temp_p_on_frame):
            
            #if p.exists_at_last_frame(nb_frame-1):
                
                if bbox_overlap(bbox(pf), bbox(p.data[-1][1])):
                    #if contours_intersect(pf, p.data[-1][1], VideoSource):
                    #if contours_intersect(pf, p.mask, VideoSource):
                    if cv2.countNonZero(cv2.bitwise_and(working_masks[i], p.mask)):
                        update_candidate[j].append((bbox_overlap_aera(bbox(pf), bbox(p.data[-1][1])), pf, uid))
                    #p.update(nb_frame, pf, VideoSource)
                    #working_temp_p_on_frame.pop(i)
            #else:
            #    temp_position = calculate_position(pf)
            #    pos_p = p.last_position
            #    if bbox_overlap(bbox(pf), bbox(p.data[-1][1])) & (distance(temp_position, pos_p) < 25):
            #        update_candidate[j].append((bbox_overlap_aera(bbox(pf), bbox(p.data[-1][1])), pf))
    timings['a_UP_first_loop'] = ti.time()


    timings['UP_second_loop'] = ti.time()
    for i,p in enumerate(update_candidate):
        if len(p) > 0:  
            #area, candidate = max_area(p)
            area, candidate, wuid = max(update_candidate[i], key=lambda e : e[0])
            persons[i].update(nb_frame, candidate, VideoSource, persons)

            for id, (k, uid) in enumerate(working_temp_p_on_frame):                
                if wuid == uid:
                    
                #if compare_contours_lists(k, candidate):
                    #working_temp_p_on_frame.pop(id)
                    del working_temp_p_on_frame[id]
    

    timings['a_UP_second_loop'] = ti.time()



    timings['UP_third_loop'] = ti.time()
    for g in groups:
        g.calculate_hist_data()
    for p in persons:
        p.update_position(groups, VideoSource)
    timings['a_UP_third_loop'] = ti.time()

    timings['UP_fourth_loop'] = ti.time()
    for pf, uid in working_temp_p_on_frame:
        new = Person(nb_frame, VideoSource, pf)
        new.update_position(groups, VideoSource)
        x,y = new.last_position
        px, py, pw, ph = new.last_bbox()
        new_person_is_from_group = False
        for gi, g in enumerate(groups):
            if not new_person_is_from_group:
                persi, pers, dist = min([(pei, pe, distance((x,y), pe.last_position)) for pei, pe in enumerate(g.list_persons)], key= lambda i : i[2])
                if dist < 2*max(cf.dC.max_dist_center_x, cf.dC.max_dist_center_y):
                    pers.set_last_contour(new.last_contour())
                    pers.in_group = "0"
                    pers.update_position(groups, VideoSource)
                    g.remove_person(pers)        
                    new_person_is_from_group = True            
                    if len(g.list_persons) == 1:
                        g.list_persons[0].in_group = "0"
                        groups.pop(gi)
        if not new_person_is_from_group:
            persons.append(new)
    timings['a_UP_fourth_loop'] = ti.time()




def update_persons(persons, nb_frame, persons_on_frame, VideoSource, groups, timings):
    
    working_temp_p_on_frame = copy(persons_on_frame)

    for j,p in enumerate(persons):
    
        for i,pf in enumerate(working_temp_p_on_frame):
            if bbox_overlap(bbox(pf), bbox(p.data[-1][1])):
                
                p.update(nb_frame, pf, VideoSource, persons)
                p.update_position(groups, VideoSource)
                working_temp_p_on_frame.pop(i)

    for pf in working_temp_p_on_frame:
        pers = Person(nb_frame, VideoSource, pf)
        pers.update_position(groups, VideoSource)
        persons.append(pers)   
    



def update_groups(VideoSource, persons, groups):
    for i,g in enumerate(groups):
        if len(g.list_persons) == 0:
            groups.pop(i)


    associations = []

    if len(persons) > 1:
                                    
        first_loop = range(len(persons))


        for i in first_loop:
        #for i,p in enumerate(persons):
            p = persons[i]
            if i != len(persons):
                                           
                for j in xrange(i, len(persons)):
                    pe = persons[j]

                    if i!=j:

                        if p.exists_at_last_frame(VideoSource.nb_frame) & pe.exists_at_last_frame(VideoSource.nb_frame):
                                                    
                            if compare_contours_lists(p.last_contour(), pe.last_contour()):
                                associations.append((p, pe))
                                first_loop.remove(j)
                                #print("{} overlap {}".format(p.puuid, pe.puuid))
        for ai, a in enumerate(associations):
            #print("a: {} {}".format(a[0].puuid, a[1].puuid))

            if (a[0].in_group == "0") & (a[1].in_group == "0"):
                group = Group(a[0])
                group.add_person(a[1])
                groups.append(group)
                a[0].in_group = group.id
                a[0].group = group
                a[1].in_group = group.id   
                a[1].group = group
                associations.pop(ai)
                #print("creating new group {} with: {} and {}".format(group.id, a[0].puuid, a[1].puuid))

            for gi, g in enumerate(groups):

                if (a[0].in_group == "0") | (a[1].in_group == "0"):                                        
                    a0_in_g = g.is_in_group(a[0])
                    a1_in_g = g.is_in_group(a[1])

                    if a0_in_g & (not a1_in_g):

                        if a[1].in_group == "0":
                            #print "adding {} to {}".format(a[1].puuid, g.id)
                            a[1].in_group = g.id
                            a[1].group = g
                            g.add_person(a[1])
                            associations.pop(ai)

                    elif (not a0_in_g) & a1_in_g:

                        if a[0].in_group == "0":
                            #print "adding {} to {}".format(a[0].puuid, g.id)
                            a[0].in_group = g.id
                            a[0].group = g
                            g.add_person(a[0])
                            associations.pop(ai)

                elif (a[0].in_group != "0") & (a[1].in_group != "0"):

                    if (a[0].in_group != a[1].in_group):
                                                    
                        if g.is_in_group(a[0]):
                            group = None
                            groupi = -1

                            for gri, gr in enumerate(groups):
                                if gr.id == a[1].in_group:
                                    group = gr
                                    groupi = gri

                            if groupi != -1:
                                for pe in group.list_persons:
                                    g.add_person(pe)
                                    pe.group = g
            
                                groups.pop(groupi)


def kill(zones, persons, groups, i, p, nb_frame, backup):
    p.alive = False;
    previous_zone_id = p.last_zone_id()	
    previous_zone = p.last_zone()
    #p.add_zone(0, nb_frame)
    cf.to_be_sent.append((str(p.uuid), 1, previous_zone_id, time()))
    if previous_zone_id != 1:
        zones.inc_out(previous_zone)

    for gi, g in enumerate(groups):
        g.remove_person(p)

        if len(g.list_persons) == 1:
            g.list_persons[0].in_group = "0"
            groups.pop(gi)
       

    backup.append(copy(p))
    persons.pop(i)
    

def check_for_deaths(zones_detection, zones_io, persons, groups, new_size, nb_frame, backup):
    count_alive = 0
    count_dead = 0
    for i,p in enumerate(persons):
        if p.alive:
            count_alive += 1
            if nb_frame - p.last_frame_seen > cf.NO_SEE_FRAMES_BEFORE_DEATH:
                kill(zones_detection, persons, groups, i, p, nb_frame, backup)
                print("{} {} {} dies    {} age {}".format(nb_frame, time(), p.puuid, p.last_zone(), p.age))
            elif (zones_io.in_zones(p.last_position) != (False, False)) & (( nb_frame - p.last_frame_seen) > cf.NO_SEE_FRAMES_BEFORE_DEATH_BORDERS):
                kill(zones_detection, persons, groups, i, p, nb_frame, backup)
                print("{} {} {} dies    {} age {}".format(nb_frame, time(), p.puuid, p.last_zone(), p.age))
            elif (p.last_seen_frame() < nb_frame-1) & (p.age < 5):
                kill(zones_detection, persons, groups, i, p, nb_frame, backup)
                print("{} {} {} dies    {} age {}".format(nb_frame, time(), p.puuid, p.last_zone(), p.age))
            
        elif not p.alive:
            count_dead += 1
            
    #print('{} persons: {} alive {} dead ({} dead backup)'.format(len(persons), count_alive, count_dead, len(backup)))

def update_persons_zones(persons, nb_frame, zones):
    for p in persons:
        if p.alive:
            if p.exists_at_last_frame(nb_frame):
                
                previous_zone = p.last_zone()
                previous_zone_id = p.last_zone_id()

                new_zone, new_zone_id = zones.in_zones(p.position_last_frame())

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
                            if cf.ZONES_DETECTION_VERBOSE:
                                print('{} {} {} enters  {}'.format(nb_frame, time(), p.puuid, new_zone))
                            cf.to_be_sent.append((str(p.uuid), 2, new_zone_id, time()))
                            zones.inc_in(new_zone)

                        elif (new_zone == 1):
                            if cf.ZONES_DETECTION_VERBOSE:
                                print('{} {} {} leaves  {}'.format(nb_frame, time(), p.puuid, previous_zone))
                            cf.to_be_sent.append((str(p.uuid), 3, previous_zone_id, time()))
                            zones.inc_out(previous_zone)

                        else:
                            if cf.ZONES_DETECTION_VERBOSE:
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

def histBackproj(group, p):
    tot_none_zeros = 0
    for pe in group.list_persons:
        A = cv2.countNonZero(pe.mask)
        tot_none_zeros += A

    tot_post_prob = 0
    for pe in group.list_persons:
        Ap = cv2.countNonZero(pe.mask)
        P = float(Ap)/tot_none_zeros
        Px = pe.hist/Ap
        tot_post_prob += P*Px

    A0 = cv2.countNonZero(p.mask)
    P0 = float(A0)/tot_none_zeros
    Px0 = p.hist/A0
    P0x = Px0*P0 / tot_post_prob
    Prob = np.uint8(P0x*255)
    return Prob


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
    random.seed()
    h = random.randint(0,359)
    return (hsv_to_bgr(h, 1, 1) , hsv_to_bgr(h, 1, 0.5))

def random_color_zones():
    #return np.uint8([[0,0,255]])
    #return cv2.cvtColor(np.ndarray.tolist(cv2.convertScaleAbs(np.random.rand(1,3)*255))[0], cv2.COLOR_HSV2BGR)      
    rand = random.randint(64, 192)
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
        for pos in [p[2] for p in p.data]:
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
    for y in xrange(nb_pos_per_spot.shape[0]):
        for x in xrange(nb_pos_per_spot.shape[1]):

            alpha = heat_linear(min, max, nb_pos_per_spot[y,x])/2 + heat_log(min, max, nb_pos_per_spot[y,x])/2
            #alpha = 0.5
            #temp = frame[x*20:x*20+20, y*20:y*20+20]
            #print("{} {} {} {}".format(y,x, nb_pos_per_spot[y,x],alpha))
            cv2.addWeighted(image, alpha, frame[y*cf.HEAT_MAP_CELL_SIZE:y*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE, x*cf.HEAT_MAP_CELL_SIZE:x*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE], 1 - alpha, 0, frame[y*cf.HEAT_MAP_CELL_SIZE:y*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE, x*cf.HEAT_MAP_CELL_SIZE:x*cf.HEAT_MAP_CELL_SIZE+cf.HEAT_MAP_CELL_SIZE])
            #cv2.putText(frame, "{}".format(nb_pos_per_spot[y,x]), (x*20, y*20+20), cf.FONT, 0.5 , (255,255,255), 1, cv2.CV_AA)
            #frame[x*20:x*20+20, y*20:y*20+20]
    return frame

def random_position(VideoSource):
    return random.randint(0,VideoSource.new_size[0]-200), random.randint(0, VideoSource.new_size[1]-200)

def overlap_persons(bb, persons):
    if len(persons)>0:
        for p in persons:
            p_bbox = bbox(p.data[-1][1])
            if bbox_overlap(bb, p_bbox):
                return True
    return False


def export_negatives(VideoSource, persons):
    for i in xrange(25):
        pos = random_position(VideoSource)
        bbox = (pos[0], pos[1], 200, 200)
        while overlap_persons(bbox, persons):
            pos = random_position(VideoSource)
            bbox = (pos[0], pos[1], 200, 200)

        x,y,w,h = bbox
        cv2.imwrite("neg\img_"+str(VideoSource.nb_frame)+"_"+str(uuid.uuid4())+".png", cv2.cvtColor(VideoSource.current_frame[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY))

def export_positives(VideoSource, persons):
    if (VideoSource.nb_frame > 200):
        for j,p in enumerate(persons):
            if p.alive:
                x,y,w,h = tl.bbox(p.data[-1][1])
                if w > 80:
                    cv2.imwrite("exports\img_"+str(VideoSource.nb_frame)+"_"+p.puuid+".png", cv2.cvtColor(VideoSource.current_frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY))
                        


def heatMapJS(persons, VideoSource):
    nb_persons_per_position = np.zeros((int(VideoSource.new_size[1]), int(VideoSource.new_size[0])), np.uint8)

    for p in persons:
        for pos in [p[2] for p in p.data]:
            nb_persons_per_position[pos[1], pos[0]] += 1
    
    HEAT_DATA_FILE = open("heat_data.js", "w")
    heat_data = {}
    heat_data["max"] = int(np.amax(nb_persons_per_position))
    heat_data["data"] = []
    for y in xrange(nb_persons_per_position.shape[0]):
        for x in xrange(nb_persons_per_position.shape[1]):
            if nb_persons_per_position[y,x] != 0:
                temp = {}
                temp["x"] = x
                temp["y"] = y
                temp["value"] = int(nb_persons_per_position[y,x])
                heat_data["data"].append(temp)

    HEAT_DATA_FILE.write("data=")
    json_data = json.dumps(heat_data)
    HEAT_DATA_FILE.write(json_data)

    HEAT_CSS_FILE = open("heatmap.css", "w")
    HEAT_CSS_FILE.write("#heatmap{}width:{}px; height:{}px;margin-left:auto; margin-right:auto; background-image:url('avg.png'){}".format("{",VideoSource.new_size[0], VideoSource.new_size[1],"}"))





def print_perf(tot, key, nb_frame):
    print('{}: {}ms'.format(key, (float(tot[key])/nb_frame)*1000))