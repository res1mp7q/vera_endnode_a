#!/usr/bin/env python
# End Node A runtime using I2C and MCP230.
# Jimmy Lamont 2017
# Make sure you enter your API Key, state, city (TWICE!) and Vera IP where annotated
#
#
import time
import requests
import Adafruit_CharLCD as LCD
from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import *
from time import sleep, strftime
from datetime import datetime





# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])


p = Popen('hostname -I', shell=True, stdout=PIPE)
IP = p.communicate()[0]


# Show button state.
lcd.clear()
lcd.message('\n     Hello')

time.sleep(3.0)

#Show version and name
lcd.clear()
lcd.message('  Vera \n    endnode1')
time.sleep(2.0)
lcd.clear()
lcd.blink(True)
lcd.message('\n15NOV2017  v0.03')
time.sleep(2.0)
lcd.clear()
lcd.message(IP)
time.sleep(2.0)

#Start complete, select any mode, wait\
lcd.show_cursor(False)
lcd.blink(False)
lcd.clear()
lcd.message('\n  Select mode')
time.sleep(2.0)

url = 'http://<Vera IP>:3480/data_request?id=lu_action&serviceId=urn:micasaverde-com:serviceId:HomeAutomationGateway1&action=SetHouseMode&Mode={}'
r = requests.get('http://api.wunderground.com/api/<API Key>/conditions/q/<State>/<City>.json')
data = r.json()

# Make list of button values, text, backlight colour, and luup call.
buttons = ( (LCD.SELECT, '\n     Home', (1,1,1), 1),
            (LCD.LEFT,   '\n     Panic'  , (1,0,0), 5),
            (LCD.UP,     '\n     Night'    , (0,0,1), 3),
            (LCD.DOWN,   '\n     Away'  , (0,1,0), 2),
            (LCD.RIGHT,  '\n    Vacation' , (1,0,1), 4) )

# Bringing it all back

lastmessage = ""

while True:
# Loop through each button and check if it is pressed.
	for button in buttons:
		if lcd.is_pressed(button[0]):
# Button is pressed, change the message and backlight.

			r = requests.get(url.format(button[3]))
			if r.status_code==200:
				if 'ok' in r.text.lower():
					lcd.clear()
					lcd.message(button[1])
					lastmessage = button[1]
					lcd.set_color(button[2][0], button[2][1], button[2][2])
#Check to see if we can get an http 200 message from vera
				else: 
					lcd.clear()
					lastmessage = 'Vera Response not OK'
					lcd.message(lastmessage)
#rut roh raggy print that something went wrong
			else:
				lcd.clear()
				lastmessage = 'No 200 response \nfrom Vera'
				lcd.message(lastmessage)

			time.sleep(10.0)

#Show Clock wunderground data while waiting for input
	if time.mktime(time.gmtime()) % 28800 == 0:
		r = requests.get('http://api.wunderground.com/api/<API Key>/conditions/q/<State>/<City>.json')
		data = r.json()


	now = "{}\n{}".format(datetime.now().strftime('%b %d  %H:%M'), data['current_observation']['temperature_string'])
	if lastmessage != now:
		lcd.clear()
		lcd.set_backlight(0)
		lcd.message (now)
		lastmessage = now
