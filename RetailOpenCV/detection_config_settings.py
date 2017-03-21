import config as cf

class DetectionConfig(object):
    def __init__(self, setConfig = None):
        self.activeConfigSet = {}
        
        self.configs = {}

        self.configs['chute'] = {
                'CNT_MIN': 30,
                'MIN_SIZE_CNT_PERS': 30,
                'MAX_DIST_CENTER_X': 160,
                'MAX_DIST_CENTER_Y': 210,
                'MAX_PERS_SIZE_X': 280, 
                'MAX_PERS_SIZE_Y': 340,
                'MIN_PERS_SIZE_X': 30,
                'MIN_PERS_SIZE_Y': 50 
            }
        self.configs['lego'] = {
                'CNT_MIN': 10,
                'MIN_SIZE_CNT_PERS': 10,
                'MAX_DIST_CENTER_X': 80,
                'MAX_DIST_CENTER_Y': 80,
                'MAX_PERS_SIZE_X': 170, 
                'MAX_PERS_SIZE_Y': 170,
                'MIN_PERS_SIZE_X': 25,
                'MIN_PERS_SIZE_Y': 25 
            }

        self.configs['livefeed'] = {
                'CNT_MIN': 5,
                'MIN_SIZE_CNT_PERS': 5,
                'MAX_DIST_CENTER_X': 50,
                'MAX_DIST_CENTER_Y': 50,
                'MAX_PERS_SIZE_X': 300, 
                'MAX_PERS_SIZE_Y': 200,
                'MIN_PERS_SIZE_X': 5,
                'MIN_PERS_SIZE_Y': 5
            }

        self.configs['street'] = {
                'CNT_MIN': 5,
                'MIN_SIZE_CNT_PERS': 10,
                'MAX_DIST_CENTER_X': 60,
                'MAX_DIST_CENTER_Y': 30,
                'MAX_PERS_SIZE_X': 220, 
                'MAX_PERS_SIZE_Y': 150,
                'MIN_PERS_SIZE_X': 5,
                'MIN_PERS_SIZE_Y': 10
            }

        if setConfig != None:
            if self.configs[setConfig]:
                for key in self.configs[setConfig]:
                    self.activeConfigSet[key] = self.configs[setConfig][key]

    
    def cnt_min(self):
        return int(self.activeConfigSet['CNT_MIN'])

    def min_size_cnt_pers(self):
        return int(self.activeConfigSet["MIN_SIZE_CNT_PERS"])

    def max_dist_center_x(self):
        return int(self.activeConfigSet['MAX_DIST_CENTER_X'])
    
    def max_dist_center_y(self):
        return int(self.activeConfigSet['MAX_DIST_CENTER_Y'])
    
    def max_pers_size_x(self):
        return int(self.activeConfigSet['MAX_PERS_SIZE_X'])

    def max_pers_size_y(self):
        return int(self.activeConfigSet['MAX_PERS_SIZE_Y'])

    def min_pers_size_x(self):
        return int(self.activeConfigSet['MIN_PERS_SIZE_X'])

    def min_pers_size_y(self):    
        return int(self.activeConfigSet['MIN_PERS_SIZE_X'])




