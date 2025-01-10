from paho.mqtt import client as mqtt_client
import influxdb_client
import json
import os
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

database = 'greenhouse'
org = 'priot'
token = 't7YjD517EApA2sS0vhxHyJfSw0zQ6I9D6kQ4ksf8lFgIaP9goSBhIdhItrm6sGq8VB_K7Su7wo9eujIqPbqNQQ=='
url = 'https://influx:8086'

verify_ssl="/mycerts/influxdb.crt"
client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org,
    ssl_ca_cert=verify_ssl
)
write_api = client.write_api()

broker = os.environ.get('MQTT_BROKER_URL')
port = 8883
mqtt_topic_subscribed = 'greenhouse/#'
mqtt_topic_temperature = 'greenhouse/temperature'
mqtt_topic_light = 'greenhouse/light'
mqtt_client_id = "server"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(mqtt_topic_subscribed)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    logging.info(f'message received: {message}')
    
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

mqttc.connect('mosquitto', port, 1883)
mqttc.loop_forever()