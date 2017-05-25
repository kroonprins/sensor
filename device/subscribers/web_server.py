""" Serve measurements via HTTP reading from sqlite database
"""

import signal
import json
import subprocess
import paho.mqtt.client as mqtt
from constants import MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_GPIO_BUTTON_1, \
                      WEB_SERVER_PROGRAM

class ServerProcess(object):
    """ Represents the server process that should be started
    """
    def __init__(self, program):
        self.program = program
        self._process = None

    def start(self):
        """ Start the server
        """
        if self._is_stopped:
            print "Starting web server"
            self._process = subprocess.Popen(['python', self.program])

    def stop(self):
        """ Stop the server
        """
        if not self._is_stopped():
            print "Stopping web server"
            self._process.terminate()
            self._process.wait()
            print "Stopped web server"

    def _is_stopped(self):
        if self._process is None:
            return True
        else:
            return self._process.poll() is not None

if __name__ == "__main__":

    def _start_web_server():
        SERVER_PROCESS.start()

    def _stop_web_server():
        SERVER_PROCESS.stop()

    def _on_connect(client, userdata, return_code):
        pass

    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        print msg.topic+" "+str(payload['status'])
        if payload['status'] is True:
            _start_web_server()
        else:
            _stop_web_server()

    def _on_disconnect(client, userdata, return_code):
        pass

    def _end_program(signum, frame):
        print "Exiting..."
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        exit(0)

    SERVER_PROCESS = ServerProcess(WEB_SERVER_PROGRAM)

    MQTT_CLIENT = mqtt.Client()
    MQTT_CLIENT.on_connect = _on_connect
    MQTT_CLIENT.on_message = _on_message
    MQTT_CLIENT.on_disconnect = _on_disconnect

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
    MQTT_CLIENT.subscribe(MQTT_TOPIC_GPIO_BUTTON_1, qos=1)
    MQTT_CLIENT.loop_forever()

