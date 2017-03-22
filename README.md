# mqtt-aircon
A custom component for home assistant to control Heatpump unit via mqtt

# Motivation
To control a heatpump (Aircon heating/cooling unit) using Home Assistant and MQTT with self-made IR-transmitter.

# Status
heatpumppu.py is a modified version of the hass climate demo component, slightly modified to send mqtt messages.
heatpump.py should be running as a daemon and listen to a mqtt topic and then transmit appropriate ir signals.
System is running on a RPI. 

# TODO
Add support for presense sensor in the heatpump

Change code so it reads heatpump info from config instead of from code

