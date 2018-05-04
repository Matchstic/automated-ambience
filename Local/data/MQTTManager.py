import paho.mqtt.client as mqtt
from threading import Thread
import json

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
        
    def connect(self):
        global MQTT_TOPICS, MQTT_PASSWORD, MQTT_USERNAME, MQTT_PORT, MQTT_SERVER
         
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
        # Start the connection thread
        connection_thread = Thread(target=self.connection_thread)
        connection_thread.daemon = True
        connection_thread.start()
            
        # Start the event loop
        event_thread = Thread(target=self.event_thread)
        event_thread.daemon = True
        event_thread.start()
            
    def event_thread(self):
        self.client.loop_forever()
        
    def connection_thread(self):
        print("[INFO] Connecting to MQTT broker on port " + str(MQTT_PORT) + "...")
        print("[INFO] If no data is accessible, make sure this port is not blocked by a firewall.")
        try:
            self.client.connect(MQTT_SERVER, MQTT_PORT)
        except:
           print("[ERROR] Failed to connect. Is the broker up, or is port " + str(MQTT_PORT) + " blocked by a firewall?") 
        
    def disconnect(self):
        self.client.disconnect()
        
    def unjsonify(self, jsonstr):
        return json.loads(jsonstr)
        
    # MQTT event callbacks
    def on_connect(self, client, userdata, flags, rc):
        global MQTT_SERVER, MQTT_PORT
        if rc == 0:
            print("[INFO] Connected to MQTT broker on " + MQTT_SERVER + ":" + str(MQTT_PORT))
            
            # Subscribe to topics now...
            for topic in MQTT_TOPICS:
                print("[INFO] Subscribing to MQTT topic: " + topic)
                self.client.subscribe(topic, 0)
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
        
    