#  need auxiliar library instal to run
#  Adafruit_DHT
#  timerlib77    #this one is must be in the same directory with main script
#  flask_cors

from collections import defaultdict
import RPi.GPIO as GPIO
import time
import dht11  ### DHT11
import Adafruit_DHT  ### DHT22
import threading
#import _thread
import timerlib77 ####
from flask import Flask, request, jsonify
#from flask_cors import CORS  #CORS - .net 1/2
from datetime import datetime
import requests
import json



from ASHdict import smart_home_elements , FLASK_adress

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()


json_to_server = {"lights" : [] , "heating" : [] , "watertemp" : [], "gardenzones" : {"1":1} }
json_from_server = defaultdict(dict)

json_from_server["secure"] = 0
json_from_server["dimineata"] = 6
json_from_server["seara"] = 8
json_from_server["timePIR"] = 10
#json_from_server["bypassgarden"] = 0
json_to_server["dtsis"] = "01:00"
#json_from_server["floorkeepwarm"] = 0

dict_zones_garden = {"1":1}  ; counter_zones_garden = {} ; time_start_zones_garden = {} ; timeON_zones_garden = {} ; actual_humi_zones_garden = {} ; min_humi_zones_garden = {} ; max_humi_zones_garden = {} #### dicts for garden
counter_soilmoisture_elements = 0
counter_watertemp_elements = 0
counter_lights_elements = 0
counter_heating_elements = 0

counter_soilactuator_elements = 0
heatgenn = 0
soil_elements_list = []  ###################____________soil list
####################################################################
                    ### INIT CLASS  ###                           ##
                                                                  ##
