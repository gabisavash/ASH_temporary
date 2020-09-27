import RPi.GPIO as GPIO
import math
import os
from datetime import datetime
from time import sleep
limitbool = 1000 ### este a cea valoare care decide ce tip de boolean este elementul din lista de IR_receive in functie de al doilea element din tuple 
commandlenghtsend = 0 ### initializare variabila, ulterior in run o sa declaram lungimea comenzi de la IR_Remote pentru a folosi lungimea corecta

INPUT_WIRE = 9

GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_WIRE, GPIO.IN)

IR_REMOTE_name = input("Please insert the name type of IR_REMOTE (EX: AC_Panasonic01): ")
IR_REMOTE_descrition = input("INSERT IR remote description: ")
IR_REMOTE_file = "/home/pi/FLASK_PCB/TEST/IR_REMOTE_config/"+str(IR_REMOTE_name) + ".py"
print("\n01The config file for IR REMOTE will be saved in:  ---- " + str(IR_REMOTE_file))

f = open(IR_REMOTE_file, "a")
f.write(IR_REMOTE_descrition)
f.close()
#print(IR_REMOTE_file)
print("\n02READY to start")
while True:
	value = 1

	while value:
		value = GPIO.input(INPUT_WIRE)
	startTime = datetime.now()
	command = []
	numOnes = 0
	previousVal = 0

	while True:
		if value != previousVal:
			now = datetime.now()
			pulseLength = now - startTime
			startTime = now

			command.append((previousVal, pulseLength.microseconds))

		if value:
			numOnes = numOnes + 1
		else:
			numOnes = 0
		if numOnes > 12000:
			break

		previousVal = value
		value = GPIO.input(INPUT_WIRE)
	if len(command) >= 12:
		for i in range(11):
			print(command[i])
	print ("03Size of array is " + str(len(command)))
	command_name = input("DID YOU WANT TO SAVE (YES -> insert the command name) (NO -> only ppress ENTER): ")
	if commandlenghtsend == 0:
		print("04*********** FIRST SAVE THE PARAMETERS ***********")
		print(command)
		print("05Size of array is " + str(len(command)))
		paramOK = input("For parameters NOK only press ENTER or insert any letter for save ")
		if len(paramOK) != 0:
			command_name0 = input("insert lenght of pulse0 as       EX: pulse0 = 9000    :")
			f = open(IR_REMOTE_file,"a")
			content_to_save = "\n\n" + str(command_name0) 
			f.write(content_to_save)
			f.close()
			command_name0 = input("insert lenght of pulse1 as       EX: pulse1 = 4500    :")
			f = open(IR_REMOTE_file,"a")
			content_to_save = "\n" + str(command_name0) 
			f.write(content_to_save)
			f.close()
			command_name0 = input("insert lenght of short_time as       EX: short_time = 560     :")
			f = open(IR_REMOTE_file,"a")
			content_to_save = "\n" + str(command_name0) 
			f.write(content_to_save)
			f.close()
			command_name0 = input("insert lenght of long_time as       EX: long_time = 1680    :")
			f = open(IR_REMOTE_file,"a")
			content_to_save = "\n" + str(command_name0) + "\n"
			f.write(content_to_save)
			f.close()
			commandlenghtsend = len(command)
			print("06THE command lenght is: "+str(commandlenghtsend) )
            
			print("\n\n07------OK Parameters saved READY TO READ------")			
		else:
			print("\n\n08------READY TO RE_READ------")			
	else: 
		if len(command) == commandlenghtsend:
			if len(command_name) != 0:
				command_list = []
				command_to_list = command[2:]
				for i in command_to_list:
					if i[0] == 1 and i[1] >= limitbool:
						command_list.append(1)
					elif i[0] == 1 and i[1] <= limitbool:
						command_list.append(0)
				f = open(IR_REMOTE_file,"a")
				content_to_save = "\n" + str(command_name) + " = " + str(command_list)
				f.write(content_to_save)
				f.close()
				print("\n\n09-----READY TO RE_READ------")
			else:
				print("\n\n10------READY TO RE_READ------")
		else:
			if len(command_name) != 0:
				print("\n11ERROR ERROR ERROR ---- lenght of command is incorect can't save the command ---- ERROR ERROR ERROR\n")
				print("-----READY TO RE_READ------")
			else:
				print("\n12ERROR ERROR ERROR ---- lenght of command is incorect can't save the command ---- ERROR ERROR ERROR\n")
				print("-----READY TO RE_READ------")
