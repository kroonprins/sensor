import paho.mqtt.client as mqtt
import sqlite3
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected client "+client._client_id+" with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    print(msg.topic+" "+str(payload['type'])+" - "+str(payload['timing'])+" - "+str(payload['value']))
    try:
        conn.execute("insert into measurement (type, timing, value) VALUES (?,?,?)",(1,payload['timing'],payload['value']))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise exc

def on_disconnect(client, userdata, rc):
    print("Disconnecting "+client._client_id)

client = mqtt.Client(client_id="tobias", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    conn = sqlite3.connect('../sqlite/measurements.db')
    client.connect("localhost", 1883, 60)
    client.subscribe("paho/temperature", qos=1)
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    conn.close()
