import paho.mqtt.client as mqtt
from threading import Thread
import requests

MQTT_SERVER = "m14.cloudmqtt.com"
MQTT_PORT = 15466
MQTT_USERNAME = "watch-client"
MQTT_PASSWORD = "raspberrymrt"
MQTT_TOPICS = ["data", "prefs"]

class MQTTManager():
    def __init__(self):
        # Create MQTT client and assign callbacks
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        
        self.is_connected = False
        
    def connect(self):
        global MQTT_TOPICS, MQTT_PASSWORD, MQTT_USERNAME, MQTT_PORT, MQTT_SERVER
         
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # Start the connection thread
        connection_thread = Thread(target=self.connection_thread)
        connection_thread.daemon = True
        connection_thread.start()
            
    def connection_thread(self):
        print("[INFO] Connecting to MQTT broker on port " + str(MQTT_PORT) + "...")
        print("[INFO] Connecting to emulated MQTT broker on port " + str(12345) + "...")
        try:
            self.client.connect(MQTT_SERVER, MQTT_PORT)
        except:
            self.client.disconnect()
        
    def publish_message(self, message, topic):
        if self.is_connected is True:
            self.client.publish(topic, message, qos=2)
            
        # We also publish to the local HTTP server, if available
        server_address = "http://localhost"
        server_port = 12345
        
        try:
            requests.post(server_address + ":" + str(server_port), data=topic + "\n" + message)
        except:
            pass
        
    # MQTT event callbacks
    def on_connect(self, client, userdata, flags, rc):
        global MQTT_SERVER, MQTT_PORT
        if rc == 0:
            print("Connected to MQTT broker on " + MQTT_SERVER + ":" + str(MQTT_PORT))
            self.is_connected = True
        else:
            print("on_connect :: rc: " + str(rc))
        
    def on_publish(self, client, obj, mid):
        pass

    def on_log(self, client, obj, level, string):
        pass