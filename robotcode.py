from gpiozero import Motor,Button,AngularServo
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
sensor = 3
GPIO.setup(sensor, GPIO.IN)

Idle, Forward, Backward, Left, Right, camOnEntry, camOnStay, camTilt, camPan. camCenter, camOff,sensorIdle, sensorDown, sensorOnstay, sensorUP  = range(15)
current = Idle
sensorCurrent=sensorIdle
camCurrent == camOnEntry

motor1 = Motor(forward=23, backward=24)
motor2 = Motor(forward=25, backward=26)
servo1 = AngularServo(26, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo2 = AngularServo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

FPB = Button(18)
BPB = Button(19)
LPB = Button(20)
RPB = Button(21)
servoButton1 =Button(15)
servoButton2 =Button(14)
servoButton3 =Button(13)
servoButton4 =Button(12)
measureSoil =Button(11)

coil1 = Motor(forward=18, backward=23, pwm=False) #sensor stepper
coil2 = Motor(forward=24, backward=17, pwm=False)

forward_seq = ['FF', 'BF', 'BB', 'FB']
reverse_seq = list(forward_seq)  # to copy the list
reverse_seq.reverse()
steps = 800

def measureSoilButton():
    sensorDown()
    Timer(5, timerSensor).start()

def timerSensor():
    global current
    current = sensorOnstay

measureSoil.when_pressed= measureSoilButton
def sensorGoesDown():
    for i in range(steps):
        for step in forward_seq:
            set_step(step)

def sensorGoesUp():
    for i in range(steps):
        for step in reverse_seq:
            set_step(step)

def servo1Press():
    servo1.angle += 5

def servo2Press():
    servo1.angle -= 5

def servo3Press():
    servo2.angle += 5

def servo4Press():
    servo2.angle -= 5

servoButton1.when_pressed= servo1Press
servoButton2.when_pressed= servo2Press
servoButton3.when_pressed= servo3Press
servoButton4.when_pressed= servo4Press

def FPBpressed():
    global current
    print("FPBpressed")
    if current == Idle:
        current = Forward

FPB.when_pressed = FPBpressed

def BPBpressed():
    global current
    print("BPBpressed")
    if current == Idle:
        current = Backward

BPB.when_pressed = BPBpressed

def LPBpressed():
    global current
    print("LPBpressed")
    if current == Idle:
        current = Left
LPB.when_pressed = LPBpressed

def RPBpressed():
    global current
    print("RPBpressed")
    if current == Idle:
        current = Right
RPB.when_pressed = RPBpressed


def drive():
    if current == Idle:
        motor1.stop()
        motor2.stop()
    elif current == Forward:
        camCurrent = camOnEntry
        motor1.forward(speed=speed)
        motor2.forward(speed=speed)
    elif current == Backward:
        motor1.backward(speed=speed)
        motor2.backward(speed=speed)
    elif current == Left:
        motor1.forward(speed=speed)
        motor2.backward(speed=speed)
    elif current == Right:
        motor1.backward(speed=speed)
        motor2.forward(speed=speed)

def moveCam():
    if camCurrent == camOnEntry:
        servo1.angle = 0
        servo2.angle = 0

def stepper():
    global current
    if current== sensorIdle:
        print("Idle")
    elif current == sensorDown:
        sensorGoesDown()
        current=sensorOnstay
    elif current == sensorOnstay:
        moisturevalue = GPIO.input(pin)
        if moisturevalue == 0:
            print("Moisture detected")
        elif moisturevalue == 1:
            print("Moisture NOT detected")
        moistureCurrent=sensorUP
    elif current == sensorUP:
        sensorGoesUp()
        current=sensorIdle

while True:
    drive()
    moveCam()
    stepper()