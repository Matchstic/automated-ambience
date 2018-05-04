import Queue
import time

# Constants
ROLLING_AVERAGE_COUNT = 5
BPM_HIGH_DEVIATION = 40
HRV_HIGH_DEVIATION = 35

class StressDetector():
    def __init__(self):
        
        self.previous_stress_levels = Queue.Queue()
        
        self.baseline_bpm = 72 # average bpm
        self.baseline_hrv = 60 # average ms
        
    def configure_baselines(self, bpm, hrv):
        self.baseline_bpm = bpm
        self.baseline_hrv = hrv
        
    def generate_stress_level(self, bpm, hrv, bpmTimestamp, hrvTimestamp):
        global ROLLING_AVERAGE_COUNT
        
        #####################################################################
        # 1. Find deviation of incoming BPM and HRV from a baseline value for 
        #    the user
        #####################################################################
        
        # XXX: A positive deviation equates to more stressed
    
        # BPM is higher when stressed
        bpm_deviation = bpm - self.baseline_bpm
        
        # HRV is lower when stressed
        hrv_deviation = self.baseline_hrv - hrv
        
        #####################################################################
        # 2. Modify the deviations by a confidence score, dependant on the age 
        #    of the incoming data.
        #####################################################################
        
        # Get the current UNIX timestamp
        timestamp_now = int(time.time())
        
        # The BPM must be within the last 15 seconds to be considered up-to-date.
        # An age of 5 minutes ago is treated as too old.                 y = -x/(300s - 15s) + 4/3
        bpm_confidence = 1.0 if timestamp_now - bpmTimestamp <= 15 else (0.0 - float(timestamp_now - bpmTimestamp) / 285.0) + 1.053
        if bpm_confidence < 0.0: bpm_confidence = 0.0
        
        # The HRV must be within the last 15 minutes to be considered up-to-date.
        # An age of 6 hours is treated as too old.                       y = -x/(6h in seconds - 15m in seconds) + 1.043
        hrv_confidence = 1.0 if timestamp_now - hrvTimestamp <= 900 else (0.0 - float(timestamp_now - hrvTimestamp) / 20700) + 1.043
        if hrv_confidence < 0.0: hrv_confidence = 0.0
        
        #####################################################################
        # 3. Compute stress levels from each data point with the confidence
        #    score and a normalised deviation
        #####################################################################
        
        normalised_bpm = self._normalise_bpm_deviation(bpm_deviation)
        normalised_hrv = self._normalise_hrv_deviation(hrv_deviation)
        
        stress_from_bpm = bpm_confidence * normalised_bpm
        stress_from_hrv = hrv_confidence * normalised_hrv
        
        #####################################################################
        # 4. Compute an ordered weighted average to fuse the stress levels
        #####################################################################
        
        # If HRV is at confidence 1.0, we utilise it over BPM due to its higher 
        # accuracy for stress detection.
        
        weights = [0.9, 0.1]
        
        stress_level = 0.0
        if bpm_confidence > hrv_confidence:
            stress_level = weights[0]*stress_from_bpm + weights[1]*stress_from_hrv
        else:
            stress_level = weights[1]*stress_from_bpm + weights[0]*stress_from_hrv
            
        #####################################################################
        # 5. Rolling average to smooth stress levels
        #####################################################################
        
        # Pop oldest level if needed
        if self.previous_stress_levels.qsize() >= ROLLING_AVERAGE_COUNT:
            self.previous_stress_levels.get()
        
        # Add new level
        self.previous_stress_levels.put(stress_level)
        
        average_queue_copy = []
        while True:
             try:
                 elem = self.previous_stress_levels.get(block=False)
             except:
                 break
             else:
                 average_queue_copy.append(elem)
        for elem in average_queue_copy:
            self.previous_stress_levels.put(elem)
        
        # Iterate over the queue's contents without removal
        averaged_stress_level = 0
        for level in average_queue_copy:
            averaged_stress_level += level
            
        # Take average
        averaged_stress_level /= self.previous_stress_levels.qsize()
        
        return averaged_stress_level
        
        
    def _normalise_bpm_deviation(self, bpm_deviation):
        # normalise between 0 and self.stressed_bpm - self.baseline_bpm
        max_value = BPM_HIGH_DEVIATION
        normalised = bpm_deviation / float(max_value)
        
        if normalised > 1.0: normalised = 1.0
        elif normalised < 0.0: normalised = 0.0
        
        return normalised
        
    def _normalise_hrv_deviation(self, hrv_deviation):
        max_value = HRV_HIGH_DEVIATION
        normalised = hrv_deviation / float(max_value)
        
        if normalised > 1.0: normalised = 1.0
        elif normalised < 0.0: normalised = 0.0
        
        return normalised
        
