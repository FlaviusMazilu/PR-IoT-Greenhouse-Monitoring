from flask import Flask, jsonify
from paho.mqtt import client as mqtt_client
import json
import random
from time import sleep
import sys, getopt
import logging

broker = 'localhost'
port = 1884
topic_temperatures = 'greenhouse/temperature'
topic_light = 'greenhouse/temperatures'

mqtt_topic_control_temp = 'controlplane/temp'
mqtt_topic_control_light = 'controlplane/light'

is_sending_light_value = True
is_sending_temp_value = True

if len(sys.argv) < 2:
    print("enter client_id")
    exit()

client_id = sys.argv[1]

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(mqtt_topic_control_light)
    client.subscribe(mqtt_topic_control_temp)
    print(f"Connected with result code {reason_code}")

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    
    topic = msg.topic
    global is_sending_temp_value
    global is_sending_light_value

    value = message.get('value')
    if topic == mqtt_topic_control_light:
        logging.info(f'has set light: {value}')
        is_sending_light_value = True if value == "on" else False

    if topic == mqtt_topic_control_temp:
        logging.info(f'has set temp: {value}')
        is_sending_temp_value = True if value == "on" else False


mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=client_id)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(broker, port, 60)

mqttc.loop_start()
while True:
    random_integer = random.randint(20, 25)
    print(random_integer)
    
    if is_sending_temp_value:
        payload = {"sender_id": client_id, "value": float(random_integer)}
        mqttc.publish('greenhouse/temperature', json.dumps(payload))
        print("I've sent a temp val")


    random_integer = random.randint(1800, 2000)
    if is_sending_light_value:
        payload = {"sender_id": client_id, "value": float(random_integer)}
        mqttc.publish('greenhouse/light', json.dumps(payload))
        print("I've sent a light val")

    sleep(5)