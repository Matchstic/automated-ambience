from BaseTask import BaseTask
import colorsys, time

class InitialisationTask(BaseTask):
    def __init__(self, display_manager, audio_manager):
        BaseTask.__init__(self, display_manager, audio_manager)
        
        self.spacing = 360.0 / 16.0
    
    def wants_subsumption(self):
        return True
    
    # This produces a fancy rainbow animation that runs continuously.
    # It is based upon the animation found at: https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-unicorn-phat
    def on_task_update(self):
        hue = int(time.time() * 100) % 360
        for x in range(8):
            offset = x * self.spacing
            h = ((hue + offset) % 360) / 360.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            for y in range(4):
                self.display_set_pixel(x, y, r, g, b)
                
        self.display_show()
        
        # Audio output
        self.audio_request_playlist(self.audio_manager.PLAYLIST_NONE)