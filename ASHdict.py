
FLASK_adress = {  "DEVipadress" : "122.104.23.113",
				"DEVipport" : 11111 
}

smart_home_elements = { 
			"switch10":
                              { "GPIO_alocated" : 22 ,		## param for init input  (is the GPIO pin on RPY)
                                "input_type" : "pull_down" ,	## param for init input  (is the type of input  ::"pull_down" "pull_up" "pull_no" "PIR" "DHT11" "DHT22" "outsimple" ::)
                                "linked_output_name" : "bec1", }, 	## param for threading to control output  (this must be the name of output<mainkey>)
		        
			#"switch20":
                              #{ "GPIO_alocated" : 27 ,		
                                #"input_type" : "pull_down" ,	
                                #"linked_output_name" : "bec2",},
                              
			"PIR1":
			       { "GPIO_alocated" : 6 ,
			         "input_type" : "PIR" , 
				 "linked_output_name" : "bec2", },
				 
			#"water_temp1" :        ## need the heatgenerator element for RUN else do not read the temp + 1wire protocol enabled
				#{ "pozitie" : "floortemp",   ### name of the sensor pozition
				  #"input_type" : "DS18B20" ,  ### type of input
				  #"path_1wire" : "/sys/bus/w1/devices/28-0301a2799541/w1_slave" ,},  ### path for the 1 wire sensor 

			#"water_temp2" :
				#{ "pozitie" : "retur",
				  #"input_type" : "DS18B20" ,
				  #"path_1wire" : '/sys/bus/w1/devices/28-03139779c77a/w1_slave' ,},		       
######################################################################		       
######################  outputs  #####################################
######################################################################
        "bec1":                                               ### THE NAME of OBJECT 
            { "GPIO_alocated" : 23 ,                    ### the GPIO pin for the light
              "input_type" : "outsimple" ,} ,         ### the type of output     :: "outsimple"    ::

	"bec2":
	    {  "GPIO_alocated" : 24 ,
	       "input_type" : "outsimple",},
	       
	#"bec3":
	    #{  "GPIO_alocated" : 25 ,
	       #"input_type" : "outsimple",},	       
	       	
	  #"heatgenerator1" : 
		#{ "GPIO_alocated" : 12 ,
		  #"input_type" : "outsimple" , },

	  ###"heatgenerator2" : 
		###{ "GPIO_alocated" : 24 ,
		  ###"input_type" : "outsimple" , },
		  
	  #"heatactuator1" :
	       #{ "GPIO_alocated" : 23 ,
		 #"input_type" : "outsimple" ,
		 #"temp_url" : "http://122.104.23.111:11111/temp" ,} , 		 

		
	  ##"heatactuator2" :
	       ##{ "GPIO_alocated" : 24 ,
		 ##"input_type" : "outsimple" ,
		 ##"temp_url" : "http://122.104.23.113:11111/temp" ,} , 		 

	  #"heatactuator3" :
	       #{ "GPIO_alocated" : 25 ,
		 #"input_type" : "outsimple" ,
		 #"temp_url" : "http://122.104.23.114:11111/temp" ,} ,											


				
                        #"temp_11_local_read1": 
                              #{ "GPIO_alocated" : 5 ,   
                                #"input_type" : "DHT11_local" ,},

                        #"temp_read1": 
                              #{ "GPIO_alocated" : 5 ,   
                                #"input_type" : "DHT22" ,},


										#"soil_read1" :   {  "GPIO_SDA" : 2,
															#"GPIO_SCL" : 3,
															#"pozitie" : "zone1" , ### 
															#"input_type" : "sht_i2c"},
															
										#"soil_read2" :   {  "GPIO_SDA" : 15,
															#"GPIO_SCL" : 16,
															#"pozitie" : "zone2" , ### 
															#"input_type" : "sht_i2c"},

										##"soil_read3" :   {  "GPIO_SDA" : 21,
															##"GPIO_SCL" : 27,
															##"pozitie" : "zone3" , ### 
															##"input_type" : "sht_i2c"},
															
										#"soil_actuator1" : {  "GPIO_alocated" : 23 ,
															  #"pozitie" : "zone1",
															  #"input_type" : "outsimple"},
															  
										#"soil_actuator2" : {  "GPIO_alocated" : 24 ,
															  #"pozitie" : "zone1",
															  #"input_type" : "outsimple"},
					
										#"soil_actuator3" : {  "GPIO_alocated" : 25 ,
															  #"pozitie" : "zone2",
															  #"input_type" : "outsimple"},
															  
										#"soil_actuator4" : {  "GPIO_alocated" :  12,
															  #"pozitie" : "zone3",
															  #"input_type" : "outsimple"},
                       "curtain1": 
                              { 
                                "GPIO_enc_A": 26,
                                "GPIO_enc_B": 19,
                                "GPIO_motor_pin_1": 21,
                                "GPIO_motor_pin_2": 20,
                                "GPIO_speed" : 'none'  ,  ### none or (PWM pin number)
                                "GPIO_switch_pin1": "none",  ###4/ none or (input of switch)
                                "GPIO_switch_pin2": "none",  ###27/ none or (input of switch)
                                "input_type" : "DC_curtain",
								"enc_delay": 0.0001 ,    ### low procesor(accuracy) = 0.0002  ////// pololu(25d,48cpr) best 0.00005 >>>>> pololu(20d, 12cpr) 0.0005
								"motor_delay": 0.1 ,     ### low procesor(accuracy) = 0.4  ////// pololu(25d,48cpr) best 0.08 
								"motor_hysterezis" : 80, ### value 1-100 (%)    <<<< MAX hyst= 60% din cursa ,cursa = 10% max lenght,  >>>> 
								"man_sensibility" : 100,  ### number of +- counter for start manual push operation
                                "linked_PIR": "PIR1", ### name of PIR element in dict(PIR key from ASHdict.smart_home_elements) 
								 },            
								 
                       #"curtain2": 
                              #{ 
                                #"GPIO_enc_A": 7,
                                #"GPIO_enc_B": 18,
                                #"GPIO_motor_pin_1": 14,
                                #"GPIO_motor_pin_2": 15,
                                #"GPIO_speed" : 'none'  ,  ### none or (PWM pin number)
                                #"GPIO_switch_pin1": "none",  ### none or (input of switch)
                                #"GPIO_switch_pin2": "none",  ### none or (input of switch)
                                #"input_type" : "DC_curtain",
								#"enc_delay": 0.0005 ,    ### low procesor(accuracy) = 0.0002  ////// pololu(25d,48cpr) best 0.00005 
								#"motor_delay": 0.2 ,     ### low procesor(accuracy) = 0.4  ////// pololu(25d,48cpr) best 0.08 
								#"motor_hysterezis" : 80, ### value 1-100 (%)    <<<< MAX hyst= 60% din cursa ,cursa = 10% max lenght,  >>>> 
								#"man_sensibility" : 40,
                                #"linked_PIR": "none",   ### name of PIR element in dict(PIR key from ASHdict.smart_home_elements) 
								#},
}
