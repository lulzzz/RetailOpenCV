        #Main file 
#import pyximport; pyximport.install()
import numpy as np
import cv2
import config as cf
import arg_parser as parse
import tools as tl
#import cython_tools as ctl
from datetime import datetime
import logging
from Source import Source
from ForgroundExtraction import ForgroundExtraction
from Person import Person
from Group import Group
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
import profile

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

def draw_config(VideoSource, frame_annotation, zones):
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
                
def draw_persons(persons, VideoSource, frame_annotation, frame_annotation_copy):
            
    #check among the persons we have registered, which are currently on the frame so we can draw informations about them
    
    persons_alive = [p for p in persons if (p.exists_at_last_frame(VideoSource.nb_frame) & (p.in_group == "0"))]
    if len(persons_alive) > 0:
                                                
        #draw bbox, contours and position on the frame for each person
        for per in persons_alive:
            #draw the contours we have of that person on that frame
            cv2.drawContours(frame_annotation, per.contour_last_frame(VideoSource.nb_frame), -1, per.couleur_dark, 1, cv2.CV_AA)
            
            #overlay = frame_annotation.copy()
            #cv2.drawContours(overlay, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, -1)
            #cv2.addWeighted(overlay, cf.ALPHA, frame_annotation_copy, 1 - cf.ALPHA, 0, frame_annotation)
            cv2.drawContours(frame_annotation, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, 1, cv2.CV_AA)
            
            #obtain current person's bounding box in order to draw on the displayed frame
            (x,y,w,h) = per.bbox_last_frame(VideoSource.nb_frame)
            cv2.rectangle(frame_annotation, (x, y), (x+w, y+h), per.couleur, 2)

            cv2.rectangle(frame_annotation, (x, y), (x+48, y+12), per.couleur, -1)
            cv2.putText(frame_annotation, "{}".format(per.puuid), (x+2, y+12), cf.FONT, 0.4, (0,0,0), 2, cv2.CV_AA)
            cv2.putText(frame_annotation, "{}".format(per.puuid), (x+2, y+12), cf.FONT, 0.4, (255,255,255), 1, cv2.CV_AA)

            #cv2.putText(frame_annotation, "{}".format(per.age), (x+2, y+24), cf.FONT, 0.4, (0,0,0), 2, cv2.CV_AA)
            #cv2.putText(frame_annotation, "{}".format(per.age), (x+2, y+24), cf.FONT, 0.4, (255,255,255), 1, cv2.CV_AA) 
     
            if cf.DRAW_PERSON_PATH_TAIL:
                previous_pos = (0,0)
                #for i,p in enumerate(per.liste_positions[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]):
                for i,p in enumerate([d[2] for d in per.data[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]]):
                    if (i>0):
                        cv2.line(frame_annotation, previous_pos, p, per.couleur, 1, cv2.CV_AA)
                    previous_pos = p

            #draw current person's position on the frame
            cv2.circle(frame_annotation, per.position_last_frame(), 4, per.couleur, -1, cv2.CV_AA)
            cv2.circle(frame_annotation, per.position_last_frame(), 2, (255,255,255), -1, cv2.CV_AA)
            

              
    if cf.DRAW_PERSONS_WAITING:

        persons_alive = [p for p in persons if ((not (p.exists_at_last_frame(VideoSource.nb_frame))) & (p.in_group == "0"))]
        if len(persons_alive) > 0:
        #draw bbox, contours and position on the frame for each person
            for per in persons_alive:
                #draw the contours we have of that person on that frame
                cv2.drawContours(frame_annotation, per.last_contour(), -1, (0,0,0), 1, cv2.CV_AA)
            
                #overlay = frame_annotation.copy()
                #cv2.drawContours(overlay, [per.last_contour()[0]], 0, (0,0,0), -1)
                #cv2.addWeighted(overlay, cf.ALPHA, frame_annotation_copy, 1 - cf.ALPHA, 0, frame_annotation)
                #cv2.drawContours(frame_annotation, [per.last_contour()[0]], 0, (0,0,0), 1, cv2.CV_AA)
            
                #obtain current person's bounding box in order to draw on the displayed frame
                (x,y,w,h) = per.last_bbox()
                cv2.rectangle(frame_annotation, (x, y), (x+w, y+h), (0,0,0), 2)

                cv2.rectangle(frame_annotation, (x, y), (x+48, y+12), (0,0,0), -1)
                cv2.putText(frame_annotation, "{}".format(per.puuid), (x+2, y+12), cf.FONT, 0.4, per.couleur, 2, cv2.CV_AA)
                cv2.putText(frame_annotation, "{}".format(per.puuid), (x+2, y+12), cf.FONT, 0.4, (0,0,0), 1, cv2.CV_AA)

                #cv2.putText(frame_annotation, "{}".format(per.age), (x+2, y+24), cf.FONT, 0.4, (0,0,0), 2, cv2.CV_AA)
                #cv2.putText(frame_annotation, "{}".format(per.age), (x+2, y+24), cf.FONT, 0.4, (255,255,255), 1, cv2.CV_AA) 
                            
                #draw current person's position on the frame
                cv2.circle(frame_annotation, per.position_last_frame(), 4, per.couleur, -1, cv2.CV_AA)
                cv2.circle(frame_annotation, per.position_last_frame(), 2, (0,0,0), -1, cv2.CV_AA)
            
