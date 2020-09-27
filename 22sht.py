import time

import RPi.GPIO as GPIO
from pi_sht1x import SHT1x
from sht_sensor import Sht


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()

def sht1x_my1():
    #while True:
    time.sleep(1)
    try:
        with SHT1x(7, 8, gpio_mode=GPIO.BCM, vdd='3.3V', crc_check=False) as sensor:
            temperature = sensor.read_temperature()
            humidity = sensor.read_humidity(temperature)
            sensor.calculate_dew_point(temperature, humidity)
            print(sensor)
            print(temperature)
            print(humidity)
    except:
        print("EXCEPT")
	#pass   
	        



sht1x_my1()    # this one works with crc_check on False




