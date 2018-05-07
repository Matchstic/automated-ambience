from BaseTask import BaseTask
import datetime

class DaytimeAttentionTask(BaseTask):
    def __init__(self, display_manager, audio_manager):
        BaseTask.__init__(self, display_manager, audio_manager)
    
    def wants_subsumption(self):
        return self.audio_manager.has_connected_speaker()
        
    def on_task_update(self):
        red = self._get_red()
        green = self._get_green()
        
        for x in range(8):
            for y in range(4):
                self.display_set_pixel(x, y, int(red), int(green), 255)
                
        self.display_show()
        
        # Audio output
        self.audio_request_playlist(self.audio_manager.PLAYLIST_STUDY_AMBIENCE)
        
    def _get_green(self):
        # Green is maximum at midday, and at minimum at 7pm through to 5am
        # max is 100.
        
        current_hour = datetime.datetime.today().hour
        current_minute = datetime.datetime.today().minute
        if current_hour < 5 or current_hour > 19:
            return 0
        else:
            # Hour is between 5 and 19. Maximum is at 12.
            current_hour = current_hour - 5 # normalise to 0 -> 14.
            
            minutes = (60 * current_hour) + current_minute
            
            degree = float(minutes) / 420.0 # 420 mins == 7 hours
            if degree > 1.0: # Handle exceeding the halfway mark
                degree = 1.0 - (degree - 1.0)
                
            return 150.0 * degree
        
    def _get_red(self):
        # Red is at maximum at midnight, and at minimum from 7am through to 5pm
        # max is 100
        
        current_hour = datetime.datetime.today().hour
        current_minute = datetime.datetime.today().minute
        
        # Scale those hours before 7 to be "on the previous day" to handle time wrap-around
        if current_hour <= 7:
            current_hour = current_hour + 24
        
        if current_hour < 17:
            return 0
        else:
            # Hour is between 5 and 19. Maximum is at 12.
            current_hour = current_hour - 17 # normalise to 0 -> 14.
            
            minutes = (60 * current_hour) + current_minute
            
            degree = float(minutes) / 420.0
            if degree > 1.0:
                degree = 1.0 - (degree - 1.0)
                
            return 150.0 * degree
        