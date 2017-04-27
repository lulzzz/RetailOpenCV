import config as cf

class DetectionConfig(object):
    def __init__(self, setConfig = None):
        self.activeConfigSet = {}
        
        self.configs = {}

        self.configs['chute'] = {
                'width': 720,
                'height': 480,
                'CNT_MIN': 30,
                'MIN_SIZE_CNT_PERS': 30,
                'MAX_DIST_CENTER_X': 160,
                'MAX_DIST_CENTER_Y': 210,
                'MAX_PERS_SIZE_X': 280, 
                'MAX_PERS_SIZE_Y': 340,
                'MIN_PERS_SIZE_X': 30,
                'MIN_PERS_SIZE_Y': 50 
            }

        self.configs['chuteLab'] = {
                'width': 720,
                'height': 480,
                'CNT_MIN': 30,
                'MIN_SIZE_CNT_PERS': 30,
                'MAX_DIST_CENTER_X': 250,
                'MAX_DIST_CENTER_Y': 200,
                'MAX_PERS_SIZE_X': 350,  
                'MAX_PERS_SIZE_Y': 280,
                'MIN_PERS_SIZE_X': 15,
                'MIN_PERS_SIZE_Y': 20 
            }

        self.configs['lego'] = {
                'width': 960,
                'height': 540,
                'CNT_MIN': 10,
                'MIN_SIZE_CNT_PERS': 10,
                'MAX_DIST_CENTER_X': 80,
                'MAX_DIST_CENTER_Y': 80,
                'MAX_PERS_SIZE_X': 170, 
                'MAX_PERS_SIZE_Y': 170,
                'MIN_PERS_SIZE_X': 25,
                'MIN_PERS_SIZE_Y': 25 
            }
        
        self.configs['lego1080'] = {
                'width': 1920,
                'height': 1080,
                'CNT_MIN': 20,
                'MIN_SIZE_CNT_PERS': 20,
                'MAX_DIST_CENTER_X': 160,
                'MAX_DIST_CENTER_Y': 160,
                'MAX_PERS_SIZE_X': 340, 
                'MAX_PERS_SIZE_Y': 340,
                'MIN_PERS_SIZE_X': 50,
                'MIN_PERS_SIZE_Y': 50 
            }

        self.configs['livefeed'] = {
                'width': 960,
                'height': 540,
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
                'width': 960,
                'height': 540,
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

    def resize_config(self, width, height):
        size_ratio = float(width) / float(self.activeConfigSet['width'])
        area_ratio = size_ratio ** 2

        for key in self.activeConfigSet:
            self.activeConfigSet[key] = int(self.activeConfigSet[key] * size_ratio)

    @property
    def cnt_min(self):
        return int(self.activeConfigSet['CNT_MIN'])

    @property
    def min_size_cnt_pers(self):
        return int(self.activeConfigSet["MIN_SIZE_CNT_PERS"])

    @property
    def max_dist_center_x(self):
        return int(self.activeConfigSet['MAX_DIST_CENTER_X'])
    
    @property
    def max_dist_center_y(self):
        return int(self.activeConfigSet['MAX_DIST_CENTER_Y'])
    
    @property
    def max_pers_size_x(self):
        return int(self.activeConfigSet['MAX_PERS_SIZE_X'])

    @property
    def max_pers_size_y(self):
        return int(self.activeConfigSet['MAX_PERS_SIZE_Y'])

    @property
    def min_pers_size_x(self):
        return int(self.activeConfigSet['MIN_PERS_SIZE_X'])

    @property
    def min_pers_size_y(self):    
        return int(self.activeConfigSet['MIN_PERS_SIZE_Y'])




