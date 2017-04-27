#Main file 
#import pyximport; pyximport.install()
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
import thread
import time
import os
import dill
import threading
import Queue
from detection_config_settings import DetectionConfig
from random import randint
#from pathos.helpers import mp as multiprocess

class SendDataThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        print("Thread initialized")

    def run(self):
        while not self.stopped():
            time.sleep(cf.API_SLEEP_TIME)
            self.send_data()
            
    def stop(self):
        self._stop.set()
        print("Thread stopping...")
        self.send_data()
        
    def stopped(self):
        return self._stop.isSet()

    def send_data(self):
        if len(cf.to_be_sent) > 0:
            #json preparation

            # event type code:
            # appears: 0
            # dies: 1
            # enters zone: 2
            # exits zone: 3
            
            data = {}
            data['timestamp'] = tl.time()
            data['logs'] = []
            data['debug'] = cf.API_DEBUG
            #data['camera_id'] = cf.CAMERA_ID
            
            for p in cf.to_be_sent:
                temp = {}
                temp['subjectId'] = p[0]
                temp['eventType'] = p[1]
                temp['zoneId'] = p[2]
                temp['timestamp'] = p[3]

                data['logs'].append(temp)

            send_json = json.dumps(data)
            cf.OUTPUTFILE.write("\n"+send_json)
            if cf.SEND_DATA:
                print("API debug {} sending {} items".format(cf.API_DEBUG, len(cf.to_be_sent)))
                if (self.post_results(data)):
                    cf.to_be_sent = []


    def post_results(self, data):
        send_json = json.dumps(data)
        cf.OUTPUTFILE.write("\n"+send_json)
        headers = {'Content-type':'application/json'}
        try:
            res = requests.post(cf.API_POST_RESULTS, data=send_json, headers=headers)
            if res.status_code == 200:
                print("API Status 200 response: {}".format(res.text))
                return True
            elif res.status_code == 500:
                print("API Status Response {}".format(res.status_code))
                #print("API Response: {}".format(res.text))
                return True
            else:
                print("API Status Response {}".format(res.status_code))
                print("API Response: {}".format(res.text))
        except Exception as e:
            msg = "Exception in post request:\n %s \n" % e
            print(msg)
        
class ProcessThread(threading.Thread):
    def __init__(self, queue_in, queue_out, VideoSource, fgbg, zones_detection, zones_io, persons, backup):
        threading.Thread.__init__(self)
        self.queue_in = queue_in
        self.queue_out = queue_out      
        self.VideoSource = VideoSource
        self.fgbg = fgbg
        self.zones_detection = zones_detection
        self.zones_io = zones_io
        self.persons = persons
        self.backup = backup

    def run(self):
        processThread(self.queue_in, self.queue_out, self.VideoSource, self.fgbg, self.zones_detection, self.zones_io, self.persons, self.backup)

