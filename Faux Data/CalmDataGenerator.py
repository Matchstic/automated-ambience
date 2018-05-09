from BaseDataGenerator import BaseDataGenerator

class CalmDataGenerator(BaseDataGenerator):
    def __init__(self, mqtt_manager):
        BaseDataGenerator.__init__(self, mqtt_manager)
        
    def configure_min_max_values(self):
        self.max_bpm = 55
        self.min_bpm = 45
        
        self.max_hrv = 105
        self.min_hrv = 85
        
    def name(self):
        return "Low Stress Generator"