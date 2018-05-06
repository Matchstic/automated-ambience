from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import namedtuple
from threading import Thread

GLOBAL_EMULATED_MANAGER = None
SERVER_PORT = 12345

class EmulatedMQTTManagerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

    def do_HEAD(self):
        self.send_response(200)
        
    def do_POST(self):
        global GLOBAL_EMULATED_MANAGER
        
        self.send_response(200)
        
        # Get POST'd data, and forward as needed.
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        GLOBAL_EMULATED_MANAGER.on_data(post_data)
        
    def log_message(self, format, *args):
        return

# Effectively, a local server that listens on localhost for incoming data.
# This avoids the need for a working MQTT connection when running in emulator mode.
class EmulatedMQTTManager():
    def __init__(self, mqtt_manager):
        global GLOBAL_EMULATED_MANAGER
        self._ignore_incoming = False
        self._mqtt_manager = mqtt_manager
        
        self._struct_tuple = namedtuple('EmulatedMessage', 'topic payload')
        
        GLOBAL_EMULATED_MANAGER = self
        
        # Start the server thread
        server_thread = Thread(target=self.server_thread)
        server_thread.daemon = True
        server_thread.start()
        
    def server_thread(self):
        global SERVER_PORT
        
        server_address = ('', SERVER_PORT)
        httpd = HTTPServer(server_address, EmulatedMQTTManagerHandler)
        
        try:
            print("[INFO] Starting emulated MQTT broker on port " + str(SERVER_PORT) + "...")
            httpd.serve_forever()
        except:
            httpd.server_close()
        
    def on_mqtt_connected(self):
        # Now that the MQTT manager is working, we no longer require this server to be running.
        self._ignore_incoming = True
        
        # TODO: Shutdown self?
        
    def on_data(self, data):
        if self._ignore_incoming == True:
            return
        
        # Parse the topic, and JSON string from the incoming data.
        # Each data part is separated by a newline (\n)
        
        topic = data.splitlines()[0]
        data_str = data.splitlines()[1]

        self._mqtt_manager.on_message(None, None, self._struct_tuple(topic=topic, payload=data_str))