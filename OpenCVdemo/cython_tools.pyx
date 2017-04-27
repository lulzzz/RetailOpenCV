from copy import copy
from Person import Person


def xmax(cnt):
	return tuple(cnt[cnt[:,:,0].argmax()][0])[0] 

def xmin(cnt):
	return tuple(cnt[cnt[:,:,0].argmin()][0])[0] 

def ymax(cnt):
	return tuple(cnt[cnt[:,:,1].argmax()][0])[1] 

def ymin(cnt):
	return tuple(cnt[cnt[:,:,1].argmin()][0])[1] 


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