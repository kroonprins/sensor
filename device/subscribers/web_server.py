""" Serve measurements via HTTP reading from sqlite database
"""

import json
import logging
import signal
import subprocess
import paho.mqtt.client as mqtt
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_GPIO_BUTTON_1, \
                      WEB_SERVER_PROGRAM

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('web_server_starter')

if __name__ == "__main__":

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
                LOGGER.debug("Starting web server - %s", self.program)
                self._process = subprocess.Popen(['python2', self.program])

        def stop(self):
            """ Stop the server
            """
            if not self._is_stopped():
                LOGGER.debug("Stopping web server")
                self._process.terminate()
                self._process.wait()
                LOGGER.debug("Stopped web server")

        def _is_stopped(self):
            if self._process is None:
                return True
            else:
                return self._process.poll() is not None

    def _start_web_server():
        SERVER_PROCESS.start()

    def _stop_web_server():
        SERVER_PROCESS.stop()

    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        LOGGER.debug("Receiving message on topic %s with payload %s", msg.topic, payload)
        if payload['status'] is True:
            _start_web_server()
        else:
            _stop_web_server()

    def _end_program(signum, frame):
        LOGGER.debug("Received termination signal %i", signum)
        _exit_program(0)

    def _exit_program(exit_code):
        if exit_code != 0:
            LOGGER.error("Exiting with error code %d", exit_code)
        else:
            LOGGER.info("Exiting normally")

        try:
            MQTT_CLIENT.loop_stop()
            MQTT_CLIENT.disconnect()
        except Exception:
            LOGGER.error('Exception occurred when trying to close mqtt client', exc__info=True)

        try:
            SERVER_PROCESS.stop()
        except Exception:
            LOGGER.error('Exception occurred when trying to shutdown server', exc__info=True)

        LOGGER.info("Done")
        exit(exit_code)

    LOGGER.info("Starting program")

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
        LOGGER.debug("Creating server process wrapper")
        SERVER_PROCESS = ServerProcess(WEB_SERVER_PROGRAM)

        LOGGER.debug("Creating mqtt client for host %s and port %s", MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        LOGGER.debug("Subscribing to topic %s", MQTT_TOPIC_GPIO_BUTTON_1)
        MQTT_CLIENT.subscribe(MQTT_TOPIC_GPIO_BUTTON_1, qos=1)
        MQTT_CLIENT.loop_forever()

    except Exception:
        LOGGER.error("Exception occurred", exc_info=True)
        _exit_program(1)

