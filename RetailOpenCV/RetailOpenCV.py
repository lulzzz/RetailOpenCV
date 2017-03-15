# -*- coding: utf-8 -*-
#Main file 

import numpy as np
import cv2
import config as cf
import tools as tl
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


#input_video = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\chutes\\chute10\\cam2.avi"

input_video = "C:\\Users\\Olivier-Laforge\\Documents\\DatasetRetail\\footage\\Street2960.mp4"


#input_video = "C:\\Users\\Olivier Staub\\Documents\\ComputerVision_Detect_Body\\videoset\\chute16\\cam2.avi"

#input_video = 1

#input_video="C:\\Users\\Olivier Staub\\Pictures\\Camera Roll\\WIN_20170314_17_59_20_Pro.mp4"

#input_video = "C:\\Users\\Olivier Staub\\Documents\\footage\\ex1.mp4"
#input_video = "C:\\Users\\Olivier Staub\\Documents\\footage\\cafet.MOV"
#input_video = "C:\\Users\\Olivier Staub\\Documents\\footage\\cafet2.mp4"
#input_video = "C:\\Users\\Olivier Staub\\Documents\\footage\\foot1.mp4"

#input_video = "C:\\Users\\Olivier Staub\\Documents\\ComputerVision_Detect_Body\\videoset\\chutes_fablab\\chute15.MP4"



#input_video="C:\\Users\\Olivier\\Documents\\retail\\footage\\cafet2.mp4"
#input_video="C:\\Users\\Olivier\\Documents\\retail\\footage\\cafet.mov"


#input_video="C:\\Users\\Olivier\\Documents\\retail\\chute\\23\\cam2.avi"
#input_video="C:\\Users\\Olivier\\Documents\\retail\\chute\\02\\cam2.avi"
#input_video="C:\\Users\\Olivier\\Documents\\retail\\chute\\14\\cam3.avi"



#input_video = "/Users/Olivier/GitHub/Retail/chute/01/cam8.avi"
#input_video = "/Users/Olivier/GitHub/Retail/footage/cafet2.mp4"



class SendDataThread(threading.Thread):
	def __init__(self): 
		threading.Thread.__init__(self)
		self._stop = threading.Event()
		print("Thread initialized")

	def run(self):
		while not self.stopped():
			time.sleep(1)
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
			
			data = {}
			data['data'] = []
			data['camera_id'] = cf.CAMERA_ID
			

			for p in cf.to_be_sent:
				temp = {}
				temp['person'] = p[0]
				temp['exits'] = p[1]
				temp['enters'] = p[2]
				temp['timestamp'] = p[3]
				data['data'].append(temp)

			#print(json.dumps(data))
			
			tl.post_results(data)
			#print("{} items sent".format(len(cf.to_be_sent)))
			cf.to_be_sent = []
			#API POST
			'''
			if (post_results(data))
				cf.to_be_sent = []
			else:
				print('An error occured while sendind the data')
			'''
			
	   

def draw_general_infos(VideoSource, frame_annotation, zones):
	#show config distance and size at the bottom of the frame
	'''
	cv2.line(frame_annotation, (4, int(VideoSource.new_size[1])), (4, int(VideoSource.new_size[1])-cf.MIN_PERS_SIZE_Y),  (0,0,255),2)
	cv2.line(frame_annotation, (8, int(VideoSource.new_size[1])), (8, int(VideoSource.new_size[1])-cf.MAX_PERS_SIZE_Y), (0,255,0),2)
	cv2.line(frame_annotation, (12, int(VideoSource.new_size[1])), (12, int(VideoSource.new_size[1])-cf.MAX_DIST_CENTER_Y), (255,0,0), 2)

	cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-4), (cf.MIN_PERS_SIZE_X, int(VideoSource.new_size[1])-4), (0,0,255),2)
	cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-8), (cf.MAX_PERS_SIZE_X, int(VideoSource.new_size[1])-8), (0,255,0),2)
	cv2.line(frame_annotation, (0,int(VideoSource.new_size[1])-12), (cf.MAX_DIST_CENTER_X, int(VideoSource.new_size[1])-12), (255,0,0), 2)
	'''    
	 
	#recording dot
	cv2.circle(frame_annotation, (int(VideoSource.new_size[0])-16, 15), 6, (0,255,0), -1)

	#dead zones
	'''
	cv2.line(frame_annotation, ( cf.DEAD_ZONE_X, 0), (cf.DEAD_ZONE_X, int(VideoSource.new_size[1])), (255,255, 0), 1)
	cv2.line(frame_annotation, ( int(VideoSource.new_size[0]) - cf.DEAD_ZONE_X, 0), ( int(VideoSource.new_size[0]) - cf.DEAD_ZONE_X, int(VideoSource.new_size[1])), (255,255, 0), 1)
	cv2.line(frame_annotation, (0, cf.DEAD_ZONE_Y), (int(VideoSource.new_size[0]), cf.DEAD_ZONE_Y), (255, 255, 0), 1)
	cv2.line(frame_annotation, (0, int(VideoSource.new_size[1]) - cf.DEAD_ZONE_Y), (int(VideoSource.new_size[0]), int(VideoSource.new_size[1]) - cf.DEAD_ZONE_Y), (255, 255, 0), 1)
	'''


