import numpy as np
import cv2
import config as cf
import tools as tl
import random
import uuid
import time
import Person


class Group(object):
    """description of class"""

    def __init__(self, person):

        self.list_persons = []
        self.list_persons.append(person)
        self.id = str(uuid.uuid4())
        self.tot_none_zeros = 1
        self.tot_post_prob = 1


    def add_person(self, person):
        if not self.is_in_group(person):
            self.list_persons.append(person)
            person.in_group = self.id


    def remove_person(self, person):
        for i,p in enumerate(self.list_persons):
            if p.uuid == person.uuid:
                self.list_persons.pop(i)
                p.in_group = "0"
                break

    def is_in_group(self, person):
        for i,p in enumerate(self.list_persons):
            if p.uuid == person.uuid:
                return True
        return False

    def bbox(self):
        return tl.bbox(self.list_persons[0].last_bbox())

    def calculate_hist_data(self):
        
        tot_none_zeros = 0
        liste_area = []
        for pei, pe in enumerate(self.list_persons):
            A = sum([cv2.contourArea(c) for c in pe.data[-1][1]])
            tot_none_zeros += A
            liste_area.append(A)

        tot_post_prob = 0
        for pei, pe in enumerate(self.list_persons):
            #Ap = cv2.countNonZero(pe.mask)
            P = float(liste_area[pei])/tot_none_zeros
            Px = pe.hist/liste_area[pei]
            tot_post_prob += P*Px

        self.tot_none_zeros = tot_none_zeros
        self.tot_post_prob = tot_post_prob

    def print_group(self):
        res = "group {}: ".format(self.id)
        for pi, p in enumerate(self.list_persons):
            res += p.puuid
            if pi != len(self.list_persons)-1:
                res+= ", "
        return res