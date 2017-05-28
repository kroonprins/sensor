""" Start wifi access point
"""

import json
import logging
import signal
import subprocess
import paho.mqtt.client as mqtt
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_GPIO_BUTTON_1

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('wifi_access_point')

if __name__ == "__main__":

    def _start_access_point():
        LOGGER.info("Starting up interface wlan0")
        subprocess.Popen(['sudo', 'ifconfig', 'wlan0', 'up'])
        LOGGER.info("Starting hostapd")
        subprocess.Popen(['sudo', '/usr/sbin/hostapd', '-B', '/etc/hostapd/hostapd.conf'])
        LOGGER.info("Starting dhcp server")
        subprocess.Popen(['sudo', 'service', 'isc-dhcp-server', 'restart'])
        LOGGER.info("Access point started")

    def _stop_access_point():
        LOGGER.info("Killing hostapd")
        subprocess.Popen(['sudo', 'killall', 'hostapd'])
        LOGGER.info("Stopping dhcp server")
        subprocess.Popen(['sudo', 'service', 'isc-dhcp-server', 'stop'])
        LOGGER.info("Shutting down interface wlan0")
        subprocess.Popen(['sudo', 'ifconfig', 'wlan0', 'down'])
        LOGGER.info("Access point stopped")

    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        LOGGER.debug("Receiving message on topic %s with payload %s", msg.topic, payload)
        if payload['status'] is True:
            _start_access_point()
        else:
            _stop_access_point()

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

        LOGGER.info("Done")
        exit(exit_code)

    LOGGER.info("Starting program")

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
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
