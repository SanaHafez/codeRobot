from flask import Flask, request, render_template, redirect, url_for, make_response
import time
import RPi.GPIO as GPIO
from gpiozero import LED, Motor, Button, AngularServo
from time import sleep

idle, Forward, Backward, Left, Right, camOnEntry, camOnStay, camTilt, camPan, camCenter, camOff,sensorIdle, sensorDown, sensorOnstay, sensorUP  = range(15)
current = idle

motor1 = Motor(forward=23, backward=24)
motor2 = Motor(forward=25, backward=26)
panServo =  AngularServo(26, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
tiltServo =  AngularServo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

coil1 = Motor(forward=18, backward=23, pwm=False) #sensor stepper
coil2 = Motor(forward=24, backward=17, pwm=False)
forward_seq = ['FF', 'BF', 'BB', 'FB']
reverse_seq = list(forward_seq)  # to copy the list
reverse_seq.reverse()
panServoAngle = 90
tiltServoAngle = 90
sensorpin=10 #Edit this to actual sensor pin
panServo.angle=panServoAngle
tiltServo.angle=tiltServoAngle
led = "Off"
ledPin = LED(21)

steps = 800 #stepper motor steps to bring sensor up aand down

def timerSensor():
    global current
    current = sensorOnstay

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
        if value == 'forward'
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
        motor1.stop()
        motor2.stop()
    elif current == Forward:
        motor1.forward(speed=1)
        motor2.forward(speed=1)
    elif current == Backward:
        motor1.backward(speed=1)
        motor2.backward(speed=1)
    elif current == Left:
        motor1.forward(speed=1)
        motor2.backward(speed=1)
    elif current == Right:
        motor1.backward(speed=1)
        motor2.forward(speed=1)


def stepper():
    global current
    if current == sensorIdle:
        print("Idle")
    elif current == sensorDown:
        sensorGoesDown()
        current = sensorOnstay
    elif current == sensorOnstay:
        moisturevalue = GPIO.input(pin)
        if moisturevalue == 0:
            print("Moisture detected")
        else:
            print("Moisture NOT detected")
            moistureCurrent = sensorUP
    elif current == sensorUP:
        sensorGoesUp()
        current = sensorIdle

    templateData = {
        'panServoAngle': panServoAngle,
        'tiltServoAngle': tiltServoAngle,
        'led': led
    }
    # response = make_response(redirect(url_for('index')))
    # return(response)

    return render_template('index.html', **templateData)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080, threaded=True)