from BaseTask import BaseTask

class DisconnectionTask(BaseTask):
    def __init__(self, display_manager, audio_manager):
        BaseTask.__init__(self, display_manager, audio_manager)
        
        self.user_basestation_visible = True
        
    def wants_subsumption(self):
        return not self.user_basestation_visible and self.audio_manager.has_connected_speaker()
        
    def on_task_update(self):
        # Ensure the LEDs are fully off when the user is no longer in Bluetooth visibility
        for x in range(8):
            for y in range(4):
                self.display_set_pixel(x, y, 0, 0, 0)
                
        self.display_show()
        
        # Audio output
        self.audio_request_playlist(self.audio_manager.PLAYLIST_NONE)
        
    def on_mqtt_message(self, topic, message):
        # We monitor the basestation_visible flag of incoming messages
        if topic == "data":
            self.user_basestation_visible = message["basestation_visible"]