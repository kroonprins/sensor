""" Common constants
"""
import os

GPIO_PIN_BUTTON_1 = 17
GPIO_PIN_LED_1 = 18

MQTT_HOST = "localhost"
MQTT_PORT = "1883"
MQTT_KEEPALIVE = 60
MQTT_TOPIC_GPIO_EVENTS = "gpio_events"
MQTT_TOPIC_GPIO_BUTTON_1 = MQTT_TOPIC_GPIO_EVENTS+"_button_1"
MQTT_TOPIC_SENSOR_DATA = "sensor_data"
MQTT_PERSISTENT_SESSION_CLIENT_ID_SENSOR_DATA = "sensor_data_client_id"
MQTT_TOPIC_PROPERTIES = "application_properties"
MQTT_PROPERTY_INTERVAL = "interval"

TEMPERATURE_MESSAGE_TYPE = "TEMPERATURE"

DEFAULT_INTERVAL = 3600

SQLITE_DATABASE = os.environ['HOME']+"/sqlite/measurements.db"
TABLE_MEASUREMENTS = "measurement"
TABLE_PROPERTIES = "properties"

WEB_SERVER_PROGRAM = os.environ['HOME']+"/web_server/main.py"
WEB_SERVER_PORT = 8080