def processThread(queue_in, queue_out, VideoSource, fgbg, zones_detection, zones_io, persons, backup):

    while(True):
        try:
            stop = queue_in.get(block=False)

            if not stop:
                ret, frame = VideoSource.next_frame()
    
                if not ret:
                    print('End of video {}'.format(VideoSource.name_source))
                    queue_out.put(False)
                    return 1

                else:
                    #print "FRAME {}".format(VideoSource.nb_frame)
                    start=time.time()
                    foreground = fgbg.update(frame, VideoSource.nb_frame)

                    if VideoSource.nb_frame >= cf.TRAIN_FRAMES:
        
    
                        tl.check_for_deaths(zones_detection, zones_io, persons, VideoSource.new_size, VideoSource.nb_frame, backup)
                        temp_recherche_contour = copy(foreground)
                        contours, hierarchy = cv2.findContours(temp_recherche_contour, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        temp_persons_detected = []

                        if len(contours) > 0:
                            contours = [cv2.convexHull(c) for c in contours if cv2.contourArea(c) > cf.dC.cnt_min]


                            if len(contours) > 0:

                                
                                contours.sort(tl.compare_contour_aera)
                                previous_len_cnt = 0
                
                                while len(contours) > 0 & previous_len_cnt < len(contours):
                                    res, l = tl.search_person_on_frame(contours)
                                    if res:
                                        temp_persons_detected.append(l)
                                    previous_len_cnt = len(contours)

                                if (len(temp_persons_detected) > 0):
                                    tl.update_persons(persons, VideoSource.nb_frame, temp_persons_detected, VideoSource)                                    
                                    tl.update_persons_zones(persons, VideoSource.nb_frame, zones_detection)

                    end=time.time()
                    queue_out.put(True)

            else:
                break

        except:
            pass



class DrawThread(threading.Thread):
    def __init__(self, queue_in, queue_out, VideoSource, persons, zones_detection, zones_io, zones_portal, backup, logo, init):
        threading.Thread.__init__(self)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.VideoSource = VideoSource
        self.persons = persons
        self.zones_detection = zones_detection
        self.zones_io = zones_io
        self.zones_portal = zones_portal    
        self.backup = backup 
        self.logo = logo        
        self.init = init

    def run(self):
        drawThread(self.queue_in, self.queue_out, self.VideoSource, self.persons, self.zones_detection, self.zones_io, self.zones_portal, self.backup, self.logo, self.init)
      
def drawThread(queue_in, queue_out, VideoSource, persons, zones_detection, zones_io, zones_portal, backup, logo, init):
    while(True):

        try:
            stop = queue_in.get(block=False)

            if not stop:    

                frame = VideoSource.current_frame

                if VideoSource.nb_frame > cf.TRAIN_FRAMES:
                    if cf.DRAW_CONFIG:
                        draw_config(VideoSource, frame)
                    if cf.DRAW_ZONES_IO:
                        draw_zones(zones_io, frame)
                    if cf.DRAW_ZONES_DETECTION:
                        draw_zones(zones_detection, frame)
                    if cf.DRAW_ZONES_PORTAL:
                        draw_zones(zones_portal, frame)
                    if cf.DRAW_PERSONS:
                        draw_persons(persons, VideoSource, frame)

                else:
                    draw_init_frame(VideoSource, frame, init)

                border = generate_border(VideoSource, logo, persons, backup, zones_detection, VideoSource.name_source)
                frame = assemble_frame_border(frame, border)   

                queue_out.put(frame)

            else:
                break
        except Queue.Empty:
            pass
    


def print_annotation(frame, VideoSource, persons, backup, zones):

    lignes = []
    temp = copy(frame)
        
    #if self.display_frame_dim:
    lignes.append(str(int(VideoSource.new_size[0]))+"x"+str(int(VideoSource.new_size[1])))

    #if self.display_frame_number:
    lignes.append("Frame {}/{}".format(str(VideoSource.nb_frame), str(int(VideoSource.nb_total_frame))))

    lignes.append("FPS "+str(round(VideoSource.nb_frame/(time.time()-cf.T_START),2)))
    lignes.append("{} alive".format(len(persons)))
    lignes.append("{} dead".format(len(backup)))
    
    for z in zones.masks:
        lignes.append("Zone {}: {} objects".format(z[3], zones.count["entries"][z[0]] - zones.count["exits"][z[0]]))

    #write the lignes on the frame
    for ligne in enumerate(lignes):
        cv2.putText(temp,ligne[1],(0,12*(ligne[0]+1)+3*ligne[0]), cf.FONT, 0.5,cf.ANOTATION_COLOR,2)
        
    return temp

def draw_config(VideoSource, frame_annotation):
    #show config distance and size at the bottom of the frame
    
    #vertical
    cv2.line(frame_annotation, (4, int(VideoSource.new_size[1])), (4, int(VideoSource.new_size[1])-cf.dC.min_pers_size_y),  (0,0,255),1)
    cv2.line(frame_annotation, (8, int(VideoSource.new_size[1])), (8, int(VideoSource.new_size[1])-cf.dC.max_pers_size_y), (0,255,0),1)
    cv2.line(frame_annotation, (12, int(VideoSource.new_size[1])), (12, int(VideoSource.new_size[1])-cf.dC.max_dist_center_y), (255,0,0), 1)
    
    #horizontal
    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-4), (cf.dC.min_pers_size_x, int(VideoSource.new_size[1])-4), (0,0,255),1)
    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-8), (cf.dC.max_pers_size_x, int(VideoSource.new_size[1])-8), (0,255,0),1)
    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-12), (cf.dC.max_dist_center_x, int(VideoSource.new_size[1])-12), (255,0,0), 1)
    
    #recording dot
    #cv2.circle(frame_annotation, (int(VideoSource.new_size[0])-16, 15), 6, (0,255,0), -1)

    #dead zones
    '''
    cv2.line(frame_annotation, ( cf.DEAD_ZONE_X, 0), (cf.DEAD_ZONE_X, int(VideoSource.new_size[1])), (255,255, 0), 1)
    cv2.line(frame_annotation, ( int(VideoSource.new_size[0]) - cf.DEAD_ZONE_X, 0), ( int(VideoSource.new_size[0]) - cf.DEAD_ZONE_X, int(VideoSource.new_size[1])), (255,255, 0), 1)
    cv2.line(frame_annotation, (0, cf.DEAD_ZONE_Y), (int(VideoSource.new_size[0]), cf.DEAD_ZONE_Y), (255, 255, 0), 1)
    cv2.line(frame_annotation, (0, int(VideoSource.new_size[1]) - cf.DEAD_ZONE_Y), (int(VideoSource.new_size[0]), int(VideoSource.new_size[1]) - cf.DEAD_ZONE_Y), (255, 255, 0), 1)
    '''
    '''
    for x in range(int(VideoSource.new_size[0])/20):
        cv2.line(frame_annotation, (x*20, 0), (x*20, int(VideoSource.new_size[1])), (255,255,255), 1, cv2.CV_AA)

    for y in range(int(VideoSource.new_size[1])/20):
        cv2.line(frame_annotation, (0, y*20), (int(VideoSource.new_size[0]), y*20), (255,255,255), 1, cv2.CV_AA)
    '''      

