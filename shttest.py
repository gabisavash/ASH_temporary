import time

import RPi.GPIO as GPIO
from pi_sht1x import SHT1x
from sht_sensor import Sht


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()

def sht1x_my():
    while True:
        time.sleep(10)
        try:
            with SHT1x(2, 3, gpio_mode=GPIO.BCM, vdd='3.3V', crc_check=False) as sensor:
	            temperature = sensor.read_temperature()
	            humidity = sensor.read_humidity(temperature)
	            sensor.calculate_dew_point(temperature, humidity)
	            print(sensor)
	            print(temperature)
	            print(humidity)
        except:
            print("EXCEPT")
            pass   
	        
	        
def sht1x_my2():
    while True:
        time.sleep(70)
        with SHT1x(13, 26, vdd='3.3V', crc_check=False) as sensor:
	        temperature2 = sensor.read_temperature()
	        humidity2 = sensor.read_humidity(temperature2)
	        sensor.calculate_dew_point(temperature2, humidity2)
	        print(sensor)
	        print(temperature2)
	        print(humidity2)
	        break	        

def sht_sensor_my():
    sht = Sht(2,3, freq_sck=100, freq_data=200)

    print(sht.read_t())


sht1x_my()    # this one works with crc_check on False

#sht_sensor_my()   # crc check error don't work
#t = sht.read_t()
#humi = sht.read_rh(t)
#print(temp)
#print(humi)




