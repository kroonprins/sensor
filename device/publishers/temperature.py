""" Read temperature from sensor and send it to queue
"""
import signal
import time
import json
import sqlite3
import traceback
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
from constants import MQTT_HOST, MQTT_PORT, TEMPERATURE_MESSAGE_TYPE, MQTT_TOPIC_SENSOR_DATA, \
                      SQLITE_DATABASE, TABLE_PROPERTIES, DEFAULT_INTERVAL, \
                      MQTT_TOPIC_PROPERTIES, MQTT_PROPERTY_INTERVAL

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

    def _read_interval_from_database():
        database_connection = sqlite3.connect(SQLITE_DATABASE)
        try:
            cursor = database_connection.cursor()
            cursor.execute("select interval from "+TABLE_PROPERTIES+" \
                                order by version desc")
            record = cursor.fetchone()
            if record is None:
                interval = DEFAULT_INTERVAL
            else:
                interval = record[0]
            return interval
        finally:
            database_connection.close()

    def _on_message(client, userdata, msg):
        print "Received message to update interval "+ \
               msg.topic+" "+str(msg.payload)
        new_interval = msg.payload
        global INTERVAL
        INTERVAL = int(new_interval)

    def _end_program(signum, frame):
        _exit_program(0)

    def _exit_program(exit_code):
        print "Exiting... ("+str(exit_code)+")"
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        exit(exit_code)

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
        TEMPERATURE_SENSOR = W1ThermSensor()

        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT.subscribe(MQTT_TOPIC_PROPERTIES+"/"+MQTT_PROPERTY_INTERVAL, qos=1)
        MQTT_CLIENT.loop_start()

        INTERVAL = _read_interval_from_database()
        print "Retrieving new measurements every "+str(INTERVAL)+" seconds"

        while True:
            _measure_and_send(TEMPERATURE_SENSOR)
            time.sleep(INTERVAL)
            print INTERVAL

    except Exception:
        traceback.print_exc()
        _exit_program(1)