def draw_zones(zones, frame_annotation):
    if zones.nb_zones() > 0:

        if zones.mode == "detection":
            overlay = frame_annotation.copy()
            for m in zones.masks:
                cv2.drawContours(overlay, m[1], -1, m[2][1], -1)
                (x, y, w, h) = tl.bbox(m[1])                    
                section_overlay = overlay[y:y+h, x:x+w] 
                section_frame_annotation = frame_annotation[y:y+h, x:x+w]
                cv2.addWeighted(section_overlay, 0.15, section_frame_annotation, 1 - 0.15, 0, section_frame_annotation)
                frame_annotation[y:y+h, x:x+w] = section_frame_annotation
                for c in m[1]:
                    cv2.drawContours(frame_annotation, [c], 0, m[2][1], 2, cv2.CV_AA)
                    cv2.drawContours(frame_annotation, [c], 0, (255,255,255), 1, cv2.CV_AA)

                cv2.putText(frame_annotation, str(m[3]), (x, y+48), cf.FONT, 2, m[2][0], 3, cv2.CV_AA)
                cv2.putText(frame_annotation, str(m[3]), (x, y+48), cf.FONT, 2, (255,255,255), 1, cv2.CV_AA)

        elif zones.mode == "portal":
            for m in zones.masks:
                for c in m[1]:
                        cv2.drawContours(frame_annotation, [c], 0, (239, 173, 0), 6, cv2.CV_AA)
                        cv2.drawContours(frame_annotation, [c], 0, (0, 106, 255), 2, cv2.CV_AA)

        elif zones.mode == "io":
            overlay = frame_annotation.copy()
            for m in zones.masks:
                cv2.drawContours(overlay, m[1], -1, (255,255,255), -1)

                cv2.addWeighted(overlay, 0.2, frame_annotation, 1-0.2, 0, frame_annotation)
                
