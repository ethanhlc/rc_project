import RPi.GPIO as GPIO
import time
import cv2

# set GPIO pins
trig = 3
echo = 2

servoPin = 4
SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 2
DOOR_CLOSED = 90
DOOR_OPEN = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(trig, GPIO.OUT, initial=False)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(0)

def servo_control(degree, delay):
    if degree > 180:
        degree = 180

    duty = SERVO_MIN_DUTY + \
        (degree * (SERVO_MAX_DUTY - SERVO_MIN_DUTY) / 180.0)

    # print("Degree: {} to {}(Duty)".format(degree, duty))

    servo.ChangeDutyCycle(duty)
    time.sleep(delay)


def openDoor():
    # Open door quickly
    # servo_control(DOOR_OPEN, 0.1)
    # time.sleep(5)
    # servo_control(DOOR_CLOSED, 0.1)
    # Open door slowly
    for i in range(100, 9, -1):
        servo_control(i, 0.01)
    time.sleep(5)
    for i in range(10, 101, 1):
        servo_control(i, 0.01)


openDoor()
GPIO.cleanup()
