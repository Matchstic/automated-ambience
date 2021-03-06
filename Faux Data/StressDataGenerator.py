from BaseDataGenerator import BaseDataGenerator

class StressDataGenerator(BaseDataGenerator):
    def __init__(self, mqtt_manager):
        BaseDataGenerator.__init__(self, mqtt_manager)
        
    def configure_min_max_values(self):
        self.max_bpm = 100
        self.min_bpm = 75
        
        self.max_hrv = 45
        self.min_hrv = 25
        
    def name(self):
        return "High Stress Generator"