def draw_persons(persons, VideoSource, frame_annotation):
            
    #check among the persons we have registered, which are currently on the frame so we can draw informations about them
    #frame_annotation_copy = frame_annotation.copy()
    persons_to_draw = [p for p in persons if p.exists_at_last_frame(VideoSource.nb_frame) & p.alive]
    if len(persons_to_draw) > 0:
                                                
        #draw bbox, contours and position on the frame for each personz
        for per in persons_to_draw:
                    
            #draw the contours we have of that person on that frame
            cv2.drawContours(frame_annotation, per.contour_last_frame(VideoSource.nb_frame), -1, per.couleur_dark, 1, cv2.CV_AA)
            
            overlay = frame_annotation.copy()
            cv2.drawContours(overlay, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, -1)
            cv2.addWeighted(overlay, cf.ALPHA, frame_annotation, 1 - cf.ALPHA, 0, frame_annotation)
            cv2.drawContours(frame_annotation, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, 1, cv2.CV_AA)
            
            #obtain current person's bounding box in order to draw on the displayed frame
            (x,y,w,h) = per.bbox_last_frame(VideoSource.nb_frame)
            cv2.rectangle(frame_annotation, (x, y), (x+w, y+h), per.couleur, 2)
            cv2.rectangle(frame_annotation, (x, y), (x+48, y+12), per.couleur, -1)
            cv2.putText(frame_annotation, per.puuid, (x+2, y+12), cf.FONT, 0.4, (0,0,0), 2, cv2.CV_AA)
            cv2.putText(frame_annotation, per.puuid, (x+2, y+12), cf.FONT, 0.4, (255,255,255), 1, cv2.CV_AA)
                            
            #draw current person's position on the frame
            cv2.circle(frame_annotation, per.position_last_frame(), 3, per.couleur, -1, cv2.CV_AA)
            
            if cf.DRAW_PERSON_PATH_TAIL:
                previous_pos = (0,0)
            
                #for i,p in enumerate(per.liste_positions[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]):
                for i,p in enumerate([d[2] for d in per.data[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]]):
                    if (i>0):
                        cv2.line(frame_annotation, previous_pos, p, per.couleur, 2, cv2.CV_AA)
                    previous_pos = p
            
def generate_border(VideoSource, logo,  persons, backup, zones, name_source, drawlogo=True):
    temp = np.ones((48,int(VideoSource.new_size[0]), 3), np.uint8)
    temp[:,:] = (255,255,255)

    nb_line = 2
    nb_column = 5

    width_printing_area = temp.shape[1]-logo.shape[1]
    width_column = int(width_printing_area / nb_column)
    height_line = 18

    lines = []
    lines.append((name_source.title(),  cf.BORDER_TEXT_COLOR))
    lines.append((str(int(VideoSource.new_size[0]))+"x"+str(int(VideoSource.new_size[1])), cf.BORDER_TEXT_COLOR))

    if int(VideoSource.nb_total_frame) > 0:
        lines.append(("Frame {}/{}".format(str(VideoSource.nb_frame), str(int(VideoSource.nb_total_frame))), cf.BORDER_TEXT_COLOR))
    else:
        lines.append(("Frame {}".format(str(VideoSource.nb_frame)), cf.BORDER_TEXT_COLOR))

    #lines.append(("Frame {}/{}".format(str(VideoSource.nb_frame), str(nb_total_frame)), cf.BORDER_TEXT_COLOR))
    lines.append(("FPS "+str(round(VideoSource.nb_frame/(time.time()-cf.T_START),2)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} alive".format(len(persons)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} dead".format(len(backup)), cf.BORDER_TEXT_COLOR))

    for z in zones.masks:
        lines.append(("{}: {} items".format(z[3], zones.count["entries"][z[0]] - zones.count["exits"][z[0]]), z[2][1]))

    for i,t in enumerate(lines):
        cv2.putText(temp, t[0], (width_column*(i/nb_line),height_line*((i%nb_line)+1)), cf.FONT, 0.5, t[1], 1, cv2.CV_AA)

    if drawlogo:
        temp[0:logo.shape[0], temp.shape[1]-logo.shape[1]:int(VideoSource.new_size[0])] = logo

    return temp 

def assemble_frame_border(frame, border):
    temp = np.ones((frame.shape[0]+border.shape[0], frame.shape[1], 3), np.uint8)
    temp[:,:] = (255,255,255)
    temp[0:frame.shape[0], 0:frame.shape[1]] = frame
    temp[frame.shape[0]:frame.shape[0]+48, 0:border.shape[1]] = border

    return temp

