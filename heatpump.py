#!/usr/bin/python3.4

import time
import ssl
import paho.mqtt.client as mqtt

class Heatpump(object):
	"""Heatpump controlled by RPi with ir-led.
	Following attributes can (must) be configured:

	Attributes:
		temp: The target temperature in Celcius. Default 21.
		timer_mode: Off, Sleep, Timer_off_time, Timer_on_time, Off-On. Default Off
		fan_mode: Auto, High, Med, Low, Quiet. Default Auto.
		fan_swing_mode: Off, Vertical, Horizontal, Both. Default Off.
		master_mode: Auto, Cool, Dry, Fan, Heat. Default Heat.
		sensor: True, False. Default False (off).
	"""

	byte1 = '0x14' 		#Marker1
	byte2 = '0x63'		#Marker2
	byte3 = '0x00'		#Parity
	byte4 = '0x10'		#Custom1
	byte5 = '0x10'		#Custom2
	byte6 = '0xFE'		#CommandCode
	byte7 = '0x09'		#Unknown
	byte8 = '0x30'		#Unknown
	#Byte9_low = temp
	byte9_high = '0x00' #on-off state, 0x0 if device was on, 0x1 if device was off and now on
	#Byte10_low = timer_mode
	#Byte10_high = master_mode 
	#Byte11_low = fan speed
	#Byte11_high = swing mode
	byte12 = '0x18' #timer value in minutes, initially just sending something
	byte13 = '0x04' #timer details to be added
	byte14 = '0x05' #timer stuff
	#Byte15 = Sensor
	#Byte16 = checksum

	temp_h = {16:'0x00',17:'0x01',18:'0x02',19:'0x03',20:'0x04',21:'0x05',22:'0x06',23:'0x07',24:'0x09',25:'0x09',26:'0x0a',27:'0x0b',28:'0x0c',29:'0x0d',30:'0x0e'}
	timer_mode_h = {'Off':'0x00', 'Sleep':'0x01', 'Timer_off_time':'0x02', 'Timer_on_time':'0x03', 'Off-On':'0x04'}
	fan_mode_h = {'Auto':'0x00', 'High':'0x01', 'Med':'0x02', 'Low':'0x03', 'Quiet':'0x04'}
	fan_swing_mode_h = {'Off':'0x00','Vertical':'0x01','Horizontal':'0x02','Both':'0x03'}
	master_mode_h = {'Auto':'0x00', 'Cool':'0x01', 'Dry':'0x02', 'Fan':'0x03', 'Heat':'0x04'}
	sensor_h = {True:'0x21',False:'0x20'}

	debug = True

	def __init__(self, temp=21, timer_mode='Off', fan_mode='Auto', fan_swing_mode='Off', master_mode='Heat', sensor=False):
		"""returns a heatpump object with name as *name* and default initial values set"""
		#self.name = name
		self.temp = temp
		self.timer_mode = timer_mode
		self.fan_mode = fan_mode
		self.fan_swing_mode = fan_swing_mode
		self.master_mode = master_mode
		self.sensor = sensor	

#temperature = temp['21']
#Mode = master_mode['Heat']
#timer = timer_mode['Off']
#fan_swing = fan_swing_mode['Vertical']
#fan = fan_speed['Auto']
#Sensor_status = Sensor['On']

