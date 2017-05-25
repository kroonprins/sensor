""" Handling button clicks for button one
"""

import json
import paho.mqtt.client as mqtt
from constants import GPIO_PIN_BUTTON_1, MQTT_TOPIC_GPIO_BUTTON_1, MQTT_HOST, MQTT_PORT
from gpio_handling import GPIOinputHandler

if __name__ == '__main__':
    def _button_pushed(state):
        if "status" in state:
            state["status"] = not state["status"]
        else:
            state["status"] = False
        payload = json.dumps(state)
        print "Sending to "+MQTT_TOPIC_GPIO_BUTTON_1+" topic payload "+payload
        MQTT_CLIENT.publish(MQTT_TOPIC_GPIO_BUTTON_1, payload=payload, qos=1, retain=True)

    def _end_program():
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()

    MQTT_CLIENT = mqtt.Client()
    MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
    MQTT_CLIENT.loop_start()

    GPIO_INPUT_HANDLER = GPIOinputHandler(GPIO_PIN_BUTTON_1, _button_pushed, \
                                           termination_handler=_end_program)
    GPIO_INPUT_HANDLER.run()
