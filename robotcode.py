from flask import Flask, request, render_template, redirect, url_for, make_response
import time
from threading import Timer
import os
import RPi.GPIO as GPIO
from gpiozero import LED, Motor, Button, AngularServo
from time import sleep
#from camera_pi import Camera
#<img src="{{ url_for('video_feed') }}" width="50%">
idle, Forward, Backward, Left, Right, camOnEntry, camOnStay, camTilt, camPan, camCenter, camOff,sensorIdle, sensorDown, sensorOnstay, sensorUP  = range(15)
current = idle
current1="Idle"
#dc motor
motor1 = Motor(forward=23, backward=24)
motor2 = Motor(forward=25, backward=26)

#cam pan tilt
panServo =  AngularServo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
tiltServo =  AngularServo(28, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
panServoAngle = 90
tiltServoAngle = 90
panServo.angle=panServoAngle
tiltServo.angle=tiltServoAngle

#stepper set up
coil1 = Motor(forward=18, backward=19, pwm=False) #sensor stepper
coil2 = Motor(forward=20, backward=21, pwm=False)
forward_seq = ['FF', 'BF', 'BB', 'FB']
reverse_seq = list(forward_seq)  # to copy the list
reverse_seq.reverse()
steps = 800 #stepper motor steps to bring sensor up aand down

#Relay for pump
GPIO.setmode(GPIO.BCM)
relaypin = 9
GPIO.setup(relaypin, GPIO.OUT)
#Sensor set up
sensorpin=10 #Edit this to actual sensor pin

led = "Off"
ledPin = LED(22)

def timerSensor():
    global current
    current = sensorOnstay

#stepper code
def set_step(step):
  if step == 'S':
    coil1.stop()
    coil2.stop()
  else:
    if step[0] == 'F':
      coil1.forward()
    else:
      coil1.backward()
    if step[1] == 'F':
      coil2.forward()
    else:
      coil2.backward()

def sensorGoesDown():
    for i in range(steps):
        for step in forward_seq:
            set_step(step)

def sensorGoesUp():
    for i in range(steps):
        for step in reverse_seq:
            set_step(step)

def sensorTimer():
    global current
    current=sensorUP

def stepper():
    global current
    if current == sensorIdle:
        set_step('S')
        print("sensorIdle")
    elif current == sensorDown:
        sensorGoesDown()
        current = sensorOnstay
    elif current == sensorOnstay:
        Timer(5, sensorTimer).start()
        moisturevalue = GPIO.input(sensorpin) #Change this code to sensor code
        if moisturevalue == 0:
            print("Moisture detected")
        else:
            print("Moisture NOT detected")
            current = sensorUP
    elif current == sensorUP:
        sensorGoesUp()
        current = sensorIdle

def driveTimer():
    global current
    current=idle
    drive()


def drive():
    global current
    global current1
    camAngle('center') #center camera while in drive mode
    if current == idle:
        current1='Stop'
        motor1.stop()
        motor2.stop()
    elif current == Forward:
        current1='Forward'
        motor1.forward(speed=1)
        motor2.forward(speed=1)
        Timer(10, driveTimer).start()
    elif current == Backward:
        current1='Backward'
        motor1.backward(speed=1)
        motor2.backward(speed=1)
        Timer(10, driveTimer).start()
    elif current == Left:
        current1='Left'
        motor1.forward(speed=1)
        motor2.backward(speed=1)
        Timer(2, driveTimer).start()
    elif current == Right:
        current1='Right'
        motor1.backward(speed=1)
        motor2.forward(speed=1)
        Timer(2, driveTimer).start()

def waterTimer():
    global current
    sprinkleoff()
    current = idle
    drive()

def sprinkleon():
    GPIO.output(relaypin, GPIO.HIGH)
    Timer(5, waterTimer).start()

def sprinkleoff():
     GPIO.output(relaypin, GPIO.LOW)
     Timer(5, waterTimer).start()

def camAngle(msg): #adjust view angles
    global panServoAngle
    global tiltServoAngle
    if msg == 'panleft': 
        if panServoAngle<100:
            panServoAngle = panServoAngle + 10
    elif msg == 'panright':
        if panServoAngle>50:
            panServoAngle = panServoAngle - 10        
    elif msg == 'tiltup':
        if tiltServoAngle<100:
            tiltServoAngle = tiltServoAngle + 10
    elif msg == 'tiltdown':
        if tiltServoAngle>50:
            tiltServoAngle = tiltServoAngle - 10
    elif msg == 'center':
            panServoAngle = 0
            tiltServoAngle = 0 

#page
mgs='idle'
sprinkle='Off'
sensor='Reading'

app = Flask(__name__)
@app.route('/',methods=["POST","GET"])
def index():
    
    global led
    global current
    global current1
    global msg
    global sprinkle
    global sensor
    if request.method == "POST": #gets the posted form action message from html page
        msg = request.form['action']    
        if msg == 'panleft' or 'panright' or 'tiltup' or 'tiltdown' or 'center':
            current=idle
            drive() #car wont move while angle is adjusted
            camAngle(msg)
        elif msg == 'ledon':
            led = "On"
            ledPin.on()
            print("led On")
        elif msg == 'ledoff':
            led = "Off"
            ledPin.off()
            print("led Off")
        elif msg =='stop':
            current = idle
            drive()
        elif msg =='forward':
            current = Forward
            drive()
        elif msg =='backward':
            current = Backward
            drive()
        elif msg =='left':
            current = Left
            drive()
        elif msg =='right':
            current = Right
            drive()
        elif msg == 'soiltest':
            current = sensorDown
            stepper()
            sensor='sensorValue' ##Edit here
        elif msg == 'sprinkleon':
            sprinkle='On'
            sprinkleon()  
        elif msg == 'sprinkleoff':
            sprinkle='Off'
            sprinkleoff()
               

    templateData = {
        'panServoAngle': panServoAngle,
        'tiltServoAngle': tiltServoAngle,
        'led': led,
        'current1' : current1,
        'sprinkle' : sprinkle,
        'sensor': sensor
    }
    

    return render_template('index.html', **templateData)

if __name__ == '__main__':
    os.system("sudo rm -r  ~/.cache/chromium/Default/Cache/*")
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)






# response = make_response(redirect(url_for('index')))
    # return(response)
    
# os.system("python3 angleServoCtrl.py " + str(tiltPin) + " " + str(tiltServoAngle))


  #return render_template('index.html')

#@app.route('/<msg>/<value>')
#def move(msg, value):