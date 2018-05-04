from BaseTask import BaseTask
from StressDetector import StressDetector

import math, time

STRESS_TRIGGER_THRESHOLD = 0.43

class StressReductionTask(BaseTask):
    def __init__(self, display_manager, audio_manager):
        BaseTask.__init__(self, display_manager, audio_manager)
        
        self.stress_level = 0.0
        self.stress_detector = StressDetector()
        self.override_stress_threshold = False
        
        self.biofeedback_enabled = False
        self.current_bpm = 0
        
    def wants_subsumption(self):
        global STRESS_TRIGGER_THRESHOLD
        
        threshold_reached = self.override_stress_threshold is 1 or self.stress_level >= STRESS_TRIGGER_THRESHOLD
        return self.audio_manager.has_connected_speaker() and threshold_reached
        
    def on_task_update(self):
        # Just go red!
        for x in range(8):
            for y in range(4):
                self.display_set_pixel(x, y, 255, 10, 10)
                
        self.display_show()
        
        # Audio output
        self.audio_request_playlist(self.audio_manager.PLAYLIST_DE_STRESS)
        
        # Handle biofeedback output
        if self.wants_subsumption() is True and self.biofeedback_enabled is 1 and self.current_bpm is not 0:
            # Get the current UNIX timestamp
            timestamp_now = time.time()
            
            beats_per_second = self.current_bpm / 60.0
            
            # Use the sin() function with some adjustments to produce a continuous set of values
            # from 0.5 to 1.0 for brightness.
            brightness = (math.sin(2*math.pi * timestamp_now * beats_per_second) + 1.0) / 4.0
            brightness += 0.5
            
            self.display_manager.set_brightness(brightness)
        else:
            # Just stay at 100% brightness
            self.display_manager.set_brightness(1.0)
        
    def on_mqtt_message(self, topic, message):
        if topic == "data":
            # We monitor the following message flags: bpm, bpmTimestamp, hrv, hrvTimestamp
            # Pass data into the "stress detector" algorithm, and update our stress level value.
            
            bpm = message["bpm"]
            bpmTimestamp = message["bpmTimestamp"]
            hrv = message["hrv"]
            hrvTimestamp = message["hrvTimestamp"]
            
            self.stress_level = self.stress_detector.generate_stress_level(bpm, hrv, bpmTimestamp, hrvTimestamp)
            self.current_bpm = bpm
            
            print("[INFO] Stress level: " + str(self.stress_level) + ", BPM: " + str(bpm) + ", HRV: " + str(hrv))
        elif topic == "prefs":
            try:
                self.biofeedback_enabled = message["heartFeedback"]
                self.override_stress_threshold = message["overrideStressThreshold"]
                
                averageBPM = message["averageBPM"]
                averageHRV = message["averageHRV"]
            
                self.stress_detector.configure_baselines(averageBPM, averageHRV)
            
                print("[INFO] heartFeedback: " + str(self.biofeedback_enabled) + ", averageBPM: " + str(averageBPM) + ", averageHRV: " + str(averageHRV) + ", overrideStressThreshold: " + str(self.override_stress_threshold))
            except:
                print("[ERROR] ??")
                pass