def draw_init_frame(VideoSource, frame, init_file):
    
    temp = np.ones((int(VideoSource.new_size[1]),int(VideoSource.new_size[0]), 3), np.uint8)
    temp[:,:] = (0,0,0)

    x = int(VideoSource.new_size[0]/2 - init_file.shape[1] / 2)
    y = int(VideoSource.new_size[1]/2 - init_file.shape[0] / 2)
    w = init_file.shape[1]
    h = init_file.shape[0]

    temp[y:y+h, x:x+w] = init_file

    alpha = 0.2

    cv2.addWeighted(frame, alpha, temp, 1 - alpha, 0, frame)

def merge_frame(frameA, frameB):
    temp = np.zeros((frameA.shape[0], frameA.shape[1] + frameB.shape[1], 3), np.uint8)
    temp[0:frameA.shape[0], 0:frameA.shape[1]] = frameA
    temp[0:frameB.shape[0], frameA.shape[1]:frameA.shape[1] + frameB.shape[1]] = frameB

    return temp

def merge_fg(frameA, frameB):
    temp = np.zeros((frameA.shape[0], frameA.shape[1] + frameB.shape[1]), np.uint8)

    temp[0:frameA.shape[0], 0:frameA.shape[1]] = frameA
    temp[0:frameB.shape[0], frameA.shape[1]:frameA.shape[1] + frameB.shape[1]] = frameB

    return temp

