from flask import Flask, render_template, request, jsonify
from paho.mqtt import client as mqtt_client
import json
import logging

app = Flask(__name__)

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

mqtt_client_id = "web"
mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=mqtt_client_id)
mqttc.on_connect = on_connect

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("before connect to broker")
mqttc.connect('mosquitto', 8883, 6000)


@app.route('/temp/<signal>', methods=['POST'])
def turn_temp(signal: str):
    if signal != "on" and signal != "off":
        return "only on/off", 404

    payload = {"value": signal}
    mqttc.publish('controlplane/temp', json.dumps(payload))

    return "Done!", 200

@app.route('/light/<signal>', methods=['POST'])
def turn_light(signal: str):
    if signal != "on" and signal != "off":
        return "only on/off", 404

    payload = {"value": signal}
    mqttc.publish('controlplane/light', json.dumps(payload))

    return "Done!", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context='adhoc')
