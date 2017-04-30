import paho.mqtt.client as mqtt
from w1thermsensor import W1ThermSensor
import time
import json

sensor = W1ThermSensor()

client = mqtt.Client()
client.connect("localhost")
client.loop_start()

try:
    while True:
        temperature = sensor.get_temperature()
        timing = int(time.time())
        message = {
           'type': 'TEMPERATURE',
           'value': temperature,
           'timing': timing
        }
        print "Publishing: "+str(timing)+" - "+str(temperature)
        client.publish("paho/temperature", payload=json.dumps(message), qos=1)
        time.sleep(15)
except KeyboardInterrupt:
    client.disconnect()
