from __future__ import print_function

from MQTTManager import MQTTManager
from StressDataGenerator import StressDataGenerator
from CalmDataGenerator import CalmDataGenerator

import time, sys, os, json
from threading import Thread

# From: https://gist.github.com/payne92/11090057
# If Windows getch() available, use that.  If not, use a
# Unix version.
try:
    import msvcrt
    getch = msvcrt.getch
except:
    import sys, tty, termios
    def _unix_getch():
        """Get a single character from stdin, Unix version"""

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())          # Raw read
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    getch = _unix_getch
    
# Globals
DATA_GENERATORS = []
CURRENT_GENERATOR = None
CURRENT_GENERATOR_INDEX = 0

CURRENT_BIOFEEDBACK_STATE = False
CURRENT_BASESTATION_STATE = True

MQTT_MANAGER = MQTTManager()

def data_generator_thread():
    global CURRENT_GENERATOR
    
    while True:
        if CURRENT_GENERATOR is not None:
            # Request new data to be generated
            CURRENT_GENERATOR.generate_new_data()
            
            # Pause for two seconds
            time.sleep(2)
        else:
            time.sleep(0.05)

def print_thread():
    global CURRENT_GENERATOR_INDEX, CURRENT_BIOFEEDBACK_STATE, CURRENT_BASESTATION_STATE
    
    while True: 
        # Clear screen
        
        output_type = str(CURRENT_GENERATOR_INDEX+1)
        biofeedback = "off" if CURRENT_BIOFEEDBACK_STATE == False else "on"
        basestation = "visible" if CURRENT_BASESTATION_STATE == True else "not visible"
        
        sys.stdout.write("BPM: " + str(CURRENT_GENERATOR.get_bpm()) + " count/min | HRV: " + str(CURRENT_GENERATOR.get_hrv()) + " ms | Output type: [" + str(CURRENT_GENERATOR_INDEX+1) + "] | Biofeedback: " + biofeedback + " | Basestation: " + basestation + "                    \r")
        sys.stdout.flush()
        
        time.sleep(0.001)
        
def handle_char(char):
    global DATA_GENERATORS, CURRENT_GENERATOR, CURRENT_GENERATOR_INDEX, CURRENT_BIOFEEDBACK_STATE, CURRENT_BASESTATION_STATE
    
    if char == '1':
        CURRENT_GENERATOR_INDEX = 0
        CURRENT_GENERATOR = DATA_GENERATORS[CURRENT_GENERATOR_INDEX]
    elif char == '2':
        CURRENT_GENERATOR_INDEX = 1
        CURRENT_GENERATOR = DATA_GENERATORS[CURRENT_GENERATOR_INDEX]
    elif char == '3':
        CURRENT_BIOFEEDBACK_STATE = not CURRENT_BIOFEEDBACK_STATE
        
        publish_settings()
    elif char == '4':
        CURRENT_BASESTATION_STATE = not CURRENT_BASESTATION_STATE
        
        for generator in DATA_GENERATORS:
            generator.set_basestation_visible(CURRENT_BASESTATION_STATE)
    elif char == '\x03':
        raise KeyboardInterrupt
    elif char == '\x04':
        raise EOFError
        
def publish_settings():
    global CURRENT_BIOFEEDBACK_STATE, CURRENT_BASESTATION_STATE, MQTT_MANAGER
    
    dictionary = dict(
        heartFeedback = 1 if CURRENT_BIOFEEDBACK_STATE == True else 0,
        overrideStressThreshold = 0,
        averageBPM = 55,
        averageHRV = 75
    )
    
    string = json.dumps(dictionary)
    
    MQTT_MANAGER.publish_message(string, "prefs")
    

def main():
    global DATA_GENERATORS, CURRENT_GENERATOR, CURRENT_GENERATOR_INDEX, MQTT_MANAGER
    
    DATA_GENERATORS.append(StressDataGenerator(MQTT_MANAGER))
    DATA_GENERATORS.append(CalmDataGenerator(MQTT_MANAGER))
    CURRENT_GENERATOR = DATA_GENERATORS[CURRENT_GENERATOR_INDEX]
    
    data_gen_thread = Thread(target=data_generator_thread)
    data_gen_thread.daemon = True
    data_gen_thread.start()
    
    # Start up MQTT connection!
    MQTT_MANAGER.connect()
    
    # Print user inputs
    print("\nData output type:\n[1] User stressed\n[2] User calm\n")
    print("Preferences:\n[3] Toggle biofeedback\n[4] Toggle base station visibility\n")
    
    # Start thread to write output to console
    printing_thread = Thread(target=print_thread)
    printing_thread.daemon = True
    printing_thread.start()
    
    # Publish settings
    publish_settings()
    
    # Read user input!
    while True:           
        try:     
            char = getch()
            handle_char(char)
        except KeyboardInterrupt:
            print("\n")
            break

if __name__ == "__main__":
    main()