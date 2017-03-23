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
import time
import os
from multiprocessing import Process, TimeoutError



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
    '''
    cv2.line(frame_annotation, (4, int(VideoSource.new_size[1])), (4, int(VideoSource.new_size[1])-cf.MIN_PERS_SIZE_Y),  (0,0,255),1)
    cv2.line(frame_annotation, (8, int(VideoSource.new_size[1])), (8, int(VideoSource.new_size[1])-cf.MAX_PERS_SIZE_Y), (0,255,0),1)
    cv2.line(frame_annotation, (12, int(VideoSource.new_size[1])), (12, int(VideoSource.new_size[1])-cf.MAX_DIST_CENTER_Y), (255,0,0), 1)

    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-4), (cf.MIN_PERS_SIZE_X, int(VideoSource.new_size[1])-4), (0,0,255),1)
    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-8), (cf.MAX_PERS_SIZE_X, int(VideoSource.new_size[1])-8), (0,255,0),1)
    cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-12), (cf.MAX_DIST_CENTER_X, int(VideoSource.new_size[1])-12), (255,0,0), 1)
    '''
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

def draw_persons(persons, VideoSource, frame_annotation, frame_annotation_copy):
            
    #check among the persons we have registered, which are currently on the frame so we can draw informations about them
    
    persons_to_draw = [p for p in persons if p.exists_at_last_frame(VideoSource.nb_frame) & p.alive]
    if len(persons_to_draw) > 0:
                                                
        #draw bbox, contours and position on the frame for each person
        for per in persons_to_draw:
                    
            #draw the contours we have of that person on that frame
            cv2.drawContours(frame_annotation, per.contour_last_frame(VideoSource.nb_frame), -1, per.couleur_dark, 1, cv2.CV_AA)
            
            overlay = frame_annotation.copy()
            cv2.drawContours(overlay, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, -1)
            cv2.addWeighted(overlay, cf.ALPHA, frame_annotation_copy, 1 - cf.ALPHA, 0, frame_annotation)
            cv2.drawContours(frame_annotation, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, 1, cv2.CV_AA)
            
            #obtain current person's bounding box in order to draw on the displayed frame
            (x,y,w,h) = per.bbox_last_frame(VideoSource.nb_frame)
            cv2.rectangle(frame_annotation,(x, y),(x+w, y+h),per.couleur,2)
                            
            #draw current person's position on the frame
            cv2.circle(frame_annotation, per.position_last_frame(VideoSource.nb_frame), 3, per.couleur, -1, cv2.CV_AA)
            

            if cf.DRAW_PERSON_PATH_TAIL:
                previous_pos = (0,0)
            
                for i,p in enumerate(per.liste_positions[-cf.DRAW_PERSON_PATH_TAIL_LENGTH:]):
                    if (i>0):
                        cv2.line(frame_annotation, previous_pos, p[0], per.couleur, 2, cv2.CV_AA)
                    previous_pos = p[0]
               
