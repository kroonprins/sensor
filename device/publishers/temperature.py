""" Read temperature from sensor and send it to queue
"""

import json
import logging
import signal
import sqlite3
import time
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      MQTT_HOST, MQTT_PORT, TEMPERATURE_MESSAGE_TYPE, \
                        MQTT_TOPIC_SENSOR_DATA, \
                        MQTT_TOPIC_PROPERTIES, MQTT_PROPERTY_INTERVAL, \
                      SQLITE_DATABASE, TABLE_PROPERTIES, DEFAULT_INTERVAL

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('temperature_publisher')

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
        payload = json.dumps(message_object)
        LOGGER.debug("Publishing message %s to topic %s", payload, MQTT_TOPIC_SENSOR_DATA)
        mqtt_client.publish(MQTT_TOPIC_SENSOR_DATA, payload=payload, qos=1)

    def _measure_and_send(sensor):
        temperature_measurement, timing = _get_temperature(sensor)
        _send_message(MQTT_CLIENT, _create_message(temperature_measurement, timing))

    def _read_interval_from_database():
        LOGGER.debug("Connecting to database %s", SQLITE_DATABASE)
        database_connection = sqlite3.connect(SQLITE_DATABASE)
        try:
            cursor = database_connection.cursor()
            query = "select interval from "+TABLE_PROPERTIES+ \
                                " order by version desc"
            LOGGER.debug("Executing query [%s]", query)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                LOGGER.warn("The property for the interval could not be found. " + \
                            "Will use default interval %d", DEFAULT_INTERVAL)
                interval = DEFAULT_INTERVAL
            else:
                interval = record[0]
            return interval
        finally:
            LOGGER.debug("Closing connection to database %s", SQLITE_DATABASE)
            database_connection.close()

    def _on_message(client, userdata, msg):
        payload = msg.payload
        LOGGER.info("Receiving message on topic %s with payload %s to update checking interval", \
                     msg.topic, payload)
        new_interval = payload
        global INTERVAL
        INTERVAL = int(new_interval)

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
        LOGGER.debug("Creating temperature sensor helper class")
        TEMPERATURE_SENSOR = W1ThermSensor()

        LOGGER.debug("Creating mqtt client for host %s and port %s", MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
        TOPIC = MQTT_TOPIC_PROPERTIES+"/"+MQTT_PROPERTY_INTERVAL
        LOGGER.debug("Subscribing to topic %s", TOPIC)
        MQTT_CLIENT.subscribe(TOPIC, qos=1)
        MQTT_CLIENT.loop_start()

        LOGGER.debug("Retrieving initial check interval from the database")
        INTERVAL = _read_interval_from_database()
        LOGGER.info("Retrieving new measurements every %d seconds", INTERVAL)

        while True:
            _measure_and_send(TEMPERATURE_SENSOR)
            time.sleep(INTERVAL)

    except Exception:
        LOGGER.error("Exception occurred", exc_info=True)
        _exit_program(1)



