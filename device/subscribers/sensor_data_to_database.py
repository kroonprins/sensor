""" Read sensor data from the queue and store in the database
"""

import json
import logging
import signal
import sqlite3
import paho.mqtt.client as mqtt
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_SENSOR_DATA, \
                        MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA, \
                      SQLITE_DATABASE, TABLE_MEASUREMENTS

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('sensor_data_to_database')

if __name__ == '__main__':
    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        LOGGER.debug("Receiving message on topic %s with payload %s", msg.topic, payload)
        try:
            insert_query = "insert into "+TABLE_MEASUREMENTS+" (type, timing, value) VALUES (?,?,?)"
            LOGGER.debug("Executing query [%s][%d,%s,%s]", \
                               insert_query, 1, payload['timing'], payload['value'])
            DATABASE_CONNECTION.execute(insert_query, \
                                         (1, payload['timing'], payload['value']))
            DATABASE_CONNECTION.commit()
        except Exception:
            DATABASE_CONNECTION.rollback()
            raise

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
            DATABASE_CONNECTION.close()
        except Exception:
            LOGGER.error('Exception occurred when trying to close database client', exc__info=True)

        LOGGER.info("Done")
        exit(exit_code)

    LOGGER.info("Starting program")

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
        LOGGER.debug("Connecting to database %s", SQLITE_DATABASE)
        DATABASE_CONNECTION = sqlite3.connect(SQLITE_DATABASE)

        LOGGER.debug("Creating mqtt client for host %s and port %s and client id %s", \
                        MQTT_HOST, MQTT_PORT, MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA)
        MQTT_CLIENT = mqtt.Client(client_id=MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA, \
                                                                        clean_session=False)
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        LOGGER.debug("Subscribing to topic %s", MQTT_TOPIC_SENSOR_DATA)
        MQTT_CLIENT.subscribe(MQTT_TOPIC_SENSOR_DATA, qos=1)
        MQTT_CLIENT.loop_forever()

    except Exception:
        LOGGER.error("Exception occurred", exc_info=True)
        _exit_program(1)
