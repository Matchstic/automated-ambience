#!/usr/bin/python

from audio.AudioManager import AudioManager
from display.DisplayManager import DisplayManager
from data.SubsumptionArbiter import SubsumptionArbiter
from data.MQTTManager import MQTTManager

def main():
    # Initialise the manager instances
    display_manager = DisplayManager()
    audio_manager = AudioManager(display_manager.is_emulated())
    subsumption_arbiter = SubsumptionArbiter(display_manager, audio_manager)
    mqtt_manager = MQTTManager(subsumption_arbiter.on_mqtt_message)
    
    # Start the subsumption architecture.
    subsumption_arbiter.setup_tasks()
    subsumption_arbiter.start_threads()
    
    # Start the Bluetooth Low Energy broadcast if possible
    try:
        from bluetooth.BluetoothLowEnergyBroadcast import BluetoothLowEnergyBroadcast
        
        bluetooth_broadcast = BluetoothLowEnergyBroadcast()
        
        # Request the audio manager to begin waiting on the Bluetooth speaker (or a short busy wait if emulated)
        # We provide the bluetooth broadcast as a callback, since advertisement must start AFTER speaker connection
        audio_manager.setup(bluetooth_broadcast)
    except:
        print ("[WARN] Not starting Bluetooth Low Energy advertisement")  
        
        # Request the audio manager to begin waiting on the Bluetooth speaker (or a short busy wait if emulated)
        audio_manager.setup(None)
    
    # Connect to the MQTT broker
    mqtt_manager.connect(display_manager.is_emulated())
    
    # Finally, start the display and its main loop!
    display_manager.setup_display()
    
    # Cleanup connection to the MQTT broker
    mqtt_manager.disconnect()

if __name__ == "__main__":
    main()