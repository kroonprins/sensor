""" Handling button clicks for button one
"""

import json
import logging
import paho.mqtt.client as mqtt
from gpio_handling import GPIOinputHandler
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                       GPIO_PIN_BUTTON_1, MQTT_TOPIC_GPIO_BUTTON_1, \
                       MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('button1')

if __name__ == '__main__':
    def _button_pushed(state):
        LOGGER.debug("Button 1 pushed: %s", state)
        if "status" in state:
            state["status"] = not state["status"]
        else:
            state["status"] = False
        payload = json.dumps(state)
        LOGGER.debug("Publishing message %s to topic %s", payload, MQTT_TOPIC_GPIO_BUTTON_1)
        MQTT_CLIENT.publish(MQTT_TOPIC_GPIO_BUTTON_1, payload=payload, qos=1, retain=True)

    def _end_program():
        try:
            MQTT_CLIENT.loop_stop()
            MQTT_CLIENT.disconnect()
        except Exception:
            LOGGER.error('Exception occurred when trying to close mqtt client', exc__info=True)
    
    LOGGER.info("Starting program")

    LOGGER.debug("Creating mqtt client for host %s and port %s", MQTT_HOST, MQTT_PORT)
    MQTT_CLIENT = mqtt.Client()
    MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
    MQTT_CLIENT.loop_start()

    LOGGER.debug("Creating GPIO input handler")
    GPIO_INPUT_HANDLER = GPIOinputHandler(GPIO_PIN_BUTTON_1, _button_pushed, \
                                           termination_handler=_end_program)
    GPIO_INPUT_HANDLER.run()
