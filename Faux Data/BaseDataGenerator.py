import json

class BaseDataGenerator():
    def __init__(self, mqtt_manager):
        self.mqtt_manager = mqtt_manager
        
    def name(self):
        return "Base Generator"
        
    def generate_new_data(self):
        pass
        
    def publish(self, dictionary, topic):
        self.mqtt_manager.publish_message(self.jsonify(dictionary), topic)
        
    def jsonify(self, dictionary):
        return json.dumps(dictionary)