def main():

    cv2.setUseOptimized(True)
    print("Start time {}".format(tl.time()))
    
    #initialisation
    
    #parse arguments
    args = parse.parser()

    cf.dC = DetectionConfig("chuteLab")
    #print("Config: {}".format(cf.ACTIVE_CONFIG_SET))


    cf.FG_O_OP=1    #10 #opening
    cf.FG_C_OP=6    #15 #closing

    cf.STR_ELEMENT=cv2.MORPH_ELLIPSE

    cf.o_kernel=cv2.getStructuringElement(cf.STR_ELEMENT,(cf.FG_O_OP,cf.FG_O_OP))
    cf.c_kernel=cv2.getStructuringElement(cf.STR_ELEMENT,(cf.FG_C_OP,cf.FG_C_OP))  

    
    logo_file = cv2.imread(cf.LOGO_FILE)
    init_file = cv2.imread(cf.INIT_FILE)


    VIDEO_SOURCE = []
    VIDEO_SOURCE.append(("rtsp://admin:Azemlk123@192.168.1.246/play2.sdp", "lab"))
    VIDEO_SOURCE.append(("rtsp://admin:Azemlk123@192.168.1.31/play2.sdp", "fablab"))
    #VIDEO_SOURCE.append(("..\\dataset\\street\\04\\street960.mp4", ""))


    data = []
    for source in VIDEO_SOURCE:


        if source[1] != "":
            VideoSource = Source(source[0], name_source=source[1])
        else:
            VideoSource = Source(source[0])

        fgbg = ForgroundExtraction(cf.ALGO, VideoSource.new_size)
        persons = []
        backup = []

        zones_detection = Zones(VideoSource.name_source, VideoSource.new_size, mode='detection')
        zones_io = Zones(VideoSource.name_source, VideoSource.new_size, mode="io")
        zones_portal = Zones(VideoSource.name_source, VideoSource.new_size, mode="portal")
        frame = np.zeros((int(VideoSource.new_size[1]), int(VideoSource.new_size[0]), 3), np.uint8)

        data.append([VideoSource, fgbg, persons, backup, zones_detection, zones_io, zones_portal, frame])

    at_least_one_portal_by_frame = True

    for d in data:
        if d[6].nb_zones() == 0:
            at_least_one_portal_by_frame = False

    threads_processing = []
    threads_drawing = []

    cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)	

    size_window_h = max([d[0].new_size[1] for d in data]) + 48
    size_window_w = sum([d[0].new_size[0] for d in data])

    #cv2.resizeWindow("Tracking", 2*int(data[0][0].new_size[0]), int(data[0][0].new_size[1])+48)
    cv2.resizeWindow("Tracking", size_window_w, size_window_h)



    for d in data:
        q_processing_in = Queue.Queue()
        q_processing_out = Queue.Queue()
        t_processing = ProcessThread(q_processing_in, q_processing_out, d[0], d[1], d[4], d[5], d[2], d[3])
        #t_processing = multiprocess.Process(target=processThread, args=(q_processing_in, q_processing_in, d[0], d[1], d[4], d[5], d[2], d[3]))
        threads_processing.append([q_processing_in, q_processing_out, t_processing])
        
        q_drawing_in = Queue.Queue()
        q_drawing_out = Queue.Queue()
        t_drawing = DrawThread(q_drawing_in, q_drawing_out, d[0], d[2], d[4], d[5], d[6], d[3], logo_file, init_file)
        threads_drawing.append([q_drawing_in, q_drawing_out, t_drawing])


    
    for i,o,t in threads_processing:
        t.start()


    for i,o,t in threads_drawing:
        t.start()
    

    cf.dC.resize_config(data[0][0].new_size[0], data[0][0].new_size[1])


    #init thread in charge of sending data to the api endpoint
    sendingDataThread = SendDataThread()

    #start the thread which sends the data
    #sendingDataThread.start()


    #main loop
    print("Start training background detection")

    cf.T_START = time.time()

    timer = []

    while (True):

        print("-------")
        #break on key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break   
        

        '''
        '
        '   PROCESSING
        '
        '''  

        timr = {}

        timr['process'] = time.time()
        
        for i,o,t in threads_processing:
            i.put(False)
        
        timr['a_process'] = time.time()


        '''
        while not all(finished):
            for i,t in enumerate(threads_processing):
                try:
                    temp = t[1].get()
                    data[i][7] = temp
                    finished[i] = True
                except:
                    pass
        '''
        
        for j,th in enumerate(threads_processing):
            i,o,t = th
            timr['wait_process'] = time.time()
            o.get(block=True)
            timr['a_wait_process'] = time.time()
            

        #data.append([VideoSource, fgbg, persons, backup, zones_detection, zones_io, zones_portal])
            

        #except:
        #print "Error processing"
        persons_on_each_frame = True
        for d in data:
            if len(d[2]) == 0:
                persons_on_each_frame = False
                

        #wait TRAIN_FRAMES frames to train the background
        passed_train_frames = True

        for d in data:
            if d[0].nb_frame < cf.TRAIN_FRAMES:
                passed_train_frames = False
                

        if passed_train_frames:
            #transfert testing
            if persons_on_each_frame:


                if at_least_one_portal_by_frame:

                    transfer = []
                    


                    foundA = False
                    foundB = False
                    transferA = None
                    transferB = None
                    zone_nameA = ""
                    zone_nameB = ""

                    '''
                    for i,d in enumerate(data):
                        for p in d[2]:
                            if p.alive & p.exists_at_last_frame(d[0].nb_frame):
                                name, id = d[6].in_zones(p.position_last_frame())
                                if name != False:
                                    transfer.append((i, name, p))
                    '''
                    
                    for p in data[0][2]:
                        if p.alive & p.exists_at_last_frame(data[0][0].nb_frame):
                            zone_nameA, zone_idA = data[0][6].in_zones(p.position_last_frame())
                            if zone_nameA != False:
                                print zone_nameA
                                transferA = p
                                foundA = True
                                break
                        
                    for p in data[1][2]:
                        if p.alive & p.exists_at_last_frame(data[1][0].nb_frame):
                            zone_nameB, zone_idB = data[1][6].in_zones(p.position_last_frame())
                            if zone_nameB != False:
                                print zone_nameB
                                transferB = p
                                foundB = True
                                break    
                    '''

                    while len(transfer) > 1:
                        for j1, t1 in enumerate(transfer):
                            i1, n1, p1 = t1
                            for j2, t2 in enumerate(transfer):
                                i2, n2, p2 = t2

                                if i1 != i2:
                                    if n1 == n2 & p1.uuid != p2.uuid:
                                        p2.uuid = p1.uuid
                                        p2.puuid = p1.uuid
                                        p2.couleur = p1.couleur
                                        p2.couleur_dark = p1.couleur_dark

                                        transfer.pop(p1)
                                        transfer.pop(p2)      

                    '''
                    if foundA & foundB:
                        if (zone_nameA == zone_nameB) & (transferB.uuid != transferA.uuid):
                            transferB.uuid = transferA.uuid
                            transferB.puuid = transferA.puuid
                            transferB.couleur = transferA.couleur
                            transferB.couleur_dark = transferA.couleur_dark   
                            print "TRANSFERT DONE"      
                               

        '''
        '
        '   DRAWING     
        '
        '''
        
        if (d[0].nb_frame % cf.DISPLAYED_FRAME == 0):

            #if passed_train_frames:
            
            timr['drawing'] = time.time()
            for i,o,t in threads_drawing:
                i.put(item=False)


            for j,th in enumerate(threads_drawing):
                i,o,t = th
                timr['wait_draw'] = time.time()
                data[j][7] = o.get(block=True)
                timr['a_wait_draw'] = time.time()

            timr['a_drawing'] = time.time()
            
            



            #display the frame
            '''
            if cf.SHOW_FG:
                mergeFG = merge_fg(forgroundA, forgroundB)
                cv2.imshow('Forground detection', mergeFG)
            '''
            '''
            for d in data:
                cv2.imshow(d[0].name_source, d[7])
            '''
            
            if len(data) > 1:
                merge = merge_frame(data[0][7], data[1][7])
                cv2.imshow('Tracking',merge)
            else:
                cv2.imshow("Tracking", data[0][7])
            
        timer.append(timr)


    t_end = time.time()

    print("Killing processing threads...")
    for i,o,t in threads_processing:
        i.put(item=True, block=True)
        t.join()
        
    print("Killin drawing threads...")
    for i,o,t in threads_drawing:
        i.put(item=True, block=True)
        t.join()


    #killing aliove persons
    for d in data:
        print("Killing {} current alive item {}".format(len(d[2]), d[0].name_source))
        for i,p in enumerate(d[2]):
            print("{} {} {} dies    {} age {}".format(d[0].nb_frame, tl.time(), p.puuid, p.last_zone(), p.age))
            tl.kill(d[4], d[2], i, p, d[0].nb_frame, d[3])
    

    #clean stop the thread sending the data
    sendingDataThread.stop()
    sendingDataThread.join()
    print("Thread stopped")


    #release the camera and eventually the output video file
    for d in data:
        d[0].release()


    #close all windows properly
    cv2.destroyAllWindows()


    print("--------------------------")
    
    for d in data:
        print("Summary {}".format(d[0].name_source))
        #data = {'persons':[]}
    
        print("{} Frames".format(d[0].nb_frame))
        print("{} s".format(round(t_end - cf.T_START, 2)))
        print("{} AVG FPS".format(float(d[0].nb_frame)/(t_end-cf.T_START)))
        print("{} ms/frame".format(round(((t_end-cf.T_START)*1000)/float(d[0].nb_frame), 2)))
        print("--------------------------")

        print("Persons {}".format(d[0].name_source))
        print("{} persons detected".format(len(d[2])+len(d[3])))
    
        #print(str(p.uuid)+ ": "+ str(len(p.liste_positions)) +" positions detected")
        #print("{} age {}".format(p.uuid, p.age))
    
        print("--------------------------")
        print("Zones {}".format(d[0].name_source))

        print("{} detection zones".format(len(d[4].masks)))
        for m in d[4].masks:
            print("{} in {} out {}".format(m[0].title(), d[4].count["entries"][m[0]], d[4].count["exits"][m[0]]))
        print("{} io zones".format(len(d[5].masks)))
        print("{} portal zones".format(len(d[6].masks)))


        print("--------------------------")
   



    print("Timings")

    tot = {}
    tot['process'] = 0
    tot['drawing'] = 0
    tot['wait_process'] = 0
    tot['wait_draw'] = 0

    for t in timer:
    
        if 'process' in t:
            tot['process'] += t['a_process'] - t['process']
 
        if 'drawing' in t:
            tot['drawing'] += t['a_drawing'] - t['drawing'] 

        if 'wait_process' in t:
            tot['wait_process'] += t['a_wait_process'] - t['wait_process']

        if 'wait_draw' in t:
            tot['wait_draw'] += t['a_wait_draw'] - t['wait_draw']


    for t in tot:
        print('{}: {}ms'.format(t, (float(tot[t])/data[0][0].nb_frame)*1000))


    return 0

if __name__ == "__main__":
    main()

