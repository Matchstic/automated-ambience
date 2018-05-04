from threading import Thread
import time

class BaseTask():
    def __init__(self, display_manager, audio_manager):
        self.display_manager = display_manager
        self.audio_manager = audio_manager
        self.is_outputting = False
        
    ####################################################
    # Overrides
    ####################################################
    
    def wants_subsumption(self):
        return False
        
    def on_task_update(self):
        pass
        
    def on_mqtt_message(self, topic, message):
        pass
        
    ####################################################
    # Protected methods - Display
    ####################################################
        
    def set_is_outputting(self, outputting):
        self.is_outputting = outputting
        
    def display_set_pixel(self, x, y, r, g, b):
        if self.is_outputting is False:
            return 
            
        self.display_manager.set_pixel(x, y, r, g, b)
        
    def display_set_brightness(self, brightness):
        if self.is_outputting is False:
            return
            
        self.display_manager.set_brightness(brightness)
    
    def display_show(self):        
        if self.is_outputting is False:
            return
        
        self.display_manager.show()
        
    ####################################################
    # Protected methods - Audio
    ####################################################
    
    def audio_request_playlist(self, playlist):
        if self.is_outputting is False:
            return
        
        self.audio_manager.request_playlist(playlist)
    
    ####################################################
    # Private methods - Threading
    ####################################################
        
    def _task_thread(self):
        while True:
            self.on_task_update()
            time.sleep(0.02)
        
    def start_task_thread(self):
        task_thread = Thread(target=self._task_thread)
        task_thread.daemon = True
        task_thread.start()