# -*- encoding: utf-8 -*-
#Electronics Auto Loader - Enric Gómez Pitarch & Marc Cobler
#BCN3D Technologies - Fundacio CIM
#
#Python program that can upload the firmware up to 8 boards in series
#It has 4 rocker switches to select the firmware to upload and a load button to
#start the sequence. First it ckecks for internet connection and pulls updates from github.
#It uses avrdude for .hex upload

#PIN Connections
#SWITCH 1		-->		PIN11 - GPIO17
#SWITCH 2		-->		PIN13 - GPIO27
#SWITCH 3		-->		PIN15 - GPIO22
#SWITCH 4		-->		PIN16 - GPIO23
#LOAD BUTTON	-->		PIN18 - GPIO24
#LED1			-->		PIN23 - GPIO11
#LED2			-->		PIN29 - GPIO5
#LED3			-->		PIN31 - GPIO6
#LED4			-->		PIN33 - GPIO13
#LED5			-->		PIN32 - GPIO12
#LED6			-->		PIN36 - GPIO16
#LED7			-->		PIN38 - GPIO20
#LED8			-->		PIN40 - GPIO21

import RPi.GPIO as GPIO
import time
import os
import sys
import socket
from serial.tools import list_ports
from clint.textui import colored 

filesRepoPath 	= ('/home/pi/BCN3D-Utilities')
repoPath 		= ('/home/pi/arduino-auto-loader')
BCN3DPlusPath 	= ('/home/pi/BCN3D-Utilities/Firmware\ uploader\ scripts/Files/BCN3D_Plus_latest.hex')
BCN3DRPath 		= ('/home/pi/bcn3d-utilities/Firmware\ uploader\ scripts/Files/BCN3D_R_latest.hex')
BCN3DSigmaPath 	= ('/home/pi/bcn3d-utilities/Firmware\ uploader\ scripts/Files/BCN3D_Sigma_Firmware_latest.hex')

#LEDS
LED1 = 11
LED2 = 5
LED3 = 6 
LED4 = 13
LED5 = 12
LED6 = 16
LED7 = 20
LED8 = 21

def haveInternet():
	REMOTE_SERVER = "www.google.com"
	try:
		host = socket.gethostbyname(REMOTE_SERVER)
		s = socket.create_connection((host, 443))
		return True
	except:
		pass
	return False


def syncGithub():
	#Update the repositor
	if haveInternet():
		print (colored.green("=============Internet is ON!================"))
		try:
			print "Getting updates from github"
			os.chdir(repoPath)
			currentDirectory = os.getcwd()
			print "the current directory is: %s" % currentDirectory
			os.system("git pull")
			os.chdir(filesRepoPath)
			os.system("git pull")
		except:
			print (colored.red("Something went wrong, check you internet connection"))
			pass
	else:
		print (colored.red("==========No internet, no github sync=========="))
        

def manageInputs():
        print "Setting the input switches"
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        #Set Pull ups to pins
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #Read the inputs for the first time
        input_state_24 = GPIO.input(24)
        input_state_17 = GPIO.input(17)
        input_state_27 = GPIO.input(27)
        input_state_22 = GPIO.input(22)
        input_state_23 = GPIO.input(23)
        
def comPortsInfo():
	#getting the comports
	global ports
	ports=list_ports.comports()
	#print ports
	print "There are %d available comports: " % len(ports)
	#list the comports available
	for port in ports:
		print (colored.green(port[0]))

def printButtonStatus(switch1, switch2, switch3, switch4):
	print "Switch 1 is set to: %d" % switch1
	print "Switch 2 is set to: %d" % switch2
	print "Switch 3 is set to: %d" % switch3
	print "Switch 4 is set to: %d" % switch4
	
