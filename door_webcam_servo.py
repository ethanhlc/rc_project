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


def triggerSonar():
    pulse_start = 0.0
    pulse_end = 0.0
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
    # servo_control(DOOR_OPEN, 0.1)
    # time.sleep(5)
    # servo_control(DOOR_CLOSED, 0.1)
    # Open door slowly
    for i in range(91, -1, -1):
        servo_control(i, 0.01)
    time.sleep(5)
    for i in range(0, 91, 1):
        servo_control(i, 0.01)


def checkQRCode():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    while True:
        data = ''
        _, frame = cap.read()
        gscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        data, bbox, qr_img = detector.detectAndDecode(gscale)

        supersecretcode = 'helloWorld'

        if data == supersecretcode:
            print('QR code match!!')
            openDoor()
            break

        cv2.imshow('frame', frame)
        cv2.imshow('gray', gscale)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()


servo = GPIO.PWM(servoPin, 50)
servo.start(0)

# cap = cv2.VideoCapture(0)
# detector = cv2.QRCodeDetector()

try:
    while True:
        if triggerSonar() < 30:
            print('object detected')
            checkQRCode()


except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
    # relase camera if exists (KeyboardInterrupt while cam running)
    try:
        cap.release()
    except NameError:
        pass
