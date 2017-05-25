""" Read temperature from sensor and send it to queue
"""
import signal
import time
import json
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
from constants import MQTT_HOST, MQTT_PORT, TEMPERATURE_MESSAGE_TYPE, MQTT_TOPIC_SENSOR_DATA

if __name__ == '__main__':

    def _get_temperature(sensor):
        measurement = sensor.get_temperature()
        return measurement, int(time.time())

    def _create_message(temperature_measurement, timing):
        return {
            'type': TEMPERATURE_MESSAGE_TYPE,
            'value': temperature_measurement,
            'timing': timing
        }

    def _send_message(mqtt_client, message_object):
        print "Publishing: "+str(message_object["timing"])+" - "+str(message_object["value"])
        mqtt_client.publish(MQTT_TOPIC_SENSOR_DATA, payload=json.dumps(message_object), qos=1)

    def _measure_and_send(sensor):
        temperature_measurement, timing = _get_temperature(sensor)
        _send_message(MQTT_CLIENT, _create_message(temperature_measurement, timing))

    def _end_program(signum, frame):
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        exit(0)

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    TEMPERATURE_SENSOR = W1ThermSensor()

    MQTT_CLIENT = mqtt.Client()
    MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
    MQTT_CLIENT.loop_start()

    while True:
        _measure_and_send(TEMPERATURE_SENSOR)
        time.sleep(15)



