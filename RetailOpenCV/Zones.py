import os
import cv2
import numpy as np
import config as cf
import tools as tl

'''

zone image files names are expected to look like:
[videofilename]_[zonename].png

'''

class Zones(object):
	"""description of class"""

	def __init__(self, video_path, video_dim):
		
		if (video_path != 0)&(video_path != 1):
			video_file = os.path.basename(video_path).split('.')[0]

			if cf.DIR_ZONES == "":
				video_dir = os.path.dirname(video_path)
			else:   
				video_dir = cf.DIR_ZONES

		else:
			video_file = str(video_path)
			if cf.DIR_ZONES == "":
				video_dir = ""
			else:   
				video_dir = cf.DIR_ZONES

		self.masks = []

		self.count = {"entries":{}, "exits":{}}

		print("Zone 1 Neutral")
		if (video_dir != ""):
			zone_id = 2
			for file in os.listdir(video_dir):
				

				if file.startswith(video_file):

					if len(file.split('_')) == 2:

						zone_name = file.split('_')[1].split(".")[0].title()
						img = cv2.imread(os.path.join(video_dir, file))

						img_height, img_width, channels = img.shape
						vid_width, vid_height = video_dim

						if (img_height != vid_height)|(img_height != vid_width):
							img = cv2.resize(img, (int(video_dim[0]), int(video_dim[1])), interpolation=cv2.INTER_CUBIC)

						img_bw = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

						ret, img_bw = cv2.threshold(img_bw, 0, 255, cv2.THRESH_BINARY);


						contours,hierarchy = cv2.findContours(img_bw, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
						#couleur = tl.random_color_zones()
						couleur = tl.random_color()
						#(name of the zone, liste of contours defining the zone, color of the zone on the frame)
						self.masks.append((zone_name, contours, couleur, zone_id))
						
						self.count["entries"][zone_name] = 0
						self.count["exits"][zone_name] = 0
						print("Zone {} {}".format(zone_id, zone_name))
						zone_id += 1

	def nb_zones(self):
		return len(self.masks)


	def in_zones(self, position):
		for m in self.masks:
			for cnt in m[1]:
				if (cv2.pointPolygonTest(cnt, position, False)==True):
					return m[0], m[3]
		#Neutral zone has ID 1
		return 1, 1


	def inc_in(self, zone_name):
		self.count["entries"][zone_name] += 1
		


	def inc_out(self, zone_name):
		self.count["exits"][zone_name] += 1