def startUpLEDS():
	#Just a sequence of LEDs to know that the system is running the program
	#We need root access to manipulate the GPIO!
	print "Lighting some LEDs..."
	for x in range(0,4):
	     GPIO.setup(21, GPIO.OUT)
	     GPIO.output(21, GPIO.HIGH)
	     GPIO.setup(13, GPIO.OUT)
	     GPIO.output(13, GPIO.HIGH)
	     time.sleep(0.1)
	     #print "."
	     GPIO.output(21, GPIO.LOW)
	     GPIO.output(13, GPIO.LOW)
	     GPIO.setup(20, GPIO.OUT)
	     GPIO.output(20, GPIO.HIGH)
	     GPIO.setup(6, GPIO.OUT)
	     GPIO.output(6, GPIO.HIGH)
	     time.sleep(0.1)
	     #print "."
	     GPIO.output(20, GPIO.LOW)
	     GPIO.output(6, GPIO.LOW)
	     GPIO.setup(16, GPIO.OUT)
	     GPIO.output(16, GPIO.HIGH)
	     GPIO.setup(5, GPIO.OUT)
	     GPIO.output(5, GPIO.HIGH)
	     time.sleep(0.1)
	     #print "."
	     GPIO.output(16, GPIO.LOW)
	     GPIO.output(5, GPIO.LOW)
	     GPIO.setup(12, GPIO.OUT)
	     GPIO.output(12, GPIO.HIGH)
	     GPIO.setup(11, GPIO.OUT)
	     GPIO.output(11, GPIO.HIGH)
	     time.sleep(0.1)
	     #print "."
	     GPIO.output(12, GPIO.LOW)
	     GPIO.output(11, GPIO.LOW)
	     time.sleep(0.1)

def turnOnLED(pin):
	GPIO.output(pin, GPIO.HIGH)
	
def turnOffLED(pin):
	GPIO.output(pin, GPIO.LOW)
	
def turnOffAllLEDS():
	turnOffLED(LED1)
	turnOffLED(LED2)
	turnOffLED(LED3)
	turnOffLED(LED4)
	turnOffLED(LED5)
	turnOffLED(LED6)
	turnOffLED(LED7)
	turnOffLED(LED8)

def loadFirmware(firmware):
	x = 0
	for port in ports:
		print "loading %s firmware in Port %s" % (firmware, port[0])
		os.system("avrdude -p m2560 -c avrispmkII -V -D -P %s -U flash:w:%s:i" % (port[0], firmware))
		#turnOnLED(LED + x)
	
	turnOffAllLEDS()
	print (colored.green("============ALL BOARDS LOADED==============="))	
	
	

def checkButtons(channel):
	#Read the status of the switches and buttons
	try:
		print "Reading the inputs..."
		input_state_17 = GPIO.input(17) #Interruptor 1 - BCN3D+
		input_state_27 = GPIO.input(27) #Interruptor 2 - BCN3DR
		input_state_22 = GPIO.input(22) #Interruptor 3 - BCN3DSigma
		input_state_23 = GPIO.input(23) #Interruptor 4 - Unused
		printButtonStatus(input_state_17, input_state_27, input_state_22, input_state_23)
		
		if input_state_17 == True and input_state_27 == False and input_state_22 == False and input_state_23 == False:
			#Interruptor 1 pressed, Loading BCN3D+ firmware
			print "Loading BCN3D Plus Firmware"
			loadFirmware(BCN3DPlusPath)				
						   
		if input_state_17 == False and input_state_27 == True and input_state_22 == False and input_state_23 == False:
			#Interruptor 2 pressed, Loading BCN3DR firmware+
			print "Loading BCN3DR Firmware"
			loadFirmware(BCN3DRPath)

		if input_state_17 == False and input_state_27 == False and input_state_22 == True and input_state_23 == False:
			#Interruptor 3 pressed, Loading BCN3DSigma firmware
			print "Loading BCN3D Sigma Firmware"
			loadFirmware(BCN3DSigmaPath)
													
		#If switches 1,2,3 are selected and the load button pressed --> REBOOT
		if input_state_17 == True and input_state_27 == True and input_state_22 == True and input_state_23 == False:
			print 'Rebooting...'
			startUpLEDS()
			os.system("sudo reboot")
		#If switches 1,2,4 are selected and the load button pressed --> SHUTDOWN
		if input_state_17 == True and input_state_27 == True and input_state_22 == False and input_state_23 == True:
			print 'Powering off the system...'
			startUpLEDS()
			os.system("sudo poweroff")
			
	except KeyboardInterrupt:
		print "program closed by user"
		GPIO.cleanup()
		sys.exit()
	except:
		print "Other error or exception ocurred!"
		GPIO.cleanup()
		sys.exit()  
	
    
#Main program
def main():
	syncGithub()
	manageInputs()
	startUpLEDS()
	comPortsInfo()
	#Callback function in PIN 24. Whenever a Falling Edge is detected, run the checkButtons Function
	GPIO.add_event_detect(24, GPIO.FALLING, callback=checkButtons, bouncetime=300)  
	while True:
		time.sleep(0.1)
		#print (colored.green("Waiting for the load button..."))                                     
		
#Just the regular boilerplate to start the program
if __name__ == '__main__':
	print "Starting the Electronics Auto Loader...!"
	main()