def draw_groups(groups, VideoSource, frame):

    for g in groups:
        if g.list_persons[0].exists_at_last_frame(VideoSource.nb_frame):

                p = g.list_persons[0]

                cv2.drawContours(frame, p.last_contour(), -1, (255,255,255), 1, cv2.CV_AA)

                #overlay = frame.copy()
                #cv2.drawContours(overlay, [p.last_contour()[0]], 0, (255,255,255), -1)
                #cv2.addWeighted(overlay, cf.ALPHA, frame, 1 - cf.ALPHA, 0, frame)
                #cv2.drawContours(frame, [p.last_contour()[0]], 0, (255,255,255), 1, cv2.CV_AA)

                (x,y,w,h) = p.last_bbox()
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,255), 2)

                for i, per in enumerate(g.list_persons):
                    cv2.rectangle(frame, (x, y+(i*12)), (x+48, y+((i+1)*12)), per.couleur, -1)
                    cv2.putText(frame, "{}".format(per.puuid), (x+2, y+12*(i+1)), cf.FONT, 0.4, (0,0,0), 2, cv2.CV_AA)
                    cv2.putText(frame, "{}".format(per.puuid), (x+2, y+12*(i+1)), cf.FONT, 0.4, (255,255,255), 1, cv2.CV_AA)

                    if cf.DRAW_PERSON_PATH_TAIL:
                        previous_pos = (0,0)
                        #for i,p in enumerate(per.liste_positions[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]):
                        for i,p in enumerate([d[2] for d in per.data[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]]):
                            if (i>0):
                                cv2.line(frame, previous_pos, p, per.couleur, 1, cv2.CV_AA)
                            previous_pos = p

                    cv2.circle(frame, per.position_last_frame(), 4, per.couleur, -1, cv2.CV_AA)
                    cv2.circle(frame, per.position_last_frame(), 2, (255,255,255), -1, cv2.CV_AA)


def generate_border(VideoSource, logo,  persons, backup, zones):
    temp = np.ones((48,int(VideoSource.new_size[0]), 3), np.uint8)
    temp[:,:] = (255,255,255)

    nb_line = 2
    nb_column = 5

    width_printing_area = temp.shape[1]-logo.shape[1]
    width_column = int(width_printing_area / nb_column)
    height_line = 18

    lines = []
    lines.append((VideoSource.name_source.title(),  cf.BORDER_TEXT_COLOR))
    lines.append((str(int(VideoSource.new_size[0]))+"x"+str(int(VideoSource.new_size[1])), cf.BORDER_TEXT_COLOR))
    lines.append(("Frame {}/{}".format(str(VideoSource.nb_frame), str(int(VideoSource.nb_total_frame))), cf.BORDER_TEXT_COLOR))
    lines.append(("FPS "+str(round(VideoSource.nb_frame/(time.time()-cf.T_START),2)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} alive".format(len(persons)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} dead".format(len(backup)), cf.BORDER_TEXT_COLOR))

    for z in zones.masks:
        lines.append(("{}: {} ({})".format(z[3], zones.count["entries"][z[0]], zones.count["entries"][z[0]] - zones.count["exits"][z[0]]), z[2][1]))

    for i,t in enumerate(lines):
        cv2.putText(temp, t[0], (width_column*(i/nb_line),height_line*((i%nb_line)+1)), cf.FONT, 0.5, t[1], 1, cv2.CV_AA)

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