#convert the hex data to binary and calculate the checksum from Bytes 8-15
	def transmit(self):
		def convert(byte):
			#take the byte, convert to binary and fill in leading zeros to fill word
			binary = bin(int(byte,16))[2:].zfill(8)
			#print binary
			return binary

		def convert_b_to_B(highbits,lowbits):
			#take two half bytes, fill in leading zeros for each and combine to a Byte
			low = bin(int(lowbits,16))[2:].zfill(4)
			high = bin(int(highbits,16))[2:].zfill(4)
			byte = high + low
			return byte

		def calculate_checksum(data):
			sum = 0

			for byte in data:
				sum+=int(byte,2)
				#print (sum)
				#print (bin(sum))
			if sum < 256:
				checksum = 256 - sum
			else: 
				checksum = 512 - sum
			#print (checksum)
			#print bin(checksum)
			return bin(checksum)[2:].zfill(8)		

		def transmit_data(self):
			import pigpio
			import ir_tx
			#initialise device and clear any previous data
			pi = pigpio.pi()
                        pi.set_pull_up_down(22, pigpio.PUD_DOWN)
			tx = ir_tx.tx(pi, 22, 38000)
			tx.clear_code()				

			#create the ir code
			#add Leader
			tx.add_to_code(125,62)

			#add the data
			for bits in irsend:
				if bits == '1':
					tx.add_to_code(16,47) #0 18 44
				else:
					tx.add_to_code(16,16) #1 18 14

			#add trailer
			tx.add_to_code(16,305)

			#send code and release device
			tx.send_code()
			tx.clear_code()
			pi.stop()

#		def prepare(self):

		Byte8 = convert(self.byte8)
		Byte9 = convert_b_to_B(self.temp_h[self.temp], self.byte9_high)
		Byte10 = convert_b_to_B(self.timer_mode_h[self.timer_mode], self.master_mode_h[self.master_mode])
		Byte11 = convert_b_to_B(self.fan_swing_mode_h[self.fan_swing_mode], self.fan_mode_h[self.fan_mode])
		Byte12 = convert(self.byte12)
		Byte13 = convert(self.byte13)
		Byte14 = convert(self.byte14)
		Byte15 = convert(self.sensor_h[self.sensor])
		CSData = [Byte8, Byte9, Byte10, Byte11, Byte12, Byte13, Byte14, Byte15]
		print(CSData)
		checksum = calculate_checksum(CSData)
		print('temp=' + str(self.temp) + ' mode=' + self.master_mode + ' speed=' + self.fan_mode + ' swing=' + self.fan_swing_mode + ' sensor=' + str(self.sensor)) 
		print(checksum)

		#add the data to variable for easy sending, reverse each byte for sending LSB first
		irsend = convert(self.byte1)[::-1] + \
		convert(self.byte2)[::-1] + \
		convert(self.byte3)[::-1] + \
		convert(self.byte4)[::-1] + \
		convert(self.byte5)[::-1] + \
		convert(self.byte6)[::-1] + \
		convert(self.byte7)[::-1] + \
		Byte8[::-1] + \
		Byte9[::-1] + \
		Byte10[::-1] + \
		Byte11[::-1] + \
		Byte12[::-1] + \
		Byte13[::-1] + \
		Byte14[::-1] + \
		Byte15[::-1] + \
		checksum[::-1]
		print (irsend)

		#transmit the data
		transmit_data(irsend)
 
#MQTT Client stuff
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
	print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
#	client.subscribe("$SYS/#")
	client.subscribe("aircon/upstairs/+")
#        client.subscribe("aircon/upstairs/fanspeed")
# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
	print pumppu.temp
        print type(pumppu.temp)
	print(msg.topic+" "+str(msg.payload))
        if "temp" in msg.topic:
            pumppu.temp = int(float(msg.payload))
        elif "fan_mode" in msg.topic:
            pumppu.fan_mode = str(msg.payload)
        elif "swing_mode" in msg.topic:
            pumppu.fan_swing_mode = str(msg.payload)
        elif "sensor" in msg.topic:
            pumppu.sensor = msg.payload
        elif "master_mode" in msg.topic:
            pumppu.master_mode = str(msg.payload)
	print pumppu.master_mode + str(pumppu.temp) + pumppu.fan_mode + pumppu.fan_swing_mode
	pumppu.transmit()
#	print(str(msg.payload))

client = mqtt.Client()
client.tls_set(ca_certs="/etc/mosquitto/certs/ca.crt", certfile="/etc/mosquitto/certs/clientMasa.crt", 
    keyfile="/etc/mosquitto/certs/clientMasa.key", cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 8889, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

pumppu = Heatpump()
client.loop_forever()