def draw_zones(zones, frame_annotation):
	if zones.nb_zones() > 0:
		overlay = frame_annotation.copy()
		for m in zones.masks:
			cv2.drawContours(overlay, m[1], 0, m[2][1], -1)
			(x, y, w, h) = tl.bbox(m[1])                    
			section_overlay = overlay[y:y+h, x:x+w] 
			section_frame_annotation = frame_annotation[y:y+h, x:x+w]
			cv2.addWeighted(section_overlay, 0.15, section_frame_annotation, 1 - 0.15, 0, section_frame_annotation)
			frame_annotation[y:y+h, x:x+w] = section_frame_annotation
			cv2.drawContours(frame_annotation, m[1], 0, m[2][1], 2)


def draw_persons(persons, VideoSource, frame_annotation, frame_annotation_copy):
			
	#check among the persons we have registered, which are currently on the frame so we can draw informations about them
	
	persons_to_draw = [p for p in persons if p.exists_at_last_frame(VideoSource.nb_frame) & p.alive]

	if len(persons_to_draw) > 0:
												
		#draw bbox, contours and position on the frame for each person
		for per in persons_to_draw:
					
			#draw the contours we have of that person on that frame
			cv2.drawContours(frame_annotation, per.contour_last_frame(VideoSource.nb_frame), -1, per.couleur_dark, 1)

			overlay = frame_annotation.copy()

			cv2.drawContours(overlay, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, -1)

			cv2.addWeighted(overlay, cf.ALPHA, frame_annotation_copy, 1 - cf.ALPHA, 0, frame_annotation)

			cv2.drawContours(frame_annotation, [per.contour_last_frame(VideoSource.nb_frame)[0]], 0, per.couleur_dark, 2)

			#obtain current person's bounding box in order to draw on the displayed frame
			(x,y,w,h) = per.bbox_last_frame(VideoSource.nb_frame)
			cv2.rectangle(frame_annotation,(x, y),(x+w, y+h),per.couleur,2)
							
			#draw current person's position on the frame
			cv2.circle(frame_annotation, per.position_last_frame(VideoSource.nb_frame), 4, per.couleur, -1)

			for p in per.liste_positions:
				cv2.circle(frame_annotation, p[0], 1, per.couleur, -1)

	persons_dead = [p for p in persons if not p.alive]

	if len(persons_dead) > 0:
		for per in persons_dead:
			cv2.drawContours(frame_annotation, per.contour_last_frame(VideoSource.nb_frame), -1, (255,255,255), 1)
		

