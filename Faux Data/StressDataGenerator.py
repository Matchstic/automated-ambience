from BaseDataGenerator import BaseDataGenerator
import time

class StressDataGenerator(BaseDataGenerator):
    def __init__(self, mqtt_manager):
        BaseDataGenerator.__init__(self, mqtt_manager)
        
        self.lastBPM = 0
        self.lastBPMTimestamp = 0
        self.lastHRV = 0
        self.lastHRVTimestamp = 0
        
    def name(self):
        return "High Stress Generator"
        
    def generate_new_data(self):
        self.lastBPM = 75
        self.lastBPMTimestamp = int(time.time())
        self.lastHRV = 25
        self.lastHRVTimestamp = int(time.time())
        
        self.publish(self.to_dict(), "data")
        
    def to_dict(self):
        return dict(
            bpm = self.lastBPM,
            bpmTimestamp = self.lastBPMTimestamp,
            hrv = self.lastHRV,
            hrvTimestamp = self.lastHRVTimestamp,
            basestation_visible = True
        )