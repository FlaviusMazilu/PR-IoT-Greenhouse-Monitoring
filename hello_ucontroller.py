import network
import time
from umqtt.simple import MQTTClient
 
from machine import Pin, I2C
import time
import json

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=50000)

address = 0x76

REG_TEMP_MSB = 0xFA
REG_TEMP_LSB = 0xFB
REG_TEMP_XLSB = 0xFC
REG_PRESS_MSB = 0xF7
REG_PRESS_LSB = 0xF8
REG_PRESS_XLSB = 0xF9
REG_CONTROL = 0xF4
MODE_NORMAL = 0x27

REG_CALIB = 0x88

def init_sensor():
	i2c.writeto_mem(address, REG_CONTROL, bytes([MODE_NORMAL]))
	time.sleep(0.5)
	
def read_calibration_data():
	calib = i2c.readfrom_mem(address, REG_CALIB, 24)
	
	dig_T1 = calib[0] | (calib[1] << 8)
	dig_T2 = calib[2] | (calib[3] << 8)
	dig_T3 = calib[4] | (calib[5] << 8)
	
	dig_P1 = calib[6] | (calib[7] << 8)
	dig_P2 = calib[8] | (calib[9] << 8)
	dig_P3 = calib[10] | (calib[11] << 8)
	dig_P4 = calib[12] | (calib[13] << 8)
	dig_P5 = calib[14] | (calib[15] << 8)
	dig_P6 = calib[16] | (calib[17] << 8)
	dig_P7 = calib[18] | (calib[19] << 8)
	dig_P8 = calib[20] | (calib[21] << 8)
	dig_P9 = calib[22] | (calib[23] << 8)
	
	return {
		'dig_T1': dig_T1, 'dig_T2': dig_T2, 'dig_T3': dig_T3,
		'dig_P1': dig_P1, 'dig_P2': dig_P2, 'dig_P3': dig_P3,
		'dig_P4': dig_P4, 'dig_P5': dig_P5, 'dig_P6': dig_P6,
		'dig_P7': dig_P7, 'dig_P8': dig_P8, 'dig_P9': dig_P9
	}

def read_raw_temp():
	msb = i2c.readfrom_mem(address, REG_TEMP_MSB, 1)[0]
	lsb = i2c.readfrom_mem(address, REG_TEMP_LSB, 1)[0]
	xlsb = i2c.readfrom_mem(address, REG_TEMP_XLSB, 1)[0]
	raw_temp = (msb << 12) | (lsb << 4) | (xlsb >> 4)
	return raw_temp

def read_raw_press():
	msb = i2c.readfrom_mem(address, REG_PRESS_MSB, 1)[0]
	lsb = i2c.readfrom_mem(address, REG_PRESS_LSB, 1)[0]
	xlsb = i2c.readfrom_mem(address, REG_PRESS_XLSB, 1)[0]
	raw_press = (msb << 12) | (lsb << 4) | (xlsb >> 4)
	return raw_press

def compensate_temperature(raw_temp, calib):
	dig_T1 = calib['dig_T1']
	dig_T2 = calib['dig_T2']
	dig_T3 = calib['dig_T3']
	
	var1 = (((raw_temp >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
	var2 = (((((raw_temp >> 4) - dig_T1) * ((raw_temp >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
	t_fine = var1 + var2
	temperature = (t_fine * 5 + 128) >> 8
	return temperature / 100.0, t_fine

# Functie pentru compensarea presiunii
def compensate_pressure(raw_press, calib, t_fine):
	dig_P1 = calib['dig_P1']
	dig_P2 = calib['dig_P2']
	dig_P3 = calib['dig_P3']
	dig_P4 = calib['dig_P4']
	dig_P5 = calib['dig_P5']
	dig_P6 = calib['dig_P6']
	dig_P7 = calib['dig_P7']
	dig_P8 = calib['dig_P8']
	dig_P9 = calib['dig_P9']

	var1 = t_fine - 128000
	var2 = var1 * var1 * dig_P6
	var2 = var2 + ((var1 * dig_P5) << 17)
	var2 = var2 + (dig_P4 << 35)
	var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
	var1 = (((1 << 47) + var1) * dig_P1) >> 33

	if var1 == 0:
		return 0
	
	pressure = 1048576 - raw_press
	pressure = ((pressure << 31) - var2) * 3125 // var1
	var1 = (dig_P9 * (pressure >> 13) * (pressure >> 13)) >> 25
	var2 = (dig_P8 * pressure) >> 19

	pressure = ((pressure + var1 + var2) >> 8) + (dig_P7 << 4)
	return pressure / 25600.0  # Conversie in hPa


init_sensor()
calibration_data = read_calibration_data()

ssid = 'flavius_mazilu'
password = 'prego123'
mqtt_server = '172.20.10.2'
topic = "greenhouse/temperature"
client_id = "sensor_begin"

our_topic = "greenhouse/temperature"
print("before connecting")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
	time.sleep(1)

print(wlan.ifconfig())
 
client = MQTTClient(client_id, mqtt_server, port=1883)
client.connect()
print("Connected to MQTT broker")
try:
	while True:
		# message = b"Hello World"
		raw_temp = read_raw_temp()
		raw_press = read_raw_press()

		temp, t_fine = compensate_temperature(raw_temp, calibration_data)
		press = compensate_pressure(raw_press, calibration_data, t_fine)
		
		message = f"{temp}"
    	
		payload = {"sender_id": client_id, "value": temp}
		client.publish(topic, json.dumps(payload))
		print(f"has sent temperature {temp}")
		time.sleep(1)
finally:
	client.disconnect()