class initinputs:                                                 ##
    def __init__(self, name ):                                    ##
        self.name = name                                          ##  
                                                                  ##  
    def inputs_init(self):                                        ##  
        if (self.input_type ==  "outsimple"):
            GPIO.setup(self.GPIO_alocated,GPIO.OUT)
        elif (self.input_type ==  "pull_no"):
            GPIO.setup(self.GPIO_alocated, GPIO.IN) 
        elif(self.input_type ==  "pull_down"): 
            GPIO.setup( self.GPIO_alocated , GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
        elif(self.input_type ==  "pull_up"):
            GPIO.setup( self.GPIO_alocated , GPIO.IN , pull_up_down=GPIO.PUD_UP)
        elif(self.input_type ==  "DHT11_local"):
            pass
        elif(self.input_type ==  "DHT22"):
            DHT_PIN = self.GPIO_alocated
        elif(self.input_type == "PIR"):
            GPIO.setup(self.GPIO_alocated, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        elif(self.input_type == "DS18B20"):
            pass
        elif(self.input_type == "sht_i2c"):
            pass
        elif(self.input_type =="DC_curtain"):
            GPIO.setup( self.GPIO_enc_A , GPIO.IN , pull_up_down=GPIO.PUD_UP)
            GPIO.setup( self.GPIO_enc_B , GPIO.IN , pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.GPIO_motor_pin_1,GPIO.OUT)
            GPIO.setup(self.GPIO_motor_pin_2,GPIO.OUT)
            if (self.GPIO_speed != "none"):
                GPIO.setup(self.self.GPIO_speed,GPIO.OUT)
        else:
            print("Wrong declaretion of instance..... can not assign the GPIO Pin" + self)

    def create_thread(self):                                    ##
        t_button =threading.Thread(target = buttontrigger, name = "button_Threading",  args = (myinput[self.name].GPIO_alocated, myinput[self.name].linked_output_name))
        t_button.start()

    def temp_adafruit_thread(self):                                    ##
        t_temperatureAda =threading.Thread(target = temp_dht_adafruit, name = "Temperature_adafruit_Threading",  args = (myinput[self.name].GPIO_alocated, ))
        t_temperatureAda.start()
    def temp11_thread(self):                                    ##
        try:
            t_temperature11 =threading.Thread(target = temp_dht11, name = "Temperature_dht11_Threading")
            t_temperature11.start()
        except Exception as e:
            print(e)
            raise

    def pir_thread(self):                                    ##
        
        t_PIR =threading.Thread(target = PIR1trigger, name = "PIR_Threading",  args = (myinput[self.name].GPIO_alocated, myinput[self.name].linked_output_name))
        t_PIR.start()
        print("I working here")

    def add_light_endpoints(self):     
        global counter_lights_elements 
        light_url = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/" + "light" +  "/" + str(counter_lights_elements) + "/" + str(myinput[self.name].GPIO_alocated)
        state_bec = GPIO.input(myinput[self.name].GPIO_alocated) 
        json_to_server["lights"].append({ "state" : state_bec , "url" : light_url})                                           ##
        setattr(myinput[self.name], "indexnumber", counter_lights_elements)
        counter_lights_elements += 1 
        return(self)                                              ##

    def add_heat_generator(self):   
        global counter_heating_elements
        global heatgenn
        heat_url = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/" + "heat" + "/" + str(counter_heating_elements) + "/" + str(myinput[self.name].GPIO_alocated)
        state_heat_gen = GPIO.input(myinput[self.name].GPIO_alocated) 
        json_to_server["heating"].append({ "state" : state_heat_gen , "url_gen" : heat_url})
        json_from_server[self.name]["indexnumber"] = counter_heating_elements
        setattr(self, "indexnumber", counter_heating_elements)
        counter_heating_elements += 1
        #json_from_server["bypassheat"] = 0
        #json_from_server["manualheat"] = 0
        json_from_server["manualheatingTimeON"] = 60
        json_from_server[self.name]["GPIO"] = self.GPIO_alocated
        if (heatgenn == 0):
            json_from_server["heatmode"] = 1       ### heatmode 1=auto full, 2=auto floor, 3 = manual ,else = bypass
            json_to_server["heatmode"] = 1
            t_heatgen =threading.Thread(target = autoheat, name = "Heating_auto_Threading")
            t_heatgen.start()
        heatgenn += 1
        return(self) 								  ##

    def water_temp(self):
        global counter_watertemp_elements
        json_to_server["watertemp"].append({"pozitie" : self.pozitie,})  
        setattr(self, "indexnumber", counter_watertemp_elements)
        counter_watertemp_elements += 1
        return(self)


    def add_heat_actuator(self):                                      ##  
        global counter_heating_elements
        heat_url = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/" + "heat" + "/" + str(counter_heating_elements) + "/" + str(myinput[self.name].GPIO_alocated)
        heat_url_page = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/" + "heat" + "/" + str(counter_heating_elements) + "/" + str(myinput[self.name].GPIO_alocated)

        state_heat_act = GPIO.input(myinput[self.name].GPIO_alocated)
        json_to_server["heating"].append({ "state" : state_heat_act , "url" : heat_url , "room_url" : self.temp_url})
        json_from_server[self.name]["temp_url"] = self.temp_url
        #json_from_server[self.name]["GPIO"] = self.GPIO_alocated
        mystring = self.name
        myindex = int(mystring.replace('heatactuator', ''))

        json_from_server[self.name]["actuatorIndex"] = myindex
        json_from_server[self.name]["indexnumber"] = counter_heating_elements
        setattr(self, "indexnumber", counter_heating_elements)
        #setattr(myinput[self.name], "indexnumber", counter_heating_elements)						##
        
        #json_from_server[self.name].update({"Days":[{"name":"Mon","Intervals":[{"hour":"05","temp": "30"}],"name":"Tue","Intervals":[{"hour":"05","temp": "30"}],"name":"Wed","Intervals":[{"hour":"05","temp": "30"}],"name":"Thu","Intervals":[{"hour":"05","temp": "30"}],"name":"Fri","Intervals":[{"hour":"05","temp": "30"}],"name":"Sat","Intervals":[{"hour":"05","temp": "30"}],"name":"Sun","Intervals":[{"hour":"05","temp": "30"}],"name":"Mon","Intervals":[{"hour":"05","temp": "30"}]}]})
        json_from_server[self.name].update({"Days":[{"name":"Mon","Intervals":[{"hour":"05","temp": "30"}]}]})
        json_from_server[self.name]["Days"].append({"name":"Tue","Intervals":[{"hour":"05","temp": "30"}]})
        json_from_server[self.name]["Days"].append({"name":"Wed","Intervals":[{"hour":"05","temp": "30"}]})
        json_from_server[self.name]["Days"].append({"name":"Thu","Intervals":[{"hour":"05","temp": "30"}]})
        json_from_server[self.name]["Days"].append({"name":"Fri","Intervals":[{"hour":"05","temp": "30"}]})
        json_from_server[self.name]["Days"].append({"name":"Sat","Intervals":[{"hour":"05","temp": "30"}]})
        json_from_server[self.name]["Days"].append({"name":"Sun","Intervals":[{"hour":"05","temp": "30"}]})

        counter_heating_elements += 1
        json_from_server[self.name]["temp_set_point"] = 30
        json_from_server[self.name]["hysterezis"] = 1
        json_from_server[self.name]["roomtemp"] = 100
        json_from_server[self.name]["bypassactuator"] = 0
        return(self) 		


    def create_soil_zones(self):
        global counter_soilactuator_elements
        global soil_elements_list
        global dict_zones_garden
        add_act_dict_zone = 0
        add_to_dict = 0
        if (counter_soilactuator_elements == 0):
            from pi_sht1x import SHT1x
            json_from_server["gardenmode"] = 1  ### gardenmode: 1 = automat, 2 = manual, else bypass
            json_to_server["gardenmode"] = 1
            json_from_server["mangardactmaxtime"] = 60
            json_from_server["manualgardenTimeON"] = 400
            t_soil =threading.Thread(target = auto_garden, name = "Garden_care")
            t_soil.start()
            #dict_zones_garden = {}           
        if ("soil_actuator" in myinput[self.name].name):   #creaza json_to_server ACTUATOR
            soil_elements_list.append(myinput[self.name].name)        
            soil_url = 0
        if ("soil_actuator" in  myinput[self.name].name):
            for k0,v0 in json_to_server.items():
                if (k0 == "gardenzones"):
                    for k,v in v0.items():
                        if (k ==  myinput[self.name].pozitie  ):
                            add_to_dict = 3
                        elif(add_to_dict != 3) :
                            add_to_dict = 4	    
        elif ("soil_read" in myinput[self.name].name):    #creaza json_to_server READ(sensor)
            for k0,v0 in json_to_server.items():
                if (k0 == "gardenzones"):
                    for k,v in v0.items():
                        if (k ==  myinput[self.name].pozitie  ):
                            add_to_dict = 1
                        elif(add_to_dict != 1) :
                            add_to_dict = 2	 
        #print(myinput[self.name].name)
        #print(k)
        mystring = myinput[self.name].pozitie
        myindex = int(mystring.replace('zone', ''))
        if (k == "1" ):
            del json_to_server["gardenzones"][k]
        if (add_to_dict == 1): ## append soil_read element 
            json_to_server["gardenzones"][myinput[self.name].pozitie].append({"temperature" : 100 , "humidity" : 100,"name": myinput[self.name].name})
            json_from_server[myinput[self.name].pozitie]["schedules"][0].update({"hour" : "05","ONtime":"20", "minhumi": "10", "maxhumi": "90"})
            json_from_server[myinput[self.name].pozitie].update({"hasSensor" : 1,"zoneIndex" : myindex, "bypasszone" : 1})
            json_from_server[myinput[self.name].pozitie]["schedules"].append({"hour" : "14","ONtime":"17", "minhumi": "90", "maxhumi": "90"})   ### PT TEST
        if (add_to_dict == 2): ## create new soil_read[+zone] element 
            counter_zones_garden.update({myinput[self.name].pozitie : 0})
            json_to_server["gardenzones"][myinput[self.name].pozitie] = [{"temperature" : 100 , "humidity" : 100,"name": myinput[self.name].name}]
            json_from_server[myinput[self.name].pozitie]["schedules"] = [{"hour" : "05","ONtime":"30", "minhumi": "10", "maxhumi": "90"}]
            json_from_server[myinput[self.name].pozitie].update({"hasSensor" : 1,"zoneIndex" : myindex, "bypasszone" : 1})
            ###
            json_from_server[myinput[self.name].pozitie]["schedules"].append({"hour" : "14","ONtime":"17", "minhumi": "90", "maxhumi": "90"})   ### PT TEST
        if (add_to_dict == 3): ## append soil_actuator element
            #aici de pus GPIO in LOW
            json_to_server["gardenzones"][myinput[self.name].pozitie].append({"state":0,"url":soil_url,"name": myinput[self.name].name})
            ind_is = json_to_server["gardenzones"][myinput[self.name].pozitie].index({"state":0,"url":soil_url,"name": myinput[self.name].name})
            #print("333iiiiiiiiiii====" + str(ind_is))
            soil_url = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/"  + str(myinput[self.name].pozitie) + "/" + str(ind_is) + "/" + str(myinput[self.name].GPIO_alocated)
            json_to_server["gardenzones"][myinput[self.name].pozitie][ind_is].update ({"bypassactuator": 0,"state": 0 , "url":soil_url,"name": myinput[self.name].name})
        if (add_to_dict == 4): ## create new soil_actuator[+zone] element 
            #aici de pus GPIO in LOW
            counter_zones_garden.update({myinput[self.name].pozitie : 0})
            json_to_server["gardenzones"][myinput[self.name].pozitie] = [{"state": 0 , "url":soil_url,"name": myinput[self.name].name}]
            json_from_server[myinput[self.name].pozitie]["schedules"] = [{"hour" : "14","ONtime":"10", }]
            json_from_server[myinput[self.name].pozitie].update({"hasSensor" : 0, "zoneIndex" : myindex, "bypasszone" : 0})

            #for i in json_from_server[myinput[self.name].pozitie]:
                #for k,v in i.items 
                #if json_from_server
                    #json_from_server[myinput[self.name].pozitie].append({"hasSensor" : 0})
            ind_is = json_to_server["gardenzones"][myinput[self.name].pozitie].index({"state":0,"url":soil_url,"name": myinput[self.name].name})
            #print("444iiiiiiiiiii====" + str(ind_is))
            soil_url = "/" + str(FLASK_adress["DEVipadress"]) + ":" + str(FLASK_adress["DEVipport"]) + "/"  + str(myinput[self.name].pozitie) + "/" + str(ind_is) + "/" + str(myinput[self.name].GPIO_alocated)
            json_to_server["gardenzones"][myinput[self.name].pozitie][ind_is].update ({"bypassactuator": 0,"state": 0 , "url":soil_url,"name": myinput[self.name].name})
        #print(add_to_dict)
        if ("soil_actuator" in  myinput[self.name].name):
            for z_k,z_v in dict_zones_garden.items():
                #print("IN____IN-------IN______IN" + str(z_k) + "---" +str(myinput[self.name].pozitie))
                if (z_k == myinput[self.name].pozitie) :
                    add_z_act = {ind_is:myinput[self.name].GPIO_alocated}
                    add_act_dict_zone = 1
                elif(z_k != myinput[self.name].pozitie and add_act_dict_zone == 0) :
                    add_z_zone = {myinput[self.name].pozitie:{ind_is:myinput[self.name].GPIO_alocated} } 
                    add_act_dict_zone = 2
            #print(add_act_dict_zone)
                #print(z_k)
            #print(dict_zones_garden)
            if (add_act_dict_zone == 1):
                dict_zones_garden[myinput[self.name].pozitie].update(add_z_act)                
            if (add_act_dict_zone == 2):
                dict_zones_garden.update(add_z_zone)
        counter_soilactuator_elements += 1
        time.sleep(1)
        return(self)     

    def curtain_call(self):
        t_curtain_encoder =threading.Thread(target = encoder_read, name = "Encoder_read_Threading")
        t_curtain_encoder.start()

        t_curtain_motor =threading.Thread(target = motor_control, name = "motor_control_Threading")
        t_curtain_motor.start()        
     
##----------------------------------------------------------------##



    
##################################################################################
                    ### LOOP THROW smart_home_elements ###              	##
		      ## to transform dict to OBJECT ##				##
										##    
for i_key, i_value in smart_home_elements.items():                              ##  FIRST for loop to generate the CLASS OBJECTS                            
    myinput = {name: initinputs(name=name) for name in smart_home_elements}     ##  that create a main objects called myinput which containt the OBJECTS from dict
										##    
for i_key, i_value in smart_home_elements.items():                              ##  SECOND for loop to add the attributes for each object from dict
    for key in i_value:                                                 	##  
        setattr(myinput[i_key], key, i_value[key])                     		##
										##    
for i_key, i_value in smart_home_elements.items():                              ##  THIRD for loop to initiate the OBJECTs hardware GPIO 
    myinput[i_key].inputs_init()    						##  
										##
##------------------------------------------------------------------------------##


###################### Curtain ##############################

def encoder_read():
    outcome = [0,-1,1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]
    last_AB = 0b00 
    #global counter = 0  ### introdus in ASH_dict+ arg func
    while True:
        A = GPIO.input(A_pin) ### A_pin introdus in ASH_dict+ arg func
        B = GPIO.input(B_pin) ### B_pin introdus in ASH_dict+ arg func
        current_AB = (A << 1) | B
        position = (last_AB << 2) | current_AB
        counter += outcome[position]
        last_AB = current_AB
        #print(counter)

def motor_control():
    time.sleep(1)
    global counter ### introdus in ASH_dict+ arg func
    while True:
        if counter <= 10:
            GPIO.output(pin2out, GPIO.LOW) ### pin2out introdus in ASH_dict+ arg func
            time.sleep(0.5)
            GPIO.output(pin1out, GPIO.HIGH) ### pin1out introdus in ASH_dict+ arg func
        if counter >= 2500:
            GPIO.output(pin1out, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(pin2out, GPIO.HIGH)
            
##------------------------------------------------------------------------------##


###################### INCALZIRE AUTOMAT ##############################


def autoheat():

    start_ct = time.time()
    json_from_server["autoheattime"] = 1
    json_to_server["temperature"] = 22
    man_ON_counter = 0
    #man_ON_actuators = 0
    print(".....AUTO HEAT SYSTEM..... ON")
    time.sleep(50)
    
    while True:
        time.sleep(10)
        json_to_server["heatmode"] = json_from_server["heatmode"] 
        auto_heat_time = int(json_from_server["autoheattime"]) 
        if (int(json_from_server["heatmode"]) == 1 or int(json_from_server["heatmode"]) == 2): ###
            if(int(json_from_server["heatmode"]) == 1):
                stop_ct = time.time()
                restart_timer , pasted_or_not = timerlib77.timer_min(auto_heat_time, start_ct, stop_ct)  # arg 1 set sec for read temp
                start_ct = restart_timer
                if pasted_or_not:
                    read_watersensor()		
                    heat_act_state = heat_act_elem()
                    print("OUT............OUT.....")
                    action_heat(heat_act_state)
            elif(int(json_from_server["heatmode"]) == 2): #floor
                    floor_temp = 0
                    for i in myinput:
                        if ("water_temp" in i):
                            if (myinput[i].pozitie == "floortemp" ):
                                floor_temp = 1
                                stop_ct = time.time() #floor
                                restart_timer , pasted_or_not = timerlib77.timer_min(auto_heat_time, start_ct, stop_ct)  # arg 1 set sec for read temp   #floor
                                start_ct = restart_timer #floor
                                if pasted_or_not: #floor
                                    read_watersensor() #floor
                                    heat_act_state = heat_act_elem_floor_temp() #floor
                                    action_heat(heat_act_state) #floor
                    if (floor_temp == 0):
                        #print(json_from_server["heatmode"])
                        json_from_server["heatmode"] = 1
                        #print(json_from_server["heatmode"])
        elif (int(json_from_server["heatmode"]) == 3): ### 
            print("heating manual")
            #time.sleep(10)
            for ii in myinput:
                if ("heatactuator" in ii):
                    print(ii)
                    if(GPIO.input(myinput[ii].GPIO_alocated) != 0):
                        if (man_ON_counter == 0):
                            man_ON_counter = 1
                            start_ctman = time.time()
                        stop_ctman = time.time()
                        restart_timer , pasted_or_not = timerlib77.timer_sec(float(json_from_server["manualheatingTimeON"]), start_ctman, stop_ctman)  # arg 1 set sec for read temp
                        start_ctman = restart_timer
                        print(str(stop_ctman) + "  >>>>>> " + str(start_ctman))
                        if pasted_or_not:
                            for i in myinput:
                                if ("heatactuator" in i):
                                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                                if ("heatgenerator" in i):
                                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                            man_ON_counter = 0
                if ("heatgenerator" in ii):
                    print(ii)
                    if(GPIO.input(myinput[ii].GPIO_alocated) != 0):
                        #if (man_ON_counter == 0):
                            #man_ON_counter = 1
                            #start_ctman = time.time()
                        #stop_ctman = time.time()
                        #restart_timer , pasted_or_not = timerlib77.timer_sec(float(json_from_server["manualheatingTimeON"]), start_ctman, stop_ctman)  # arg 1 set sec for read temp
                        #start_ctman = restart_timer
                        #print(str(stop_ctman) + "  >>>>>> " + str(start_ctman))
                        #if pasted_or_not:
                            #for i in myinput:
                                #if ("heatactuator" in i):
                                    #GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    #json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                                #if ("heatgenerator" in i):
                                    #GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    #json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                        man_ON_actuators = 0
                        for myi in myinput:
                            if ("heatactuator" in myi):
                                if (GPIO.input(myinput[myi].GPIO_alocated) == 1):
                                    man_ON_actuators += 1
                        if (man_ON_actuators == 0):
                            for i in myinput:
                                if ("heatactuator" in i):
                                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                                if ("heatgenerator" in i):
                                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                            man_ON_counter = 0
                        

                                
        else:
            #off everything
            print("Heating OFF")
            for i in myinput:
                if ("heatactuator" in i):
                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
                if ("heatgenerator" in i):
                    GPIO.output(myinput[i].GPIO_alocated , GPIO.LOW)
                    json_to_server["heating"][myinput[i].indexnumber]["state"] = GPIO.input(myinput[i].GPIO_alocated)
            time.sleep(20)

def read_watersensor():  # read water temp sensor
    for i in myinput:
        if ("water_temp" in i):
            print("water_sensor..............................................")
            json_to_server["watertemp"][myinput[i].indexnumber]["temperature"] = read_water_temp(myinput[i].path_1wire)    

def floor_temp():  # read water temp sensor
    for i in myinput:
        if ("water_temp" in i):
            if (myinput[i].pozitie == "floortemp" ):
                json_to_server["watertemp"][myinput[i].indexnumber]["temperature"] = read_water_temp(myinput[i].path_1wire) 
            return(json_to_server["watertemp"][myinput[i].indexnumber]["temperature"]) 

def heat_act_elem():   # ON/OFF actuator heat
    heat_act_list = []
    for i in myinput:
        if ("heatactuator" in i):
            if (int(json_from_server[i]["bypassactuator"]) == 1):
                ONheat(myinput[i].GPIO_alocated,  i, myinput[i].indexnumber )
            else:    
                reqtemp(myinput[i].temp_url, i)
                ONheat(myinput[i].GPIO_alocated,  i, myinput[i].indexnumber )
            if (GPIO.input(myinput[i].GPIO_alocated) == 1):
                heat_act_list.append(myinput[i])
    return heat_act_list

def heat_act_elem_floor_temp():  #floor
    heat_act_list = []   #floor
    for i in myinput:    #floor
        if ("heatactuator" in i):
            json_from_server[i]["roomtemp"] = floor_temp()
            ONheat(myinput[i].GPIO_alocated,  i, myinput[i].indexnumber )
            if (GPIO.input(myinput[i].GPIO_alocated) == 1):
                heat_act_list.append(myinput[i]) 		
    return heat_act_list		
		
		
def action_heat(heat_aact_state): # ON/OFF generator heat
    for ii_key, ii_value in json_from_server.items():
        if("heatgenerator" in ii_key):
            for kkey, vvalue in ii_value.items():
                generator_kk = ii_key
                if (kkey == "GPIO"):
                    GPIO_vv = vvalue
                elif(kkey == "indexnumber"):
                    index_vv = vvalue
            print("HERE HRE HERE" + str(heat_aact_state))
            if (len(heat_aact_state) > 0):
                GPIO.output(GPIO_vv , GPIO.HIGH)
                json_to_server["heating"][index_vv]["state"] = GPIO.input(GPIO_vv)
            else:
                GPIO.output(GPIO_vv, GPIO.LOW)
                json_to_server["heating"][index_vv]["state"] = GPIO.input(GPIO_vv)	

def ONheat(out,  maindictkey, index_num):   # ON/OFF heat generator
    if (int(json_from_server[maindictkey]["bypassactuator"]) == 1):
        GPIO.output(out, GPIO.LOW)
        json_to_server["heating"][index_num]["state"] = GPIO.input(out)
    else:        
        set_temp1 = mytempget(maindictkey)
        temp = float(json_from_server[maindictkey]["roomtemp"])
        json_from_server[maindictkey]["temp_set_point"] = set_temp1
        mintemp = float(set_temp1) - float(json_from_server[maindictkey]["hysterezis"])
        maxtemp = float(set_temp1) + float(json_from_server[maindictkey]["hysterezis"])
        if (temp >= 100):					#in case of no temp received from rooms
            temp = float(json_to_server["temperature"])	# work with backup sensor from this plate
            json_from_server[maindictkey]["roomtemp"] = temp
            json_from_server[maindictkey]["badtemprequest"] = 1
        else:
            json_from_server[maindictkey]["badtemprequest"] = 0
        if (int(json_from_server["heatmode"]) == 1 or int(json_from_server["heatmode"]) == 2 or int(json_from_server["heatmode"]) == 3):
            if (temp < mintemp):
                GPIO.output(out, GPIO.HIGH)
                json_to_server["heating"][index_num]["state"] = GPIO.input(out)
            elif (temp > maxtemp):
                GPIO.output(out, GPIO.LOW)
                json_to_server["heating"][index_num]["state"] = GPIO.input(out)
	
	
def reqtemp(req_adress, maindictkey):   #request temp from a External Device
	print(req_adress)
	try:
                response = requests.get(req_adress)
                print("IN TRY" + str(req_adress) + "and is " + str(response.status_code))
                if (int(response.status_code == 200)):		# good response
                        json_from_server[maindictkey]["roomtemp"] = response.text 
			#cameradata[dictkey] = response.text 
                        return int(response.status_code)
                else:		
                        json_from_server[maindictkey]["roomtemp"] = "1000" 								# 1000 not good response from room's devices
                        return int(response.status_code)
	except :
                json_from_server[maindictkey]["roomtemp"] = "3000"  										# 3000 can't access device ( flask off on room's devices) 
		

def mytempget(maindictkey):
    mylist=[]
    myhour=[]
    mytemp =[]
    dict_split_dtsis1 = json_to_server["dtsis"].split(':')
    actualhour = dict_split_dtsis1[0]
    for key, value in json_from_server.items():
        if(key == maindictkey):  ### main dict key       ### heatactuator1
            for kkey, vvalue in value.items():
                if (kkey == "Days"):  
                    for i in vvalue:
                        #print(i)
                        for kkkey, vvvalue in i.items():
                            if (vvvalue == json_to_server["wsis"]):
                                for kkkkey, vvvvalue in i.items():
                                    if( kkkkey == "Intervals"):
                                        for ii in vvvvalue:
                                            for key5, value5 in ii.items():
                                                if (key5 == "hour"):
                                                    if( int(actualhour) >= int(value5)):  
                                                        mylist.append(value5)
                                                        myhour.append(value5)
                                                if (key5 == "temp"):
                                                    mytemp.append(value5)
                                   
    if mylist:                                 
        mylist.sort(reverse = True)
        myindexis = myhour.index(mylist[0])
        mytempis = mytemp[myindexis]
    else:
        mytempis = json_from_server[maindictkey]["temp_set_point"]
    return mytempis

##---------------------------------------------------------------------------------##



###################### GARDEN AUTOMAT ##############################

def auto_garden():
    print(".....AUTO GARDEN ........ON")
    time.sleep(80)
    global time_start_zones_garden	
    last_wsis = json_to_server["wsis"]
    last_hour = 25
    man_ON_counter = 0
    start_ctman = time.time()
    while True:
        print("WHILE WORK")
        json_to_server["gardenmode"] = json_from_server["gardenmode"] 
        if(str(last_wsis) != str(json_to_server["wsis"])):
            for k,v in dict_zones_garden.items():
                if ("zone" in k):
                    counter_zones_garden[k] = 0	
            print("ZIUA SAPTAMANII modificata din: "+ str(last_wsis) +"  in  " +str(json_to_server["wsis"]) )
            last_wsis = json_to_server["wsis"]
        
        print(json_from_server["gardenmode"])
        dict_split_dtsis1 = json_to_server["dtsis"].split(':')
        actualhour = dict_split_dtsis1[0]
        if (int(last_hour) != int(actualhour)):
            getsoil_values()
            last_hour = actualhour
        #print("aici0")----------------------------------------------incepe automat mode
        if (int(json_from_server["gardenmode"]) == 1 ):
            for k,v in json_from_server.items():
                if ("zone" in k):   # k = zona
                    for kn00, vn00 in v.items():
                        if kn00 == "bypasszone":
                            if int(vn00) == 0: 
                                for kn0, vn0 in v.items():
                                    if kn0 == "schedules":
                                        
                                        for i in vn0:
                                            for kk,vv in i.items():
                                                if("hour" in kk):
                                                    if (vv == actualhour ):
                                                        elem_minhumi = 0
                                                        for kkh, vvh in i.items():
                                                            if("minhumi" in kkh):  ###aici verific daca am minhumi 
                                                                elem_minhumi += 1 ################################################## AM el minhumi
                                                            #print(i)
                                                                for kkk , vvv in i.items():
                                                                    if(kkk == "ONtime"):
                                                                        timeON_zones_garden[k] = vvv
                                                                    elif(kkk == "minhumi"):
                                                                        min_humi_zones_garden[k] = vvv
                                                                    elif(kkk == "maxhumi"):
                                                                        max_humi_zones_garden[k] = vvv
                                                                activare_soil_act_sensor(k)        
                                                        if(elem_minhumi == 0):
                                                            for kkk , vvv in i.items():
                                                                if(kkk == "ONtime"):
                                                                    timeON_zones_garden[k] = vvv
                                                            activare_soil_act_timer(k)
        elif(int(json_from_server["gardenmode"]) == 2 ):
            print("manual ON")
            for k,v in dict_zones_garden.items():
                if("zone" in k):
                    for kk,vv in v.items():
                        if (GPIO.input(vv) != 0):
                            #time.sleep(int(json_from_server["manualgardenTimeON"]) * 1)
                            if (man_ON_counter == 0):
                                man_ON_counter = 1
                                start_ctman = time.time()
                            stop_ctman = time.time()
                            restart_timer , pasted_or_not = timerlib77.timer_sec(float(json_from_server["manualgardenTimeON"]), start_ctman, stop_ctman)  # arg 1 set sec for read temp
                            start_ctman = restart_timer
                            print(str(stop_ctman) + "  >>>>>> " + str(start_ctman))
                            if pasted_or_not:
                                print("MAN PASTED____________")
                                for k_off,v_off in dict_zones_garden.items():
                                    if("zone" in k_off):
                                        for kk_off,vv_off in v_off.items():
                                            GPIO.output(vv_off , GPIO.LOW)
                                            json_to_server["gardenzones"][k_off][kk_off]["state"] = GPIO.input(vv_off)
                                man_ON_counter = 0
            #time.sleep(10)
        else:
            print("Garden bypass")
            for k,v in dict_zones_garden.items():
                if("zone" in k):
                    #print(str(v) + " IN " + str(k))
                    for kk,vv in v.items():
                        if (GPIO.input(vv) != 0):
                            for k_off,v_off in dict_zones_garden.items():
                                if("zone" in k_off):
                                    for kk_off,vv_off in v_off.items():
                                        GPIO.output(vv_off , GPIO.LOW)
                                        json_to_server["gardenzones"][k_off][kk_off]["state"] = GPIO.input(vv_off)
            #time.sleep(10)
        print("Atentie la ORA ==="+ str(actualhour) )
        if (int(json_from_server["gardenmode"]) == 1 ):
            oprire_soil_act_sensor(actualhour)
        time.sleep(10)	

def oprire_soil_act_sensor(actualhour):
    if (1 == 1):
        for k,v in dict_zones_garden.items():
            if ("zone" in k):
                for kk,vv in v.items():
                    if (GPIO.input(vv) == 1):
                        getsoil_values()
                        for kkk,vvv in json_from_server.items():
                            if (k == kkk):   # k = zona
                                for kn0, vn0 in vvv.items():
                                    if kn0 == "schedules":
                                        for i in vn0:
                                            for kk_k,vv_v in i.items():
                                                print("....10....")
                                                if("hour" in kk_k):
                                                    print("....20....")
                                                    if (1 == 1):
            
                                                        if ("maxhumi" in i):
                                                            print("....30....")
                                                            if(kkk == k):
                                                                print("....31....")
                 #                                               print("000000000 " + str(i))
                                                                ind_iss = json_from_server[k]["schedules"].index(i)
                                                                if (k in timeON_zones_garden):
                                                                    myONtime = timeON_zones_garden[k] #json_from_server[k][ind_iss]["ONtime"] 
                                                                    maxhumi = max_humi_zones_garden[k]
                                                                    actualhumi = actual_humi_zones_garden[k] 
                                                                else:
                                                                    myONtime = 0
                                                                    time_start_zones_garden[k] = 0
                                                                    maxhumi = 0
                                                                    actualhumi = 300
                                                                #maxhumi = max_humi_zones_garden[k]
                                                                #actualhumi = actual_humi_zones_garden[k]
                                                                stop_ct = time.time() #floor
                  #                                              print(stop_ct - float(time_start_zones_garden[k]))
                                                                restart_timer , pasted_or_not = timerlib77.timer_sec(float(myONtime),float(time_start_zones_garden[k]) , stop_ct)  
                                                                if (pasted_or_not or actualhumi >= int(maxhumi) and actualhumi != 1000): #floor
                                                                    print(pasted_or_not)
                    #                                                print("0000000 ACTUAL = " + str(actualhumi) + "  max:  "+str(maxhumi))							    
                                                                    for kkkk,vvvv in dict_zones_garden.items():
                                                                        if (kkkk == k):
                                                                            for k_index , v_gpio in vvvv.items():
                                                                                print("INNNN")
                                                                                GPIO.output(v_gpio, GPIO.LOW)
                                                                                json_to_server["gardenzones"][k][k_index]["state"] = GPIO.input(v_gpio)
                                                        else:
                                                            print("....40....")
                                                            ind_iss = json_from_server[k]["schedules"].index(i)
                                                            stop_ct = time.time()
                                                            if (k in timeON_zones_garden):
                                                                myONtime = timeON_zones_garden[k] #json_from_server[k][ind_iss]["ONtime"]  
                                                            else:
                                                                myONtime = 0
                                                                time_start_zones_garden[k] = 0
                                    #actualhumi = actual_humi_zones_garden[k]
         #floor
                                                            restart_timer , pasted_or_not = timerlib77.timer_sec(float(myONtime),float(time_start_zones_garden[k]) , stop_ct) 
                                                            print(pasted_or_not)
                                                            print(str(time_start_zones_garden[k]) + "  " +str(stop_ct) + "   " +str(myONtime)) 
                                                            if pasted_or_not : #floor
                                                                for kkkk,vvvv in dict_zones_garden.items():
                                                                        #print()
                                                                    if (kkkk == k):
                                                                        for k_index , v_gpio in vvvv.items():
                                                                            GPIO.output(v_gpio, GPIO.LOW)
                                                                            json_to_server["gardenzones"][k][k_index]["state"] = GPIO.input(v_gpio)
        

def activare_soil_act_sensor(k): # k
    print("FUNCTION SENSOR pe ::: " + str(k))
    global time_start_zones_garden
    for k0,v0 in json_to_server.items():
        if (k0 == "gardenzones"):    
            for kka, vva in v0.items():   #itereaza prin json_to_server   ######## creaza lista actuatori
                if (k in kka):   # daca a gasit zona itereaza prin ea
                    lista_zona_GPIO = [] ; lista_zona_index = []
                    for ia in vva:  # itereaza elem de tip lista prin zona
                        for kkka,vvva in ia.items():  # itereaza prin lista
                            if ("soil_actuator" in str(vvva)): # daca gaseste actuator
           #             print(str(kkka) + "::::1::::"  + str(vvva))
                                lista_zona_GPIO.append(myinput[vvva].GPIO_alocated) ### creaza lista cu pini actuatoarelor
                                lista_zona_index.append(ia)
         #   print("IIIIII" + str(lista_zona_GPIO))
                    if (len(lista_zona_GPIO) > 0 and int(counter_zones_garden[k]) == 0 and int(actual_humi_zones_garden[k]) < int(min_humi_zones_garden[k]) and int(actual_humi_zones_garden[k]) != 1000):  ### verifica daca am element in lista
                        start_ct = time.time()
                        time_start_zones_garden[k] = start_ct
                        counter_zones_garden[k] += 1
                        for il in lista_zona_GPIO:   ### itereaza in lista
          #          print("GPIO aprins= " + str(il) + " din lista = " + str(lista_zona_GPIO))
                            il_index = lista_zona_GPIO.index(il)
                            elem_zone = lista_zona_index[il_index]
                            elem_zone_index = vva.index(elem_zone)
           #         print("before >>> " + str(json_to_server[k][elem_zone_index]["state"]) )
                            GPIO.output(il , GPIO.HIGH) 
                            json_to_server["gardenzones"][k][elem_zone_index]["state"] = GPIO.input(il)
                    elif (int(actual_humi_zones_garden[k]) == 1000):
                        activare_soil_act_timer(k)
                                #"timer"+str(k) = time.time()
                                #print("timer"+str(k))                                

def activare_soil_act_timer(k): # k
    print("FUNCTION TIMER" + str(k))
    global time_start_zones_garden
    for k0,v0 in json_to_server.items():
        if (k0 == "gardenzones"):    
            for kka, vva in v0.items():   #itereaza prin json_to_server   ######## creaza lista actuatori
                if (k in kka):   # daca a gasit zona itereaza prin ea
                    lista_zona_GPIO = [] ; lista_zona_index = []
                    for ia in vva:  # itereaza elem de tip lista prin zona
                        for kkka,vvva in ia.items():  # itereaza prin lista
                            if ("soil_actuator" in str(vvva)): # daca gaseste actuator
                        #print(str(kkka) + ":"  + str(vvva))
                                lista_zona_GPIO.append(myinput[vvva].GPIO_alocated) ### creaza lista cu pini actuatoarelor
                                lista_zona_index.append(ia)
      #      print("IIIIII" + str(lista_zona_GPIO))
                    if (len(lista_zona_GPIO) > 0 and int(counter_zones_garden[k]) == 0):  ### verifica daca am element in lista
                        start_ct = time.time()
                        time_start_zones_garden[k] = start_ct
                        counter_zones_garden[k] += 1
                        for il in lista_zona_GPIO:   ### itereaza in lista
       #             print("GPIO aprins= " + str(il) + " din lista = " + str(lista_zona_GPIO))
                            il_index = lista_zona_GPIO.index(il)
                            elem_zone = lista_zona_index[il_index]
                            elem_zone_index = vva.index(elem_zone)
        #            print("before >>> " + str(json_to_server[k][elem_zone_index]["state"]) )
                            GPIO.output(il , GPIO.HIGH) 
                            json_to_server["gardenzones"][k][elem_zone_index]["state"] = GPIO.input(il)

    
def getsoil_values():
    for i in myinput:
        if ("soil_read" in i):
            for k0,v0 in json_to_server.items():
                if (k0 == "gardenzones"):
                    for k,v in v0.items():
                        if (k == myinput[i].pozitie):
                            for ii in v:
                                for kk,vv in ii.items():
                                    if("soil_read" in str(vv)):
                                        ind_iss = json_to_server["gardenzones"][k].index(ii)
                                #print(i)
                                        soil_moisture_values = soil_moisture_read(myinput[i].GPIO_SDA, myinput[i].GPIO_SCL)
                                        json_to_server["gardenzones"][myinput[i].pozitie][ind_iss]["temperature"] = soil_moisture_values[0]
                                        json_to_server["gardenzones"][myinput[i].pozitie][ind_iss]["humidity"] = soil_moisture_values[1]
                                        actual_humi_zones_garden[myinput[i].pozitie] = soil_moisture_values[0]
                                 
##-----------------------------------END GARDEN------------------------------------------##


#############################################################
#############################################################
#############################################################

#device_file1 = '/sys/bus/w1/devices/28-0301a2799541/w1_slave' # cap rotund (retur)  se cauta in folder /sys/bus/w1/devices  ###
#device_file = '/sys/bus/w1/devices/28-03139779c77a/w1_slave'  # cap tocit (tur)  ### ad 3.2 adaugare senzor temp instalatie

def read_temp_raw(device_location):
    f = open(device_location, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_water_temp(device_location):
    lines = read_temp_raw(device_location)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        tempc = float(temp_string) / 1000.0
        temp_c = round(tempc, 1)
        return temp_c

	
#############################################################
#############################################################
#############################################################



##################################################################################
                          ### Switch FUNCTION  ###              		##
		      ## Action outputs throw FLASK ##				##
def buttontrigger( inpin, becnumber):
	time.sleep(10)
	indexnumber = myinput[becnumber].indexnumber
	out = myinput[becnumber].GPIO_alocated
	inlaststate = GPIO.input(inpin)
	print(".......Buton........ON>>> " + str(inpin) + " control out nr:" + str(out) )
	while True:
		if (GPIO.input(inpin) != inlaststate ):
			ouputtrigger(out, indexnumber)
			time.sleep(1)					#### Asta se poate adauga ca variabila
			inlaststate = GPIO.input(inpin)
		time.sleep(0.2)
def ouputtrigger( out, indexnumber ):  # ARG1...GPIO Pin output , ARG2...mainkey from dict for json , ARG3...key from dict for json
	
#	global pirbypass 
	state = json_to_server["lights"][int(indexnumber)]["state"]	
	actual_state = GPIO.input(out) 
	state = actual_state 
	if (state == False): 
		GPIO.output(out, GPIO.HIGH) 
		state = GPIO.input(out) 
		json_to_server["lights"][ int(indexnumber) ]["state"] = state 
#		pirbypass = 1 
#		savecsv("datal.csv", livingdata) 
	elif (state == True): 
		GPIO.output(out, GPIO.LOW) 
		state = GPIO.input(out) 
#		pirbypass = 0 
	#	savecsv("datal.csv", livingdata) 
		json_to_server["lights"][ int(indexnumber) ]["state"] = state 

def ouputheat( out, indexnumber ):  # ARG1...GPIO Pin output , ARG2...mainkey from dict for json , ARG3...key from dict for json
	
#	global pirbypass 
	state = json_to_server["heating"][int(indexnumber)]["state"]	
	actual_state = GPIO.input(out) 
	state = actual_state 
	if (state == False): 
		GPIO.output(out, GPIO.HIGH) 
		state = GPIO.input(out) 
		json_to_server["heating"][ int(indexnumber) ]["state"] = state 
#		pirbypass = 1 
#		savecsv("datal.csv", livingdata) 
	elif (state == True): 
		GPIO.output(out, GPIO.LOW) 
		state = GPIO.input(out) 
#		pirbypass = 0 
	#	savecsv("datal.csv", livingdata) 
		json_to_server["heating"][ int(indexnumber) ]["state"] = state 
		
def ouputsoil( out, indexnumber, zone ):  # ARG1...GPIO Pin output , ARG2...mainkey from dict for json , ARG3...key from dict for json
	
#	global pirbypass 
	state = json_to_server["gardenzones"][zone][int(indexnumber)]["state"]	
	actual_state = GPIO.input(out) 
	state = actual_state 
	if (state == False): 
		GPIO.output(out, GPIO.HIGH) 
		state = GPIO.input(out) 
		json_to_server["gardenzones"][zone][ int(indexnumber) ]["state"] = state 
#		pirbypass = 1 
#		savecsv("datal.csv", livingdata) 
	elif (state == True): 
		GPIO.output(out, GPIO.LOW) 
		state = GPIO.input(out) 
#		pirbypass = 0 
	#	savecsv("datal.csv", livingdata) 
		json_to_server["gardenzones"][zone][ int(indexnumber) ]["state"] = state 

##################################################################################
                            ### TEMP READ ###                             	##
		          ## for DHT11 sensor ##				##
def tempread1(): 
    instance = dht11.DHT11(pin=5)
    result = instance.read()
    if result.is_valid():
        tempz = result.temperature
        humiz = result.humidity
        #print(tempz)
        #print(humiz)
        return tempz, humiz


def temp_dht11():
    start_ct = time.time()
    print(".....DHT11_simple.....ON")
    #print(instance)
    while True:
        stop_ct = time.time()
        dht11read_value = None
        while (dht11read_value is None): 
            dht11read_value = tempread1()
#    print("TEMPERATURA ESTE: " + str(tempg))
        restart_timer , pasted_or_not = timerlib77.timer_sec(10 , start_ct , stop_ct)
        start_ct = restart_timer
        if pasted_or_not:
            #print("TEMPERATURA ESTE: " + str(tempg))
            #print(dht11read_value)
            json_to_server["temperature"] = dht11read_value[0]
            json_to_server["humidity"] = dht11read_value[1]
        time.sleep(0.3)	

###-------------------------------------------------------------------------------##

##################################################################################
                            ### TEMP READ ###                             	##
		          ## for DHT22 sensor ##				##
firrupt = 0
def dht11read1(DHT_SENSOR, DHT_PIN):

	global firrupt
	firrupt += 1  # alerta fir intrerupt   
	if (firrupt >= 12):
			print("FAIL READ CHECK CABLE " + str(firrupt))
			json_to_server["ambienttempdefect"] = 1
	time.sleep(2);
	humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN) ###
	if humidity is not None and temperature is not None:
		firrupt = 0 
		json_to_server["ambienttempdefect"] = 0 ###
		temperature = round(temperature, 1)
		humidity = round(humidity, 1)
		return temperature, humidity
	
def temp_dht_adafruit(DHT_PIN):

	DHT_SENSOR = Adafruit_DHT.DHT22       ###################
	start_ct = time.time()
	print(".........temp read.........ON")
	while True:
		stop_ct = time.time()
		dht11results = None
		while (dht11results is None):  
			dht11results = dht11read1(DHT_SENSOR, DHT_PIN)
			if (firrupt >= 13):
				dht11results = (200, 200)
				break
		restart_timer , pasted_or_not = timerlib77.timer_sec(10 , start_ct , stop_ct) # arg 1 timpul in sec la cat sa faca afisarea
		start_ct = restart_timer
		if pasted_or_not:
			print("TEMPERATURA ESTE: " + str(dht11results[0]))
			print("Umiditatea este: " + str(dht11results[1])) 
			json_to_server["temperature"] = dht11results[0] ###
			json_to_server["humidity"] = dht11results[1] ###
			#savecsv("datal.csv", livingdata)
		time.sleep(2)
###-------------------------------------------------------------------------------##




#####################################################################################
                                ### SHT10 Function ###

#from pi_sht1x import SHT1x
#primele 2 argumente din SHT1x sunt pinii GPIO 2-SDA///3-SCL

"""  !!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!! 

In libraria original trb modificate 2 linii pentru a functiona

1)--- LINE 59 --- from gpio_mode=GPIO.BOARD to gpio_mode=GPIO.BCM  this can be made also when initiate the instance 
2)--- LINE 92 --- from GPIO.cleanup() to #GPIO.cleanup()  so comment the cleanup because that comand set out the GPIO.pins mode and is also used in another threadings
"""

def soil_moisture_read(SDA_pin_num, SCL_pin_num):
    try:
        with SHT1x(SDA_pin_num, SCL_pin_num, gpio_mode=GPIO.BCM ,vdd='3.3V', crc_check=False) as sensor:
            temperature = sensor.read_temperature()
            humidity = sensor.read_humidity(temperature)
            #sensor.calculate_dew_point(temperature, humidity)
            #print(sensor)
            #print(temperature)
            #print(humidity)
            return temperature , humidity
    except :
        print("Defect sensor soil moisture")
        #json_to_server["SHT10defect"] = 1
        return 1000 , 1000
        pass 
    #except Exception as e:
        #print(e)
        #raise


###-------------------------------------------------------------------------------##



#####################################################################################
                                ### PIR function ###

def PIR1trigger(ingpio, becnumber):
    time.sleep(10)
    pirbypass = 0  #### check that
    outgpio = myinput[becnumber].GPIO_alocated
    indexnumber = myinput[becnumber].indexnumber
    PIRls = 0
    becON = 0
    becls = 0
    start_ct = time.time()
    print("........PIR........ ON " + str(ingpio) + " >>> " + str(outgpio))
    while True:
        secureON = int(json_from_server["secure"])  
        dimineata = int(json_from_server["dimineata"])  
        seara = int(json_from_server["seara"]) 
	#print("GPIO_" + str(ingpio) + " have state_" + str(GPIO.input(ingpio)) + " and PIRls_" + str(PIRls) +" with becON" + str(becON))
        time.sleep(1) 
        if (secureON == 0):
            timejson = int(json_from_server["timePIR"])  
            
            dict_split_dtsis = json_to_server["dtsis"].split(':') 
            datetimepi = int(dict_split_dtsis[0])
            #print(datetimepi)
            if (int(datetimepi) < dimineata or int(datetimepi) > seara):  ###noapte
                #print("im in")
                stop_ct = time.time() 
                time_elapsed = stop_ct - start_ct 
                if (GPIO.input(ingpio) == 1 and PIRls == 0):  
                    becON += 1  
                    PIRls = 1
                elif (GPIO.input(ingpio) == 0 and PIRls == 1):  
                    PIRls = 0
                elif (becON > becls):
                    GPIO.output(outgpio, GPIO.HIGH)  ###___
                    json_to_server["lights"][indexnumber]["state"] = GPIO.input(outgpio)  
		    #savecsv("datal.csv", livingdata)  
                    becls = becON
                    start_ct = stop_ct
                elif (time_elapsed > int(timejson) and GPIO.input(outgpio) != 0 and pirbypass == 0):  
                    GPIO.output(outgpio, GPIO.LOW)  ###___
                    json_to_server["lights"][indexnumber]["state"] = GPIO.input(outgpio)   
		    #savecsv("datal.csv", livingdata)  
                    start_ct = stop_ct   
		
        else:
            secureON = int(livingset["secure"])  ###
            if (GPIO.input(PIR1) == 1):  
                print("sentalert")
                time.sleep(int(livingset["timePIR"]))  ###
###-------------------------------------------------------------------------------##		




##################################################################################
                            ### SYSTEM DATE/TIME ###                           	##
		               ## use only HOUR ##				##
def datetimesis():
	print('.......date time.......ON')
	while True:
		datetimenow()
		time.sleep(60)

def datetimenow():
	now = datetime.now()
	timen = now.strftime("%H:%M")
	weekn = now.strftime("%a")    # days of week:  0-Sun , 1-Mon , 2-Tue , 3-Wed , 4-Thu , 5-Fri , 6-Sat  
	json_to_server["wsis"] = weekn
	json_to_server["dtsis"] = timen  
	#savecsv("datal.csv", livingdata)				
##------------------------------------------------------------------------------##
		



##################################################################################
                                ### FLASK ###                           	##
                                                   				##

app = Flask(__name__)
#CORS(app, origins='*') #CORS - .net line2/2

@app.route('/')
def index():
	return' WELCOME TO SMART HOME '
	
	
@app.route('/page', methods=['POST', 'GET'])
def living():
	#global json_to_server
	return jsonify(json_to_server)
	        
@app.route('/temp', methods=['POST', 'GET'])
def temp_send():
	#global json_to_server
        return str(json_to_server["temperature"])	
	#return jsonify(json_to_server)

@app.route('/light/<name>/<GPIO_alocat>' , methods=['POST', 'GET'])   #route pentru iluminat
def light_trig(name, GPIO_alocat):
    print(name)
    print(GPIO_alocat)
    
    ouputtrigger( int(GPIO_alocat) , name )     	
    return jsonify(json_to_server)

@app.route('/heat/<name>/<GPIO_alocat>' , methods=['POST', 'GET'])   #route pentru heting
def heat_trig(name, GPIO_alocat):
    #print(name)
    #print(GPIO_alocat)
    if (json_from_server["heatmode"] == 3):
        ouputheat( int(GPIO_alocat) , name ) 
    return jsonify (json_to_server, json_from_server) 
    
@app.route('/<zone>/<name>/<GPIO_alocat>' , methods=['POST', 'GET'])   #route pentru soil_actuator
def soil_trig(name, GPIO_alocat, zone):
    #print(name)
    #print(GPIO_alocat)
    if (json_from_server["gardenmode"] == 2):
        ouputsoil( int(GPIO_alocat) , name , zone )     	
    return jsonify (json_to_server, json_from_server) 
    
@app.route('/pageset' , methods=['POST', 'GET']) 	
def page_set():
    #print(name)
    #print(GPIO_alocat)
    #ouputheat( int(GPIO_alocat) , name )     	
    return jsonify (json_from_server) 		
    
@app.route('/getjson' , methods=['POST', 'GET']) 	
def page_getjson():
    global json_from_server
    #print(name)
    #print(GPIO_alocat)
    #ouputheat( int(GPIO_alocat) , name ) 
    received_json = request.json
    print(received_json) 
    print(type(received_json))
    #print(json_from_server)   
    json_from_server.update(received_json)
    #print("after")
    #print(json_from_server) 
    return jsonify (json_from_server)    
    
    
#@app.route('/lpostpy', methods=['POST', 'GET'])
#def setliving():
#	global livingset
#	req_data = request.get_json()
#
#	livingset["setpointhumi"] = req_data["humipointl"]  
#	livingset["timePIR"] = req_data["pirtimel"]
#	livingset["humitimeON"] = req_data["humitimel"]
#	savecsv("datal.csv", livingdata)
#	print (req_data)
#	print (livingset)
#	return jsonify(req_data)	
##--------------------------------------------------------------------------------##


##########################################################################################
                                ### MAIN static ###                                     ##
                                                                                        ##


def Flaskon():		
	if __name__ == '__main__':
		app.run(threaded = True , debug=False , host= FLASK_adress["DEVipadress"] , port= FLASK_adress["DEVipport"])


t_FLASK =threading.Thread(target = Flaskon, name = "Flask_Threading")
t_FLASK.start()

t_DateTimesis = threading.Thread(target = datetimesis, name = "Datetime_Threading")
t_DateTimesis.start()
#t_soil =threading.Thread(target = soil_moisture_read, name = "Flask_Threading", args = (2, 3))
#t_soil.start()
#soil_moisture_read(2,3)

##########################################################################################
                                ### MAIN dynamic ###                               	##
                             ## Elements,THREADING generator ##                 			##
											##
for i_key, i_value in smart_home_elements.items():					##
    if("bec" in i_key):									##
        myinput[i_key].add_light_endpoints()							##
        #myinput[i_key].create_api()                              	 		##
    elif("temp_read" in i_key):								##
        myinput[i_key].temp_adafruit_thread()							##
    elif("temp_11_local_read" in i_key):								##
        myinput[i_key].temp11_thread()							##
    elif("switch" in i_key):								##
        myinput[i_key].create_thread() 							##
    elif("PIR" in i_key):								##
        myinput[i_key].pir_thread()
    elif("heatgenerator" in i_key):
        myinput[i_key].add_heat_generator()
    elif("heatactuator" in i_key): 
        myinput[i_key].add_heat_actuator()	
    elif("water_temp" in i_key):
        myinput[i_key].water_temp()	    	    									##
 ##   elif("soil_read" in i_key):
 ##       myinput[i_key].soil_sensor_read()
 ##   elif("soil_actuator" in i_key):
 ##       myinput[i_key].add_soil_actuator()
    elif("soil" in i_key):
        myinput[i_key].create_soil_zones()
    elif("curtain" in i_key):
        myinput[i_key].curtain_call()
    else:										##
        print("\n THAT smart_home_elements IS not THREADED " + str(i_key) + "\n")  	##
											##
											##
##--------------------------------------------------------------------------------------##

#############################################################


time.sleep(10)
while True:
        time.sleep(30)
        #print(counter_zones_garden)
        #print(json_to_server)
        #print(dict_zones_garden)
	
        #time.sleep(30)
        #print("GARDEN IN MAN........................................................")
        #json_from_server["gardenmode"] = 2
        time.sleep(120)
        #json_from_server["gardenmode"] = 0
        time.sleep(30)
        #print("GARDEN IN AUTO........................................................")
        #json_from_server["gardenmode"] = 1
        #for k,v in dict_zones_garden.items():   ################################################################
        #    if ("zone" in k):                   ################### reset zones ON act counter #################
        #        counter_zones_garden[k] = 0     ################################################################
        #print(json_from_server)
        #for i in myinput:
            #print (i)
            #print("...M..........")
            ##print(myinput[i].GPIO_alocated)
        #print(json_from_server)    
        #datetimesis()
        #soil_moisture_read(2,3)
	#print(myinput)
	#time.sleep(50)
	#print(myinput['bec3'].GPIO_alocated)
	#print("---------------------------------------")
        #print("json_to_server")
	#print(json_to_server)
	#print("\n")
        #print("json_from_server")
	#print(json_from_server)
	#print("\n")
	#print(json_for_heating)
	#print(myinput['bec1'].indexnumber)
	#print(json_to_server["lights"][0])
	#print(json_to_server["lights"][0]["state"])
	#time.sleep(50)
