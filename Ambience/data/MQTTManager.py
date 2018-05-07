import paho.mqtt.client as mqtt
from threading import Thread
import json
import time

from EmulatedMQTTManager import EmulatedMQTTManager

MQTT_SERVER = "m14.cloudmqtt.com"
MQTT_PORT = 15466
MQTT_USERNAME = "rpi-client"
MQTT_PASSWORD = "raspberrymrt"
MQTT_TOPICS = ["data", "prefs"]

class MQTTManager():
    def __init__(self, callback):
        
        # Create MQTT client and assign callbacks
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log
        
        self.callback = callback
        
        # We need an emulated server for when running in emulated mode.
        self.emulated_server = EmulatedMQTTManager(self)
        
    def connect(self, is_emulated):
        global MQTT_TOPICS, MQTT_PASSWORD, MQTT_USERNAME, MQTT_PORT, MQTT_SERVER
         
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
        # Start the connection thread
        connection_thread = Thread(target=self.connection_thread, args=(is_emulated,))
        connection_thread.daemon = True
        connection_thread.start()
        
    def event_thread(self):
        try:
            self.client.loop_forever()
        except:
            pass
        
    def connection_thread(self, is_emulated):
        print("[INFO] Connecting to MQTT broker on port " + str(MQTT_PORT) + "...")
        try:
            if is_emulated is False:
                print ("[DEBUG] Waiting for network connectivity")
                time.sleep(10)
                
            self.client.connect(MQTT_SERVER, MQTT_PORT)
            
            # Start the event loop
            event_thread = Thread(target=self.event_thread)
            event_thread.daemon = True
            event_thread.start()
        except:
            self.client.disconnect()
        
    def disconnect(self):
        self.client.disconnect()
        
    def unjsonify(self, jsonstr):
        return json.loads(jsonstr)
    
    # MQTT event callbacks
    def on_connect(self, client, userdata, flags, rc):
        global MQTT_SERVER, MQTT_PORT
        if rc == 0:
            print("[INFO] Connected to MQTT broker on " + MQTT_SERVER + ":" + str(MQTT_PORT))
            self.emulated_server.on_mqtt_connected()
            
            # Subscribe to topics now...
            for topic in MQTT_TOPICS:
                print("[INFO] Subscribing to MQTT topic: " + topic)
                self.client.subscribe(topic, 2)
        else:
            print("[WARN] on_connect :: rc: " + str(rc))

    def on_message(self, client, obj, msg):
        topic = msg.topic
        message = self.unjsonify(msg.payload)
        
        self.callback(topic, message)

    def on_subscribe(self, client, obj, mid, granted_qos):
        pass

    def on_log(self, client, obj, level, string):
        pass
        
    