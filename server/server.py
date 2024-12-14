from paho.mqtt import client as mqtt_client
import influxdb_client
import json
import os

database = os.getenv('INFLUXDB_DATABASE_NAME')
org = os.getenv('INFLUXDB_ORG')
token = os.environ.get('INFLUXDB_TOKEN') 
url = os.environ.get('INFLUXDB_URL')

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api()

broker = os.environ.get('MQTT_BROKER_URL')
port = 1883
mqtt_topic_subscribed = 'greenhouse/#'
mqtt_topic_temperature = 'greenhouse/temperature'
mqtt_topic_light = 'greenhouse/light'
mqtt_client_id = "server"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(mqtt_topic_subscribed)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    
    try:
        value = message.get('value')
        sensor_id = message.get("sender_id")
    except TypeError:
        print("got an invalid value/sender_id")
        return

    topic = msg.topic

    print(f"Value received on topic: '{topic}' from {sensor_id}: {value}")
    
    if topic == mqtt_topic_temperature and value != -9999:
        p = influxdb_client.Point("temperature").tag("sensor_id", sensor_id).field("value", value)
        write_api.write(bucket="measurements", org=org, record=p)

    if topic == mqtt_topic_light:
        p = influxdb_client.Point("light").tag("sensor_id", sensor_id).field("value", value)
        write_api.write(bucket="measurements", org=org, record=p)

 
mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=mqtt_client_id)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(broker, port, 60)

mqttc.loop_forever()