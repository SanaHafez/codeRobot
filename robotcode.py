from flask import Flask, request, render_template, redirect, url_for, make_response
import time
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
pump=Motor(forward=9, backward=10)

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
def stepper():
    global current
    if current == sensorIdle:
        set_step('S')
        print("Idle")
    elif current == sensorDown:
        sensorGoesDown()
        current = sensorOnstay
    elif current == sensorOnstay:
        moisturevalue = GPIO.input(sensorpin) #Change this code to sensor code
        if moisturevalue == 0:
            print("Moisture detected")
        else:
            print("Moisture NOT detected")
            current = sensorUP
    elif current == sensorUP:
        sensorGoesUp()
        current = sensorIdle

def drive():
    global current
    global current1
    if current == idle:
        current1='Stop'
        motor1.stop()
        motor2.stop()
    elif current == Forward:
        current1='Forward'
        motor1.forward(speed=1)
        motor2.forward(speed=1)
    elif current == Backward:
        current1='Backward'
        motor1.backward(speed=1)
        motor2.backward(speed=1)
    elif current == Left:
        current1='Left'
        motor1.forward(speed=1)
        motor2.backward(speed=1)
    elif current == Right:
        current1='Right'
        motor1.backward(speed=1)
        motor2.forward(speed=1)
#page
mgs='idle'
sprinkle='Off'
sensor='Reading'
app = Flask(__name__)

@app.route('/',methods=["POST","GET"])
def index():
    global panServoAngle
    global tiltServoAngle
    global led
    global current
    global current1
    global msg
    global sprinkle
    global sensor
    if request.method == "POST":
        msg = request.form['action']
    #return render_template('index.html')

#@app.route('/<msg>/<value>')
#def move(msg, value):
    
        if msg == 'panleft':
            current=idle
            if panServoAngle<100:
                panServoAngle = panServoAngle + 10
        elif msg == 'panright':
            if panServoAngle>50:
                panServoAngle = panServoAngle - 10
    # os.system("python3 angleServoCtrl.py " + str(panPin) + " " + str(panServoAngle))
        elif msg == 'tiltup':
            current = idle
            if tiltServoAngle<100:
                tiltServoAngle = tiltServoAngle + 10
        elif msg == 'tiltdown':
            if tiltServoAngle>50:
                tiltServoAngle = tiltServoAngle - 10
    # os.system("python3 angleServoCtrl.py " + str(tiltPin) + " " + str(tiltServoAngle))
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
            current = sensorIdle
            sensor='sensorValue' ##Edit here
        elif msg == 'sprinkleon':
            sprinkle='On'
            pump.forward()
            current = sensorIdle
        elif msg == 'sprinkleoff':
            sprinkle='Off'
            pump.forward()
            current = sensorIdle
               


    templateData = {
        'panServoAngle': panServoAngle,
        'tiltServoAngle': tiltServoAngle,
        'led': led,
        'current1' : current1,
        'sprinkle' : sprinkle,
        'sensor': sensor
    }
    # response = make_response(redirect(url_for('index')))
    # return(response)

    return render_template('index.html', **templateData)

if __name__ == '__main__':
    os.system("sudo rm -r  ~/.cache/chromium/Default/Cache/*")
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)