def main():
    #raw_input("Press enter to begin...")

    cv2.setUseOptimized(True)
    print("Start time {}".format(tl.time()))
    
    #initialisation
    
    #parse arguments
    args = parse.parser()

    #input argument 
    if args.input:
        if args.input == "0":
            input_video = 0
        elif args.input == "1":
            input_video = 1
        else:
            input_video = args.input
    else:
        input_video = cf.VIDEO_SOURCE

    #config argument
    if args.config:
        if args.config in cf.dC.configs:
            cf.ACTIVE_CONFIG_SET = args.config
            cf.dC = DetectionConfig(args.config)
        else:
            print("Config not found, using {}".format(cf.ACTIVE_CONFIG_SET))

    print("Config: {}".format(cf.ACTIVE_CONFIG_SET))

    if(input_video==0)|(input_video==1):
        name_source = "Webcam"
    else:
        name_source = os.path.basename(input_video).split('.')[0]

    VideoSource = Source(input_video)
    
    cf.dC.resize_config(VideoSource.new_size[0], VideoSource.new_size[1])

    print("Source: {}".format(name_source))
    
    if cf.RENDER_VIDEO:
        output_video = cv2.VideoWriter(cf.OUTPUT_VIDEO(name_source), cv2.cv.CV_FOURCC(*'MJPG'), 20, (int(VideoSource.new_size[0]), int(VideoSource.new_size[1])))


    #background substraction tools
    fgbg = ForgroundExtraction(cf.ALGO, VideoSource.new_size)

    #liste of persons detected
    persons = []
    backup_dead_persons = []

    groups = []

    if cf.USE_SENDING_THREAD:
        #init thread in charge of sending data to the api endpoint
        sendingDataThread = SendDataThread()

        #start the thread which sends the data
        sendingDataThread.start()
    else:
        print "Data sending thread desactivated"    


    timer = []

    #initialise the zones object
    zones_detection = Zones(input_video, VideoSource.new_size, mode='detection')
    zones_io = Zones(input_video, VideoSource.new_size, mode='io')
    zones_portal = Zones(input_video, VideoSource.new_size, mode='portal')

    cv2.namedWindow('Tracking', cv2.WINDOW_NORMAL)	
    cv2.resizeWindow('Tracking', int(VideoSource.new_size[0]), int(VideoSource.new_size[1])+48)

    logo_file = cv2.imread(cf.LOGO_FILE)
    init_file = cv2.imread(cf.INIT_FILE)

    #main loop
    print("Start training background detection")

    cf.T_START = time.time()

    player = "play"

    frames = []
    current_displayed_frame = 0

    while (True):

        key = cv2.waitKey(1)
        #if key != -1:
         #   print key
           
        if current_displayed_frame > cf.PLAYBACK_LENGTH:
            frames[current_displayed_frame - cf.PLAYBACK_LENGTH] = 0

        if key != -1:

            #touche q ou esc
            if (key == ord('q')) | (key == 27):
                player = "stop"
                print("Exiting...")
                break   
            
            #barre espace
            elif key == 32:
                if player=="play":
                    player = "pause"
                elif player == "pause":
                    player="play"
                else:
                    player = "play"

            #fleche droite
            elif key == 2555904:
                player = "next_frame"

            #fleche gauche
            elif key == 2424832:
                if (VideoSource.nb_frame - current_displayed_frame) < (cf.PLAYBACK_LENGTH-2):
                    player = "previous_frame"
                else:
                    print "End of recorded playback"
                    player = "pause"


            print "{} {}".format(VideoSource.nb_frame, player.title())
        
        if player == "previous_frame":
            current_displayed_frame = current_displayed_frame - 1
            if cf.SHOW_FG:
                cv2.imshow('Forground detection',frames[current_displayed_frame-1][2])
            cv2.imshow("Tracking", frames[current_displayed_frame-1][1])
            player = "pause"
            

        if (player == "play") | (player == "next_frame"):
            if player == "next_frame":
                player = "pause"

            if current_displayed_frame < VideoSource.nb_frame:
                if cf.SHOW_FG:
                    cv2.imshow('Forground detection',frames[current_displayed_frame-1][2])
                cv2.imshow("Tracking", frames[current_displayed_frame-1][1])
                current_displayed_frame += 1
                time.sleep(0.02)
            else:

                t = {}
                t['frame'] = time.time()
                t['frame_number'] = VideoSource.nb_frame
                t['alive'] = len(persons)
                t['backup'] = len(backup_dead_persons)

                t['next_frame'] = time.time()

                #new frame acquisition
                ret,frame = VideoSource.next_frame()

                t['a_next_frame'] = time.time()


                #break at the end of the video 
                if not ret:
                    print('End of video')
                    break

                #break on key press

        
                '''
                '
                '   PROCESSING
                '
                '''  
                t['processing'] = time.time()

                t['foreground'] = time.time()
                #Foreground extraction
                forground = fgbg.update(frame, VideoSource.nb_frame)
                t['a_foreground'] = time.time()
        
                #prepare the frame to be displayed
                t['draw_annotation'] = time.time()
                #frame_annotation = print_annotation(frame, VideoSource, persons, backup_dead_persons, zones)
                frame_annotation = frame
                t['a_draw_annotation'] = time.time()

                #wait TRAIN_FRAMES frames to train the background
                if (VideoSource.nb_frame >= cf.TRAIN_FRAMES):
    
                    if (VideoSource.nb_frame == cf.TRAIN_FRAMES):
                        print("Training over")
                        print("Start Detection")


                    t['check_for_deaths'] = time.time()
                    tl.check_for_deaths(zones_detection, zones_io, persons, groups, VideoSource.new_size, VideoSource.nb_frame, backup_dead_persons)
                    t['a_check_for_deaths'] = time.time()


                    #detect contours on the extracted foreground
                    temp_recherche_contour = copy(forground)

                    t['find_contours'] = time.time()
                    contours,hierarchy = cv2.findContours(temp_recherche_contour, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                    t['a_find_contours'] = time.time()

                    #init liste that contains the probable persons detected on the frame
                    temp_persons_detected_on_current_frame = []
            
                    #if some contours were actually detected on the frame, we process them
                    if len(contours) > 0:

                        #only keep the bigger contours (for noise removal)
                        #contours = [cv2.convexHull(c) for c in contours if cv2.contourArea(c) > cf.dC.cnt_min]
                        contours = [c for c in contours if cv2.contourArea(c) > cf.dC.cnt_min]
   
                        #if there are still some contours big enough present on the frame
                        if len(contours) > 0:

                            contours.sort(tl.compare_contour_aera)

                            #try to detect groups on contours that could be persons on the frame
                            previous_len_cnt = 0                    
                            while len(contours) > 0 & previous_len_cnt < len(contours):
                                t['search_persons_on_frame'] = time.time()
                                res, l = tl.search_person_on_frame(contours)
                                t['a_search_persons_on_frame'] = time.time()

                                if (res == True):
                                    temp_persons_detected_on_current_frame.append(l)
                                previous_len_cnt = len(contours)

                            if (len(temp_persons_detected_on_current_frame) > 0) & (len(temp_persons_detected_on_current_frame)-len(persons) < 20):
                        

                                #when possible persons are identified on the frame, try to track them, ie associate these persons with the ones already registered
                                t['update_persons'] = time.time()
                                tl.update_persons_with_groups(persons, VideoSource.nb_frame, temp_persons_detected_on_current_frame, VideoSource, groups, t)
                                t['a_update_persons'] = time.time()


                                t['update_zones'] = time.time()
                                tl.update_persons_zones(persons, VideoSource.nb_frame, zones_detection)
                                t['a_update_zones'] = time.time()


                                '''
                                t['disappear'] = time.time()
                                diseppeared = [] 
                                #tl.search_for_diseppeared_persons(persons, VideoSource)
                                #print("disepeared {}".format(len(diseppeared)))
                                t['a_disappear'] = time.time()

                                t['add_new_zones'] = time.time()
                                if len(diseppeared) > 0:
                                    for p in diseppeared:
                                        zones_detection.add_new_zone(p[0], p[1])
                                t['a_add_new_zones'] = time.time()
                                '''

                                t['update_groups'] = time.time()
                                tl.update_groups(VideoSource, persons, groups)
                                t['a_update_groups'] = time.time()

                    #tl.export_positives(VideoSource, persons)
                    #tl.export_negatives(VideoSource, persons)
                t['a_processing'] = time.time()



                '''
                '
                '   DRAWING     
                '
                '''
                t['drawing'] = time.time()

                if (VideoSource.nb_frame >= cf.TRAIN_FRAMES):
                    if VideoSource.nb_frame % cf.DISPLAYED_FRAME == 0:
                        #draw general information
                        #frame_annotation_copy = frame_annotation.copy()
                        t['draw_general'] = time.time()
                        if cf.DRAW_CONFIG:
                            draw_config(VideoSource, frame_annotation, zones_detection)
                        t['a_draw_general'] = time.time()

                        #draw detection zone on the frame
                        t['draw_zones'] = time.time()
                        if cf.DRAW_ZONES_IO:
                            draw_zones(zones_io, frame_annotation)
                        if cf.DRAW_ZONES_DETECTION:
                            draw_zones(zones_detection, frame_annotation)
                        if cf.DRAW_ZONES_PORTAL:
                            draw_zones(zones_portal, frame_annotation)
                        t['a_draw_zones'] = time.time()

                        #draw the detected persons on the frame
                        t['draw_persons'] = time.time()
                        if cf.DRAW_PERSONS:
                            draw_persons(persons, VideoSource, frame_annotation, frame_annotation)
                        t['a_draw_persons'] = time.time()

                        if cf.DRAW_GROUPS:
                            draw_groups(groups, VideoSource, frame)
 

                else:
                    draw_init_frame(VideoSource, frame_annotation, init_file)

                t['a_drawing'] = time.time()

                if cf.RENDER_VIDEO & (VideoSource.nb_frame > cf.TRAIN_FRAMES):
                    output_video.write(frame_annotation)
        
                if VideoSource.nb_frame % cf.DISPLAYED_FRAME == 0:
                    border = generate_border(VideoSource, logo_file, persons, backup_dead_persons, zones_detection)
                    frame_annotation = assemble_frame_border(frame_annotation, border)

                    #display the frame
            
                    forground = cv2.resize(forground, (int(forground.shape[1]/2), int(forground.shape[0]/2)))

                    if cf.SHOW_FG:
                        cv2.imshow('Forground detection',forground)

                    t['imshow'] = time.time()
                    cv2.imshow('Tracking',frame_annotation)
                    t['a_imshow'] = time.time()

                t['a_frame'] = time.time()
                frames.append((VideoSource.nb_frame, frame_annotation, forground))
                current_displayed_frame = VideoSource.nb_frame
                timer.append(t)



    t_end = time.time()

    print("Killing {} alive current items".format(len(persons)))
    for i,p in enumerate(persons):
        print("{} {} {} dies    {} age {}".format(VideoSource.nb_frame, tl.time(), p.puuid, p.last_zone(), p.age))
        tl.kill(zones_detection, persons, groups, i, p, VideoSource.nb_frame, backup_dead_persons)

    #process and display heat map
    if cf.DRAW_HEAT_MAP:
        print("Processing heat map...")
        t_heat_map = time.time()
        heatmap = tl.heatMap(persons, VideoSource)   
        t_a_heat_map = time.time()
        cv2.imwrite('heatmap.png', heatmap)
        print('Heat map done')

        cv2.imshow("Heat map", heatmap)
        while True:
            if 27 == cv2.waitKey(1):
                break   

    if cf.EXPORT_HEATMAPJS_DATA:
        print("Exporting heatmapJS data...")
        t_heatmapjs_data = time.time()
        tl.heatMapJS(persons, VideoSource)
        t_a_heatmapjs_data = time.time()
        print("Export heatmapJS data done")
        #draw avg frame
        cv2.imwrite('avg.png', VideoSource.avg_frame)

    if cf.USE_SENDING_THREAD:
        #clean stop the thread sending the data
        sendingDataThread.stop()
        sendingDataThread.join()
        print("Thread stopped")

    #release the camera and eventually the output video file
    VideoSource.release()
    if cf.RENDER_VIDEO:
        output_video.release()



    #close all windows properly
    cv2.destroyAllWindows()


    print("--------------------------")
    print("Summary")
    #data = {'persons':[]}

    print("{} Frames".format(VideoSource.nb_frame))
    print("{} s".format(round(t_end - cf.T_START, 2)))
    print("{} AVG FPS".format(float(VideoSource.nb_frame)/(t_end-cf.T_START)))
    print("{} ms/frame".format(round(((t_end-cf.T_START)*1000)/float(VideoSource.nb_frame), 2)))
    print("--------------------------")

    print("Persons")
    print("{} persons detected".format(len(persons)+len(backup_dead_persons)))
    print("{} backuped".format(len(backup_dead_persons)))

    
    print("--------------------------")
    print("Zones")
    print("{} detection zones".format(len(zones_detection.masks)))
    for m in zones_detection.masks:
        print("{} in {} out {}".format(m[0].title(), zones_detection.count["entries"][m[0]], zones_detection.count["exits"][m[0]]))

    
    print("--------------------------")
    
    print("Performances")

    perf = open("log.js", "w")
    perf_line = []
    perf_line.append("log=[")

    tot = {}
    tot['frame'] = 0
    tot['processing'] = 0
    tot['drawing'] = 0
    tot['next_frame'] = 0
    tot['foreground'] = 0
    tot['draw_annotation'] = 0
    tot['check_for_deaths'] = 0
    tot['find_contours'] = 0
    tot['search_persons_on_frame'] = 0
    tot['update_persons'] = 0
    tot['update_zones'] = 0
    tot['draw_general'] = 0
    tot['draw_zones'] = 0
    tot['draw_persons'] = 0
    tot['imshow'] = 0
    tot['disappear'] = 0
    tot['add_new_zones'] = 0
    tot['update_groups'] = 0
    

    tot['UP_first'] = 0
    tot['UP_second'] = 0
    tot['UP_third'] = 0
    tot['UP_fourth'] = 0



    for i,t in enumerate(timer):

        t_frame = 0
        t_next_frame = 0
        t_foreground = 0
        t_check_deaths = 0
        t_find_contours = 0
        t_search_persons_on_frame = 0
        t_update_persons = 0

        
        if 'frame' in t:
            t_frame = t['a_frame'] - t['frame']
            tot['frame'] += t_frame 

        if 'processing' in t:
            tot['processing'] += t['a_processing'] - t['processing']

        if 'drawing' in t:
            tot['drawing'] += t['a_drawing'] - t['drawing']

        if 'next_frame' in t:
            t_next_frame = t['a_next_frame'] - t['next_frame']
            tot['next_frame'] += t_next_frame

        if 'foreground' in t:
            t_foreground = t['a_foreground'] - t['foreground']
            tot['foreground'] += t_foreground

        if 'draw_annotation' in t:
            tot['draw_annotation'] += t['a_draw_annotation'] - t['draw_annotation']

        if 'check_for_deaths' in t:
            t_check_deaths = t['a_check_for_deaths'] - t['check_for_deaths']
            tot['check_for_deaths'] += t['a_check_for_deaths'] - t['check_for_deaths']

        if 'find_contours' in t:
            t_find_contours = t['a_find_contours'] - t['find_contours']
            tot['find_contours'] += t_find_contours

        if 'search_persons_on_frame' in t:
            t_search_persons_on_frame = t['a_search_persons_on_frame'] - t['search_persons_on_frame']
            tot['search_persons_on_frame'] += t['a_search_persons_on_frame'] - t['search_persons_on_frame']

        if 'update_persons' in t:
            t_update_persons = t['a_update_persons'] - t['update_persons']
            tot['update_persons'] += t['a_update_persons'] - t['update_persons']

        if 'update_zones' in t:
            tot['update_zones'] += t['a_update_zones'] - t['update_zones']

        if 'draw_general' in t:
            tot['draw_general'] += t['a_draw_general'] - t['draw_general']

        if 'draw_zones' in t:
            tot['draw_zones'] += t['a_draw_zones'] - t['draw_zones']

        if 'draw_persons' in t:
            tot['draw_persons'] += t['a_draw_persons'] - t['draw_persons']

        if 'imshow' in t:
            tot['imshow'] += t['a_imshow'] - t['imshow']

        if 'disappear' in t:
            tot['disappear'] += t['a_disappear'] - t['disappear']

        if 'add_new_zones' in t:
            tot['add_new_zones'] += t['a_add_new_zones'] - t['add_new_zones']

        if 'update_groups' in t:
            tot['update_groups'] += t['a_update_groups'] - t['update_groups']





        if 'UP_first_loop' in t:
            tot['UP_first'] += t['a_UP_first_loop'] - t['UP_first_loop']

        if 'UP_second_loop' in t:
            tot['UP_second'] += t['a_UP_second_loop'] - t['UP_second_loop']

        if 'UP_third_loop' in t:
            tot['UP_third'] += t['a_UP_third_loop'] - t['UP_third_loop']

        if 'UP_fourth_loop' in t:
            tot['UP_fourth'] += t['a_UP_fourth_loop'] - t['UP_fourth_loop']


        if cf.PERF_STATS:
            if i==len(timer):
                perf_line.append("[{},{},{},{},{},{},{},{},{},{}]".format(t['frame_number'], t['alive'], t['backup'],t_frame,t_next_frame,t_foreground,t_check_deaths,t_find_contours,t_search_persons_on_frame,t_update_persons))
            else:
                perf_line.append("[{},{},{},{},{},{},{},{},{},{}],".format(t['frame_number'], t['alive'], t['backup'],t_frame,t_next_frame,t_foreground,t_check_deaths,t_find_contours,t_search_persons_on_frame,t_update_persons))


    if cf.PERF_STATS:
        perf_line.append("]")
        for l in perf_line:
            perf.write(l)
        perf.close()
        
    '''
    for t in tot:
        print('{}: {}ms'.format(t, (float(tot[t])/VideoSource.nb_frame)*1000))
    '''
    tl.print_perf(tot, 'frame', VideoSource.nb_frame)
    print " "
    tl.print_perf(tot, 'processing', VideoSource.nb_frame)
    tl.print_perf(tot, 'next_frame', VideoSource.nb_frame)
    tl.print_perf(tot, 'foreground', VideoSource.nb_frame)
    tl.print_perf(tot, 'check_for_deaths', VideoSource.nb_frame)
    tl.print_perf(tot, 'find_contours', VideoSource.nb_frame)
    tl.print_perf(tot, 'search_persons_on_frame', VideoSource.nb_frame)
    tl.print_perf(tot, 'update_persons', VideoSource.nb_frame)

    tl.print_perf(tot, 'UP_first', VideoSource.nb_frame)
    tl.print_perf(tot, 'UP_second', VideoSource.nb_frame)
    tl.print_perf(tot, 'UP_third', VideoSource.nb_frame)
    tl.print_perf(tot, 'UP_fourth', VideoSource.nb_frame)

    tl.print_perf(tot, 'update_zones', VideoSource.nb_frame)
    tl.print_perf(tot, 'update_groups', VideoSource.nb_frame)

    print " "
    tl.print_perf(tot, 'drawing', VideoSource.nb_frame)
    tl.print_perf(tot, 'draw_general', VideoSource.nb_frame)
    tl.print_perf(tot, 'draw_zones', VideoSource.nb_frame)
    tl.print_perf(tot, 'draw_persons', VideoSource.nb_frame)

    

    if cf.DRAW_HEAT_MAP:
        print("heat_map: {}ms".format(t_a_heat_map-t_heat_map))

    if cf.EXPORT_HEATMAPJS_DATA:
        print("heatmapJS_data: {}ms".format(t_a_heatmapjs_data - t_heatmapjs_data))
    
    print("--------------------------")

    return 0

if __name__ == "__main__":
    #main()
    profile.run('main()')