import RPi.GPIO as GPIO
import math
import os
from datetime import datetime
from time import sleep

# This is for revision 1 of the Raspberry Pi, Model B
# This pin is also referred to as GPIO23
INPUT_WIRE = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_WIRE, GPIO.IN)
print("READY to start")
while True:
	value = 1
	# Loop until we read a 0
	while value:
		#print("while 01")
		value = GPIO.input(INPUT_WIRE)

	# Grab the start time of the command
	startTime = datetime.now()

	# Used to buffer the command pulses
	command = []

	# The end of the "command" happens when we read more than
	# a certain number of 1s (1 is off for my IR receiver)
	numOnes = 0

	# Used to keep track of transitions from 1 to 0
	previousVal = 0

	while True:
		#print("value= " + str(value) + " ::::: prevalue= " + str(previousVal))
		if value != previousVal:
			# The value has changed, so calculate the length of this run
			now = datetime.now()
			pulseLength = now - startTime
			startTime = now

			command.append((previousVal, pulseLength.microseconds))

		if value:
			numOnes = numOnes + 1
		else:
			numOnes = 0

		# 10000 is arbitrary, adjust as necessary
		if numOnes > 4000:
			break

		previousVal = value
		value = GPIO.input(INPUT_WIRE)
	print("outwhile")
	print ("----------Start----------")
	for (val, pulse) in command:
		print (val, pulse)
		print("    ")

	print ("-----------End-----------\n")
	print (command)
	print ("Size of array is " + str(len(command)))
