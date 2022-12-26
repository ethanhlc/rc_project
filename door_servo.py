import RPi.GPIO as GPIO
import time

# set pins for peripherals
trig = 3
echo = 2

servoPin = 4
SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(trig, GPIO.OUT, initial=False)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(0)


def triggerSonar():
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start        # time difference
    distance = pulse_duration * (340 * 100) / 2     # distance calc in cm
    # round distance to 2 decimals
    distance = round(distance, 2)

    return distance


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
    servo_control(90, 0.1)
    time.sleep(5)
    servo_control(0, 0.1)
    # Open door slowly
    # for i in range(0, 91, 10):
    #     servo_control(i, 0.2)
    # time.sleep(5)
    # for i in range(90, -1, -10):
    #     servo_control(i, 0.2)


try:
    while True:
        if triggerSonar() < 20:
            print('object detected')
            openDoor()

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
