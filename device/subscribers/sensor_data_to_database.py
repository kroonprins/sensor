""" Read sensor data from the queue and store in the database
"""
import signal
import json
import sqlite3
import traceback
import paho.mqtt.client as mqtt
from constants import MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_SENSOR_DATA, \
                      MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA, \
                      SQLITE_DATABASE, TABLE_MEASUREMENTS

if __name__ == '__main__':
    def _on_connect(client, userdata, return_code):
        pass

    def _on_message(client, userdata, msg):
        payload = json.loads(msg.payload)
        print msg.topic+" "+str(payload['type'])+" - "+str(payload['timing']) \
                                                    +" - "+str(payload['value'])
        try:
            DATABASE_CONNECTION.execute( \
                "insert into "+TABLE_MEASUREMENTS+" (type, timing, value) VALUES (?,?,?)", \
                                         (1, payload['timing'], payload['value']))
            DATABASE_CONNECTION.commit()
        except Exception as exc:
            DATABASE_CONNECTION.rollback()
            raise exc

    def _on_disconnect(client, userdata, return_code):
        pass

    def _end_program(signum, frame):
        _exit_program(0)

    def _exit_program(exit_code):
        print "Exiting... ("+str(exit_code)+")"
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        DATABASE_CONNECTION.close()
        exit(exit_code)

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
        MQTT_CLIENT = mqtt.Client(client_id=MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA, \
                                                                        clean_session=False)
        MQTT_CLIENT.on_connect = _on_connect
        MQTT_CLIENT.on_message = _on_message
        MQTT_CLIENT.on_disconnect = _on_disconnect

        DATABASE_CONNECTION = sqlite3.connect(SQLITE_DATABASE)
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        MQTT_CLIENT.subscribe(MQTT_TOPIC_SENSOR_DATA, qos=1)
        MQTT_CLIENT.loop_forever()

    except Exception:
        traceback.print_exc()
        _exit_program(1)