def generate_border(VideoSource, logo,  persons, backup, zones, name_source):
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
    lines.append(("Frame {}/{}".format(str(VideoSource.nb_frame), str(int(VideoSource.nb_total_frame))), cf.BORDER_TEXT_COLOR))
    lines.append(("FPS "+str(round(VideoSource.nb_frame/(time.time()-cf.T_START),2)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} alive".format(len(persons)), cf.BORDER_TEXT_COLOR))
    lines.append(("{} dead".format(len(backup)), cf.BORDER_TEXT_COLOR))

    for z in zones.masks:
        lines.append(("{}: {} items".format(z[3], zones.count["entries"][z[0]] - zones.count["exits"][z[0]]), z[2][1]))

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
    raw_input("Press enter to begin...")
               

    #cv2.setUseOptimized(True)
    print("Start time {}".format(tl.time()))
    
    #initialisation
    
    #video source
    args = parse.parser()

    if args.input:
        if args.input == "0":
            input_video = 0
        elif args.input == "1":
            input_video = 1
        else:
            input_video = args.input

    else:
        input_video = cf.VIDEO_SOURCE



    if(input_video==0)|(input_video==1):
        name_source = "Webcam"
    else:
        name_source = os.path.basename(input_video).split('.')[0]

    VideoSource = Source(input_video)
    
    print("Source: {}".format(name_source))
    
    #cf.apply_config_set(cf.ACTIVE_CONFIG_SET, VideoSource.new_size)
    #print("Applying {} detection config".format(cf.ACTIVE_CONFIG_SET))


    if cf.RENDER_VIDEO:
        output_video = cv2.VideoWriter(cf.OUTPUT_VIDEO(name_source), cv2.cv.CV_FOURCC(*'MJPG'), 20, (int(VideoSource.new_size[0]), int(VideoSource.new_size[1])))


    #background substraction tools
    fgbg = ForgroundExtraction(cf.ALGO, VideoSource.new_size)

    #liste of persons detected
    persons = []
    backup_dead_persons = []

    #init thread in charge of sending data to the api endpoint
    sendingDataThread = SendDataThread()

    #start the thread which sends the data
    sendingDataThread.start()
    
    timer = []

    #initialise the zones object
    zones = Zones(input_video, VideoSource.new_size)

    cv2.namedWindow('Tracking', cv2.WINDOW_NORMAL)	
    cv2.resizeWindow('Tracking', int(VideoSource.new_size[0]), int(VideoSource.new_size[1])+48)

    logo_file = cv2.imread(cf.LOGO_FILE)
    init_file = cv2.imread(cf.INIT_FILE)

    #main loop
    print("Start training background detection")

    while (True):

        t = {}

        t['next_frame'] = time.time()

        #new frame acquisition
        ret,frame = VideoSource.next_frame()

        t['a_next_frame'] = time.time()


        #break at the end of the video 
        if not ret:
            print('End of video')
            break

        #break on key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break   


        
        '''
        '
        '   PROCESSING
        '
        '''  
        
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
            tl.check_for_deaths(zones, persons, VideoSource.new_size, VideoSource.nb_frame, backup_dead_persons)
            t['a_check_for_deaths'] = time.time()


            #detect contours on the extracted foreground
            temp_recherche_contour = copy(forground)

            t['find_contours'] = time.time()
            contours,hierarchy = cv2.findContours( temp_recherche_contour, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            t['a_find_contours'] = time.time()

            #init liste that contains the probable persons detected on the frame
            temp_persons_detected_on_current_frame = []
            
            #if some contours were actually detected on the frame, we process them
            if len(contours) > 0:

                #simplify the geometry of the contours to lesser memory and compute operations impact
                #cnt_approx = []
                '''
                epsilon = 0.01*cv2.arcLength(c,True)
                approx = cv2.approxPolyDP(c,epsilon,True)
                cnt_approx.append(approx)    
                
                cnt_approx.append(c)
                
                nbapprox = len(c)
                '''

                cnt_approx = contours



                #only keep the bigger contours (for noise removal)
                contours = [c for c in cnt_approx if cv2.contourArea(c) > cf.dC.cnt_min()]

                
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

                    if (len(temp_persons_detected_on_current_frame)>0)&(len(temp_persons_detected_on_current_frame)<30):
                        

                        #when possible persons are identified on the frame, try to track them, ie associate these persons with the ones already registered
                        t['update_persons'] = time.time()
                        tl.update_persons(persons, VideoSource.nb_frame, temp_persons_detected_on_current_frame)
                        t['a_update_persons'] = time.time()


                        t['update_zones'] = time.time()
                        tl.update_persons_zones(persons, VideoSource.nb_frame, zones)
                        t['a_update_zones'] = time.time()				
                    
        
            '''
            '
            '   DRAWING
            '
            '''
            if VideoSource.nb_frame % cf.DISPLAYED_FRAME == 0:
	            #draw general information
	            #frame_annotation_copy = frame_annotation.copy()
	            t['draw_general'] = time.time()
	            if cf.DRAW_CONFIG:
	                draw_config(VideoSource, frame_annotation, zones)
	            t['a_draw_general'] = time.time()

	            #draw detection zone on the frame
	            t['draw_zones'] = time.time()
	            if cf.DRAW_ZONES:
	                draw_zones(zones, frame_annotation)
	            t['a_draw_zones'] = time.time()

	            #draw the detected persons on the frame
	            t['draw_persons'] = time.time()
	            if cf.DRAW_PERSONS:
	                draw_persons(persons, VideoSource, frame_annotation, frame_annotation)
	            t['a_draw_persons'] = time.time()


        else:
            draw_init_frame(VideoSource, frame_annotation, init_file)

        if cf.RENDER_VIDEO:
            output_video.write(frame_annotation)
        
        if VideoSource.nb_frame % cf.DISPLAYED_FRAME == 0:
	        border = generate_border(VideoSource, logo_file, persons, backup_dead_persons, zones, name_source)
	        frame_annotation = assemble_frame_border(frame_annotation, border)

	        #display the frame
	        
	        #cv2.imshow('Forground detection',forground)

	        t['imshow'] = time.time()
	        cv2.imshow('Tracking',frame_annotation)
	        t['a_imshow'] = time.time()

        timer.append(t)         

    t_end = time.time()

    print("Killing {} alive current items".format(len(persons)))
    for i,p in enumerate(persons):
        print("{} {} {} dies    {} age {}".format(VideoSource.nb_frame, tl.time(), p.puuid, p.last_zone(), p.age))
        tl.kill(zones, persons, i, p, VideoSource.nb_frame, backup_dead_persons)

    #process and display heat map
    if cf.DRAW_HEAT_MAP:
        print("Processing heat map")
        t_heat_map = time.time()
        heatmap = tl.heatMap(persons, VideoSource)   
        t_a_heat_map = time.time()
        cv2.imwrite('heatmap.png', heatmap)
        while True:
            cv2.imshow("Heat map", heatmap)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break   

    

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
    print("{} AVG FPS".format(float(VideoSource.nb_frame)/(time.time()-cf.T_START)))
    print("{} ms/frame".format(round(((time.time()-cf.T_START)*1000)/float(VideoSource.nb_frame), 2)))
    print("--------------------------")

    print("Persons")
    print("{} persons detected".format(len(persons)+len(backup_dead_persons)))
    print("{} backuped".format(len(backup_dead_persons)))
    '''
    for p in backup_dead_persons:
        print("{} age {}".format(p.uuid, p.age))
    '''
    
    #for p in persons:
    '''
    temp = {}
    temp['id'] = str(p.uuid)
    temp['positions'] = str(len(p.liste_positions))
    data.get('persons').append(temp)
    '''
    #print(str(p.uuid)+ ": "+ str(len(p.liste_positions)) +" positions detected")
    #print("{} age {}".format(p.uuid, p.age))
    
    print("--------------------------")
    print("Zones")
    
    for m in zones.masks:
        print("{} in {} out {}".format(m[0].title(), zones.count["entries"][m[0]], zones.count["exits"][m[0]]))

    
    
    print("--------------------------")
    
    print("Performances")


    tot = {}
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

    for t in timer:


        if 'next_frame' in t:
            tot['next_frame'] += t['a_next_frame'] - t['next_frame']

        if 'foreground' in t:
            tot['foreground'] += (t['a_foreground'] - t['foreground'])

        if 'draw_annotation' in t:
            tot['draw_annotation'] += t['a_draw_annotation'] - t['draw_annotation']

        if 'check_for_deaths' in t:
            tot['check_for_deaths'] += t['a_check_for_deaths'] - t['check_for_deaths']

        if 'find_contours' in t:
            tot['find_contours'] += t['a_find_contours'] - t['find_contours']

        if 'search_persons_on_frame' in t:
            tot['search_persons_on_frame'] += t['a_search_persons_on_frame'] - t['search_persons_on_frame']

        if 'update_persons' in t:
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

    for t in tot:
        #t = float(t)/float(VideoSource.nb_frame)
        print('{}: {}ms'.format(t, (float(tot[t])/VideoSource.nb_frame)*1000))

    if cf.DRAW_HEAT_MAP:
        print("heat_map: {}ms".format(t_a_heat_map-t_heat_map))
    
    print("--------------------------")
    
    

    '''
    nb_contours_tot = {'contours':0, 'approx':0}
    for n in  nb_contours:
        nb_contours_tot['contours'] += n['contours']
        nb_contours_tot['approx'] += n['approx']

    
    print("--------------------------")
    print("Contours: {}".format(nb_contours_tot['contours'])) 
    print("--------------------------")
    '''

    #print json.dumps(data)


    return 0

if __name__ == "__main__":
    main()