def main():

	print("Start time {}".format(tl.time()))
	
	#initialisation
	
	#video source
	VideoSource = Source(input_video)

	if(input_video==0)|(input_video==1):
		print("Source: Webcam")
	else:
		print("Source: {}".format(os.path.basename(input_video)))

	camera = cv2.VideoCapture(input_video)
	#background substraction tools
	fgbg = ForgroundExtraction(cf.ALGO, VideoSource.new_size)

	#liste of persons detected
	persons = []

	#init thread in charge of sending data to the api endpoint
	sendingDataThread = SendDataThread()

	#start the thread which sends the data
	sendingDataThread.start()
	
	timer = []

	#initialise the zones object
	zones = Zones(input_video, VideoSource.new_size)

	#main loop
	while (True):

		#t = {}

		#t['start'] = time.time()

		#new frame acquisition
		ret,frame = VideoSource.next_frame()


		#break at the end of the video 
		if not ret:
			print('End of video')
			break

		#break on key press
		if cv2.waitKey(1) & 0xFF == ord('q'):
			print("Exiting...")
			break   


		
		#t['next_frame'] = time.time()

		'''
		'
		'   PROCESSING
		'
		'''  
		
		#Foreground extraction
		forground = fgbg.update(frame, VideoSource.nb_frame)

		#t['foreground'] = time.time()
		
		#prepare the frame to be displayed
		frame_annotation = VideoSource.frame_with_annotation()

		
		#['annotations'] = time.time()

		#wait TRAIN_FRAMES frames to train the background
		if (VideoSource.nb_frame > cf.TRAIN_FRAMES):


			tl.check_for_deaths(persons, VideoSource.new_size, VideoSource.nb_frame)

			#detect contours on the extracted foreground
			temp_recherche_contour = copy(forground)
			contours,hierarchy = cv2.findContours( temp_recherche_contour, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			
			#t['detect_contours'] = time.time()

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

				#t['contours_approx'] = time.time()


				#only keep the bigger contours (for noise removal)
				contours = [c for c in cnt_approx if cv2.contourArea(c)>cf.CNT_MIN]

				#t['contours_sort'] = time.time()

				#if there are still some contours big enough present on the frame
				if len(contours) > 0:

					contours.sort(tl.compare_contour_aera)

					#t['contours_size_sort'] = time.time()

					#try to detect groups on contours that could be persons on the frame
					previous_len_cnt = 0                    
					while (len(contours)>0) & previous_len_cnt < len(contours):
						res, l = (tl.search_person_on_frame(contours))
						if (res==1):
							temp_persons_detected_on_current_frame.append(l)
						previous_len_cnt = len(contours)

					#t['search_persons'] = time.time()

					#when possible persons are identified on the frame, try to track them, ie associate these persons with the ones already registered
					tl.update_persons(persons, VideoSource.nb_frame, temp_persons_detected_on_current_frame)

					#t['update_persons'] = time.time()


					tl.update_persons_zones(persons, VideoSource.nb_frame, zones)

					#t['update_zones'] = time.time()

					
					
		
			'''
			'
			'   DRAWING
			'
			'''       

			#draw general information
			#frame_annotation_copy = frame_annotation.copy()
			draw_general_infos(VideoSource, frame_annotation, zones)
			
			#draw detection zone on the frame
			draw_zones(zones, frame_annotation)

			#draw the detected persons on the frame
			draw_persons(persons, VideoSource, frame_annotation, frame_annotation)
						   
				#frame_annotation[x:y, x+w:y+h] = section_frame_annotation
						 
				#cv2.imshow('overlay', overlay)   

				

				#cv2.addWeighted(overlay, cf.ALPHA, frame_annotation, 1 - cf.ALPHA, 0, frame_annotation)
			#t['draw'] = time.time()




		#display the frame
		#cv2.imshow('Forground detection',forground)
		cv2.imshow('frameshow',frame_annotation)

		#print("FRAME "+str(VideoSource.nb_frame)+" "+str(round(VideoSource.nb_frame/(time.time()-cf.T_START)))+" FPS")  
		
		#timer.append(t)         

	t_end = time.time()

	#release the camera and close opencv windows
	VideoSource.release()
	cv2.destroyAllWindows()

	#clean stop the thread sending the data
	sendingDataThread.stop()
	sendingDataThread.join()
	print("Thread stopped")
	print("--------------------------")
	print("Summary")
	#data = {'persons':[]}



	print("{} Frames".format(VideoSource.nb_frame))
	print("{} s".format(round(t_end - cf.T_START, 2)))
	print("{} AVG FPS".format(float(VideoSource.nb_frame)/(time.time()-cf.T_START)))
	print("{} ms/frame".format(round(((time.time()-cf.T_START)*1000)/float(VideoSource.nb_frame), 2)))
	print("--------------------------")


	
	print("{} persons detected".format(len(persons)))
	for p in persons:
		'''
		temp = {}
		temp['id'] = str(p.uuid)
		temp['positions'] = str(len(p.liste_positions))
		data.get('persons').append(temp)
		'''
		#print(str(p.uuid)+ ": "+ str(len(p.liste_positions)) +" positions detected")
		print("{} age {}".format(p.uuid, p.age))
	
	print("--------------------------")
	print("Zones")
	
	for m in zones.masks:
		print("{}: {} entries, {} exists".format(m[0].title(), zones.count["entries"][m[0]], zones.count["exits"][m[0]]))

	
	
	print("--------------------------")

	

	

	'''
	tot = {}
	tot['next_frame'] = 0
	tot['foreground'] = 0
	tot['annotations'] = 0
	tot['detect_contours'] = 0
	tot['contours_approx'] = 0
	tot['contours_sort'] = 0
	tot['contours_size_sort'] = 0
	tot['search_persons'] = 0
	tot['update_persons'] = 0
	tot['update_zones'] = 0
	tot['draw'] = 0

	for t in timer:
		tot['next_frame'] += t['next_frame'] - t['start']
		tot['foreground'] += t['foreground'] - t['next_frame']
		tot['annotations'] += t['annotations'] - t['foreground']
		if 'detect_contours' in t:        
			tot['detect_contours'] += t['detect_contours'] - t['annotations']
			if 'contours_approx' in t:
				tot['contours_approx'] += t['contours_approx'] - t['detect_contours']
				if 'contours_sort' in t:
					tot['contours_sort'] += t['contours_sort'] - t['contours_approx']
					if 'contours_size_sort' in t:
						tot['contours_size_sort'] += t['contours_size_sort'] - t['contours_sort']
						if 'search_persons' in t:
							tot['search_persons'] += t['search_persons'] - t['contours_size_sort']
							if 'update_persons' in t:
								tot['update_persons'] += t['update_persons'] - t['search_persons']
								if 'update_zones' in t:
									tot['update_zones'] += t['update_zones'] - t['update_persons']
									if 'draw' in t:
										tot['draw'] += t['draw'] - t['update_zones']
		
	for t in tot:
		#t = float(t)/float(VideoSource.nb_frame)
		print('{}: {}ms'.format(t, (float(tot[t])/VideoSource.nb_frame)*1000))
	
	print("--------------------------")
	'''


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
