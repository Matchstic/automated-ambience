import json
import random, time

class BaseDataGenerator():
    def __init__(self, mqtt_manager):
        self.mqtt_manager = mqtt_manager
        
        self.configure_min_max_values()
        
        self.lastBPM = self.min_bpm
        self.lastBPMTimestamp = 0
        self.lastHRV = self.max_hrv
        self.lastHRVTimestamp = 0
        
        self.basestation_visible = True
        
    def name(self):
        return "Base Generator"
        
    def configure_min_max_values(self):
        self.max_bpm = 75
        self.min_bpm = 55
        
        self.max_hrv = 105
        self.min_hrv = 85
        
    def set_basestation_visible(self, visible):
        self.basestation_visible = visible
        
    def get_hrv(self):
        return self.lastHRV
        
    def get_bpm(self):
        return self.lastBPM
        
    def generate_new_data(self):
        rand = random.randint(0,10)
        rand -= 5
        
        self.lastBPM = self.lastBPM + rand
        if self.lastBPM < self.min_bpm: self.lastBPM = self.min_bpm
        if self.lastBPM > self.max_bpm: self.lastBPM = self.max_bpm
        
        self.lastBPMTimestamp = int(time.time())
        
        
        self.lastHRV = self.lastHRV + rand
        if self.lastHRV < self.min_hrv: self.lastHRV = self.min_hrv
        if self.lastHRV > self.max_hrv: self.lastHRV = self.max_hrv
        self.lastHRVTimestamp = int(time.time())
        
        self.publish(self.to_dict(), "data")
        
    def to_dict(self):
        return dict(
            bpm = self.lastBPM,
            bpmTimestamp = self.lastBPMTimestamp,
            hrv = self.lastHRV,
            hrvTimestamp = self.lastHRVTimestamp,
            basestation_visible = self.basestation_visible
        )
        
    def publish(self, dictionary, topic):
        self.mqtt_manager.publish_message(self.jsonify(dictionary), topic)
        
    def jsonify(self, dictionary):
        return json.dumps(dictionary)