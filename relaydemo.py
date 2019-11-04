#Following code is for any machine whose log we want to keep throughout the time (job cycle) using raspberry pi
#This code aims to track the state of a  5 machines i.e ON/OFF ( you can have any no of machines you want)
# logs are sent to web page using json objects like on time,off time ,total job time etc
# data is also printed on max7219 led matrix device.

import RPi.GPIO as GPIO
import time
import sys
import os
import requests
import urllib
import httplib
from time import sleep, strftime
from datetime import datetime
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
start_job_pin= 36
stop_job_pin= 38
motor_pin_1 = 31
motor_pin_2 = 33
motor_pin_3 = 35
motor_pin_4 = 37
motor_pin_5 = 29
emergency_pin = 40
red_led_pin = 16
green_led_pin = 18
blue_led_pin = 22
flag = 0
count =0
errorFlag = False
startFlag = False
total_job_time_motor_1 = []
total_job_time_motor_2 = []
total_job_time_motor_3 = []
total_job_time_motor_4 = []
total_job_time_motor_5 = []
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(50)
virtual = viewport(device, width=32, height=16)
show_message(device, 'Skrillex', fill="white", font=proportional(LCD_FONT))
# Following functions board setup,bluestable,redstable,greenstable and redblink can be called from seperate file 
#but for simplicity purpose i have kept it in main python file.	
def boardSetup(): 
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(start_job_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(stop_job_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(motor_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(motor_pin_2,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(motor_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(motor_pin_4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(motor_pin_5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(red_led_pin, GPIO.OUT)
    GPIO.output(red_led_pin, GPIO.LOW)
    GPIO.setup(green_led_pin, GPIO.OUT)
    GPIO.output(green_led_pin, GPIO.LOW)
    GPIO.setup(blue_led_pin, GPIO.OUT)
    GPIO.output(blue_led_pin, GPIO.LOW)
def blueStable():
    GPIO.output(blue_led_pin, GPIO.HIGH)
    GPIO.output(red_led_pin, GPIO.LOW)
    GPIO.output(green_led_pin, GPIO.LOW)
def redStable():
    GPIO.output(blue_led_pin, GPIO.LOW)
    GPIO.output(red_led_pin, GPIO.HIGH)
    GPIO.output(green_led_pin, GPIO.LOW)
def greenStable():
    GPIO.output(blue_led_pin, GPIO.LOW)
    GPIO.output(red_led_pin, GPIO.LOW)
    GPIO.output(green_led_pin, GPIO.HIGH)
def redBlink():
    GPIO.output(red_led_pin, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(red_led_pin, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(red_led_pin, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(red_led_pin, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(red_led_pin, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(red_led_pin, GPIO.LOW)
    time.sleep(0.25)
def startSwitch(self):
    print ('start interrupt')
    global errorFlag,startFlag
    if (errorFlag == True and GPIO.input(start_job_pin)) == 1:
        errorFlag = False
        with canvas(virtual) as draw:
            sleep(1)
            text(draw, (1, 1),"Ready", fill="white", font=proportional(LCD_FONT))
            sleep(0.5)
    elif  (errorFlag == False and startFlag == False and GPIO.input(start_job_pin)) == 1:
	global job_start_time,flag,count 
	flag = 1 
	startFlag = True
        blueStable()
        job_start_time = int(time.time())
        print ('Start time of job is: ')+str(job_start_time)
	with canvas(virtual) as draw:
            sleep(1)
            text(draw, (1, 1),"Busy", fill="white", font=proportional(LCD_FONT))
            sleep(0.5)
    else:
        print ('LOW')
def stopSwitch(self):
    if GPIO.input(stop_job_pin) == 1:
	global job_stop_time,job_start_time,total_job_time_motor_1,total_job_time_motor_2,total_job_time_motor_3,total_job_time_motor_4,total_job_time_motor_5,total_job_time,flag,job_idle_time,count,startFlag
	greenStable()
	if flag == 1:
            job_stop_time = int(time.time())
            count = count + 1

            print 'Stop time of job is: '+str(job_stop_time)
            print 'Total time for which machine 1 was working:'+str(sum(total_job_time_motor_1))
            print 'Total time for which machine 2 was working:'+str(sum(total_job_time_motor_2))
            print 'Total time for which machine 3 was working:'+str(sum(total_job_time_motor_3))
            print 'Total time for which machine 4 was working:'+str(sum(total_job_time_motor_4))
            print 'Total time for which machine 5 was working:'+str(sum(total_job_time_motor_5))
            total_job_time = job_stop_time - job_start_time
            job_idle_time = (total_job_time) - (sum(total_job_time_motor_1) + sum(total_job_time_motor_2) + sum(total_job_time_motor_3) + sum(total_job_time_motor_4) + sum(total_job_time_motor_5))
            print 'Total job time: '+str(total_job_time)
            print  'Job idle time: '+str(job_idle_time)
            print  'Total Job count: '+str(count).zfill(2)
            status = "success"
            data_logs = { 
                    "status" : status, 
                    "serial_id": "midas123", 
                    "total_job_time" : total_job_time, 
                    "job_start_time": job_start_time , 
                    "job_stop_time" : job_stop_time ,
                    "emergency_stop_time": "Null",
                    "motors_data":
                            {
     
                                    "motor_1": sum(total_job_time_motor_1),
                                    "motor_2": sum(total_job_time_motor_2),
                                    "motor_3": sum(total_job_time_motor_3),
                                    "motor_4": sum(total_job_time_motor_4),
                                    "motor_5": sum(total_job_time_motor_5)
                             }
			}
            print data_logs
            response = requests.post('http://midas.iogreen.in/data/add', json=data_logs)
            print response
            print "cleared all array"
            total_job_time_motor_1[:] = []
            total_job_time_motor_2[:] = []
            total_job_time_motor_3[:] = []
            total_job_time_motor_4[:] = []
            total_job_time_motor_5[:] = []
            flag = 0
            startFlag = False
            with canvas(virtual) as draw:
                text(draw, (1, 1),"Job:"+str(count).zfill(2), fill="white", font=proportional(LCD_FONT))
                sleep(2)	
            with canvas(virtual) as draw:
                sleep(1)
                text(draw, (1, 1),"Done", fill="white", font=proportional(LCD_FONT))
                sleep(0.5)        
            with canvas(virtual) as draw:
                sleep(1)
                text(draw, (1, 1),"Ready", fill="white", font=proportional(LCD_FONT))
                sleep(0.5)
    else:
        redBlink()
def emergencyInterrupt(self):
    if GPIO.input(emergency_pin) == 1:
        
	global job_stop_time,job_start_time,total_job_time_motor_1,total_job_time_motor_2,total_job_time_motor_3,total_job_time_motor_4,total_job_time_motor_5,total_job_time,flag,errorFlag,startFlag
	errorFlag = True
	startFlag = False
	redStable()
	if flag ==1:
            emergency_stop_time = int(time.time())
            print 'Emergency Time is: '+str(emergency_stop_time)
            total_job_time = emergency_stop_time - job_start_time
            status = "failure"
            data_logs = { 
            "status" : status, 
            "serial_id": "midas123", 
            "total_job_time" : total_job_time, 
            "job_start_time": job_start_time , 
            "job_stop_time" : "Null" , 
            "emergency_stop_time": emergency_stop_time,
            "motors_data":
                    {
                            "motor_1": sum(total_job_time_motor_1),
                            "motor_2": sum(total_job_time_motor_2),
                            "motor_3": sum(total_job_time_motor_3),
                            "motor_4": sum(total_job_time_motor_4),
                            "motor_5": sum(total_job_time_motor_5)

                     }

			 }
            print data_logs
            response = requests.post('http://midas.iogreen.in/data/add', json=data_logs)
            print response
            total_job_time_motor_1[:] = []
            total_job_time_motor_2[:] = []
            total_job_time_motor_3[:] = []
            total_job_time_motor_4[:] = []
            total_job_time_motor_5[:] = []
            print "cleare array 1"+str(total_job_time_motor_1)
            flag = 0
            with canvas(virtual) as draw:
                sleep(1)
                text(draw, (1, 1),"Error", fill="white", font=proportional(LCD_FONT))
                sleep(0.5)
    else:
	redBlink()
def motor1(self):
    global motor_start_time, total_time, motor_finish_time,startFlag
    if flag == 1 and startFlag == True:
        if GPIO.input(motor_pin_1) == 1:
            motor_start_time = int(time.time())
            print ('start time of motor 1: ') + str(motor_start_time)
        elif GPIO.input(motor_pin_1) == 0:
            motor_finish_time = int(time.time())
            print ('finish_time of motor 1: ')+str(motor_finish_time)
            total_time = motor_finish_time - motor_start_time
            print ('Total time of motor 1: ')+str(total_time)
            total_job_time_motor_1.append(total_time)       
    else:
        redBlink()
def motor2(self):
    global motor_2_start_time, total_time_motor_2, motor_2_finish_time,startFlag
    if flag == 1 and startFlag == True:
        if GPIO.input(motor_pin_2) == 1:
            motor_2_start_time = int(time.time())
            print ('Start time of motor 2: ')+str(motor_2_start_time)
        elif GPIO.input(motor_pin_2) == 0:
            motor_2_finish_time = int(time.time())
            print ('Finish time of motor 2: ')+str(motor_2_finish_time)
            total_time_motor_2 = motor_2_finish_time - motor_2_start_time
            print ('Total time of motor 2: ')+str(total_time_motor_2)
            total_job_time_motor_2.append(total_time_motor_2)
    else:
        redBlink()
def motor3(self):
    global motor_3_start_time, total_time_motor_3, motor_3_finish_time,startFlag 
    if flag == 1 and startFlag == True:
        if GPIO.input(motor_pin_3) == 1:
            motor_3_start_time = int(time.time())
            print ('Start time of motor 3: ')+str(motor_3_start_time)
        elif GPIO.input(motor_pin_3) == 0:
            motor_3_finish_time = int(time.time())
            print ('Finish time of motor 3: ')+str(motor_3_finish_time)
            total_time_motor_3 = motor_3_finish_time - motor_3_start_time
            print ('Total time of motor 3: ')+str(total_time_motor_3)
            total_job_time_motor_3.append(total_time_motor_3)

    else:
        redBlink()
def motor4(self):
    global motor_4_start_time, total_time_motor_4, motor_4_finish_time,startFlag
    if flag == 1 and startFlag == True:
        if GPIO.input(motor_pin_4) == 1:
            motor_4_start_time = int(time.time())
            print ('Start time of motor 4: ')+str(motor_4_start_time)
        elif GPIO.input(motor_pin_4) == 0:
	    motor_4_finish_time = int(time.time())
	    print 'Finish time of motor 4: '+str(motor_4_finish_time)
	    total_time_motor_4 = motor_4_finish_time - motor_4_start_time
	    print 'Total time of motor 4: '+str(total_time_motor_4)
	    total_job_time_motor_4.append(total_time_motor_4)

    else:
        redBlink()
def motor5(self):
    global motor_5_start_time, total_time_motor_5, motor_5_finish_time,startFlag
    print ('Motor-5 interrupt')
    if flag == 1 and startFlag == True:
        if GPIO.input(motor_pin_5) == 1:
            motor_5_start_time = int(time.time())
            print ('Start time of motor 5: ')+str(motor_5_start_time)
        elif (GPIO.input(motor_pin_5) == 0):
            motor_5_finish_time = int(time.time())
            print ('Finish time of motor 5: ')+str(motor_5_finish_time)
            total_time_motor_5 = motor_5_finish_time - motor_5_start_time
            print ('Total time of motor 5: ')+str(total_time_motor_5)
            total_job_time_motor_5.append(total_time_motor_5)

    else:

        redBlink()
def interruptAttach():
    GPIO.add_event_detect(start_job_pin, GPIO.RISING, callback=startSwitch, bouncetime=300)
    GPIO.add_event_detect(stop_job_pin, GPIO.BOTH, callback=stopSwitch, bouncetime=300)
    GPIO.add_event_detect(emergency_pin, GPIO.BOTH,callback=emergencyInterrupt, bouncetime=300)
    GPIO.add_event_detect(motor_pin_1, GPIO.BOTH, callback=motor1, bouncetime=300)
    GPIO.add_event_detect(motor_pin_2, GPIO.BOTH,callback=motor2, bouncetime=300)
    GPIO.add_event_detect(motor_pin_3, GPIO.BOTH,callback=motor3, bouncetime=300)
    GPIO.add_event_detect(motor_pin_4, GPIO.BOTH,callback=motor4, bouncetime=300)
    GPIO.add_event_detect(motor_pin_5, GPIO.BOTH,callback=motor5, bouncetime=300)

boardSetup()
interruptAttach()
redStable()
while  True:
	time.sleep(0)


