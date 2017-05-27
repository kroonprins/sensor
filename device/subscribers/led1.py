""" Toggle LED 1
"""

import signal
import json
import traceback
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from constants import MQTT_TOPIC_GPIO_BUTTON_1, GPIO_PIN_LED_1, MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE
from gpio_handling import GPIOoutputHandler

if __name__ == '__main__':

    def _on_connect(client, userdata, return_code):
        pass

    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        print msg.topic+" "+str(payload['status'])
        if payload['status'] is True:
            level = GPIO.HIGH
        else:
            level = GPIO.LOW
        GPIO_OUTPUT_HANDLER.set_output(level)

    def _on_disconnect(client, userdata, return_code):
        pass

    def _end_program(signum, frame):
        _exit_program(0)

    def _exit_program(exit_code):
        print "Exiting... ("+str(exit_code)+")"
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        GPIO_OUTPUT_HANDLER.cleanup()
        exit(exit_code)

    try:
        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.on_connect = _on_connect
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.on_disconnect = _on_disconnect

        signal.signal(signal.SIGINT, _end_program)
        signal.signal(signal.SIGTERM, _end_program)

        GPIO_OUTPUT_HANDLER = GPIOoutputHandler(GPIO_PIN_LED_1)

        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        MQTT_CLIENT.subscribe(MQTT_TOPIC_GPIO_BUTTON_1, qos=1)
        MQTT_CLIENT.loop_forever()

    except Exception:
        traceback.print_exc()
        _exit_program(1)

