from MQTTManager import MQTTManager
from StressDataGenerator import StressDataGenerator
import time
from threading import Thread

CURRENT_GENERATOR = None
DATA_GENERATORS = []

def data_generator_thread():
    while True:
        if CURRENT_GENERATOR is not None:
            # Request new data to be generated
            CURRENT_GENERATOR.generate_new_data()
            
            # Pause for two seconds
            time.sleep(2)
        else:
            time.sleep(0.05)

def user_input_thread():
    pass

def main():
    global DATA_GENERATORS, CURRENT_GENERATOR
    
    mqtt_manager = MQTTManager()
    
    DATA_GENERATORS.append(StressDataGenerator(mqtt_manager))
    CURRENT_GENERATOR = DATA_GENERATORS[0]
    
    data_gen_thread = Thread(target=data_generator_thread)
    data_gen_thread.daemon = True
    data_gen_thread.start()
    
    # Start up MQTT connection!
    mqtt_manager.connect()

if __name__ == "__main__":
    main()