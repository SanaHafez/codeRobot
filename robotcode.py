from flask import Flask, request, render_template, redirect, url_for, make_response
import time
import RPi.GPIO as GPIO
from gpiozero import LED, Motor, Button, AngularServo
from time import sleep

idle, Forward, Backward, Left, Right, camOnEntry, camOnStay, camTilt, camPan, camCenter, camOff,sensorIdle, sensorDown, sensorOnstay, sensorUP  = range(15)
current = idle
current1='Idle'
#dc motor
motor1 = Motor(forward=23, backward=24)
motor2 = Motor(forward=25, backward=26)

#cam pan tilt
panServo =  AngularServo(26, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
tiltServo =  AngularServo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
panServoAngle = 90
tiltServoAngle = 90
panServo.angle=panServoAngle
tiltServo.angle=tiltServoAngle

#stepper set up
coil1 = Motor(forward=18, backward=23, pwm=False) #sensor stepper
coil2 = Motor(forward=24, backward=17, pwm=False)
forward_seq = ['FF', 'BF', 'BB', 'FB']
reverse_seq = list(forward_seq)  # to copy the list
reverse_seq.reverse()
steps = 800 #stepper motor steps to bring sensor up aand down


#Sensor set up
sensorpin=10 #Edit this to actual sensor pin

led = "Off"
ledPin = LED(21)

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
#page
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<msg>/<value>')
def move(msg, value):
    global panServoAngle
    global tiltServoAngle
    global led
    global current
    global current1
    if msg == 'pan':
        current=idle
        if value == 'left':
            panServoAngle = panServoAngle + 10
        else:
            panServoAngle = panServoAngle - 10
    # os.system("python3 angleServoCtrl.py " + str(panPin) + " " + str(panServoAngle))
    elif msg == 'tilt':
        current = idle
        if value == 'up':
            tiltServoAngle = tiltServoAngle + 10
        else:
            tiltServoAngle = tiltServoAngle - 10
    # os.system("python3 angleServoCtrl.py " + str(tiltPin) + " " + str(tiltServoAngle))
    elif msg == 'led':
        if value == 'on':
            led = "On"
            ledPin.on()
            print("led On")
        else:
            led = "Off"
            ledPin.off()
            print("led Off")
    elif msg =='drive':
        if value == 'forward':
            current = Forward
            drive()
        elif value =='backward':
            current = Backward
            drive()
        elif value =='left':
           current = Left
           drive()
        elif value =='right':
           current = Right
           drive()
    elif msg == 'testSoil':
           current = sensorIdle

def drive():
    if current == idle:
        current1='Idle'
        motor1.stop()
        motor2.stop()
    elif current == Forward:
        current1='Idle'
        motor1.forward(speed=1)
        motor2.forward(speed=1)
    elif current == Backward:
        current1='Forward'
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

    templateData = {
        'panServoAngle': panServoAngle,
        'tiltServoAngle': tiltServoAngle,
        'led': led,
        'current' : current1
    }
    # response = make_response(redirect(url_for('index')))
    # return(response)

    return render_template('index.html', **templateData)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)