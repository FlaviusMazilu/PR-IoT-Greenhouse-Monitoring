from flask import Flask, jsonify
from paho.mqtt import client as mqtt_client
import json
import random
from time import sleep
import sys, getopt

broker = 'localhost'
port = 1883
topic_temperatures = 'greenhouse/temperature'
topic_light = 'greenhouse/temperatures'

if len(sys.argv) < 2:
    print("enter client_id")
    exit()

client_id = sys.argv[1]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=client_id)
mqttc.on_connect = on_connect

mqttc.connect(broker, port, 60)

while True:
    random_integer = random.randint(20, 25)
    print(random_integer)
    
    payload = {"sender_id": client_id, "value": random_integer}
    mqttc.publish('greenhouse/temperature', json.dumps(payload))


    random_integer = random.randint(1800, 2000)
    payload = {"sender_id": client_id, "value": random_integer}
    mqttc.publish('greenhouse/light', json.dumps(payload))

    print("I've sent a message")

    sleep(5)