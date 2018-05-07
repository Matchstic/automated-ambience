import time
import signal, sys

IS_EMULATED = False

try:
    import unicornhat
except:
    IS_EMULATED = True
    from display.EmulatedDisplay import EmulatedDisplay
    
MAX_BRIGHTNESS = 1.0 if IS_EMULATED else 0.5

class DisplayManager():
    def __init__(self):
        global IS_EMULATED
        
        # Handle signals emitted by the underlying OS to clean up for exiting.
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGABRT, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGSEGV, self.handle_signal)
        
        if IS_EMULATED is False:
            self.display = unicornhat
        else:
            self.display = EmulatedDisplay()
            
        self.is_setup = False
        self.signalled_exit = False
        self.brightness = MAX_BRIGHTNESS
            
        # Set default brightness    
        self.set_brightness(1.0)
        
    def is_emulated(self):
        global IS_EMULATED
        return IS_EMULATED
        
    def handle_signal(self,signum, frame):
        self.signalled_exit = True
            
    #######################################################        
    # Forward requests through to the display in use
    ####################################################### 
    
    def setup_display(self):
        self.is_setup = True
        
        # Set the maximum brightness level
        self.display.brightness(MAX_BRIGHTNESS)
        
        if IS_EMULATED is False:
            self.display.set_layout(self.display.PHAT)
            self.display.rotation(0)
        else:
            self.display.setup()
        
        if IS_EMULATED is False:
            # Start a main GUI loop for the actual hardware so we don't just exit
            try:
                while True and not self.signalled_exit:
                    time.sleep(0.05)
            except KeyboardInterrupt:
                # End on a keyboard intterupt
                pass
                
            self.is_setup = False
            
            # Clear the display
            for x in range(8):
                for y in range(4):
                    self.display.set_pixel(x, y, 0, 0, 0)
                    
            sys.exit(0)
        
    
    def set_pixel(self, x, y, r, g, b):
        if self.is_setup is not True:
            return 
            
        # Adjust colour for brightness        
        r -= int(float(r) * (1.0-self.brightness))
        g -= int(float(g) * (1.0-self.brightness))
        b -= int(float(b) * (1.0-self.brightness))
        
        if r < 0: r = 0
        if g < 0: g = 0
        if b < 0: b = 0
            
        self.display.set_pixel(x, y, r, g, b)
        
    def set_brightness(self, brightness):
        global MAX_BRIGHTNESS
        
        if self.is_setup is not True:
            return
            
        self.brightness = brightness
            
        # Scale brightness from 1.0 -> 0.0 to MAX_BRIGHTNESS -> 0.0
        #normalised = brightness / MAX_BRIGHTNESS
        
        #if normalised > 1.0: normalised = 1.0
        #elif normalised < 0.0: normalised = 0.0
            
        #self.display.brightness(normalised)
        
    def show(self):
        if self.is_setup is not True:
            return
            
        self.display.show()