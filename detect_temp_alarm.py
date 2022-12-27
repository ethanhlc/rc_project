# Send Kakao MSG if temp detected
# Sound alarm

from os import write
from threading import Semaphore
import RPi.GPIO as GPIO
import spidev
import time
import json
import requests
import pymysql
from picamera import PiCamera

# Setup Code
# Pin Setup
SENSOR_PIN = 5
BUZZER_PIN = 4
LED_PIN = 3

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=False)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzz = GPIO.PWM(BUZZER_PIN, 100)    # change duty to adjust volume

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000

# Setup DB
db = None
cur = None

db = pymysql.connect(host='127.0.0.1', user='root', password='12345678', db='mysql', charset='utf8')

# Setup PiCamera
cam = PiCamera()


# Function Defn
# Take Photo
def take_photo():
    img_file_path = '/home/raspberry/rc_project/flask/static/stream_img.jpg'
    cam.capture(img_file_path)

# Wrie to DB
def write_db(temp, alarm):
    if alarm == 0:
        state = "'OK'"
    elif alarm == 1:
        state = "'ALERT'"
    cur = db.cursor()
    sql_insert = 'INSERT INTO sec_status (state, temp) VALUES (%s, %.2f)' % (state, temp)
    print(sql_insert)
    cur.execute(sql_insert)
    db.commit()


# Read Temp
def temp_read(channel):
    r = spi.xfer2([1, (0x08 + channel) << 4, 0])
    adc_out = ((r[1] & 0x03) << 8) + r[2]
    voltage = adc_out * (3.3 / 1023) * 1000
    temperature = voltage / 10.0

    # write_db(temperature, alarm_state)
    print(temperature)
    return temperature


# Send Kakao MSG
def send_msg():
    # User Token
    usr_token = "WSfKWpGwGYcyDDfcvziVdJHNYF0pv4SLqrOIP1VKCilv1QAAAYVRPGtk"

    now = time.strftime('%x %X', time.localtime())

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + usr_token
    }

    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "Intruder Detected!!\n" + now,
            "link": {
                "web_url": "https://www.google.com",
                "mobile_web_url": "https://www.google.com"
            }
        })
    }

    # send kakao msg
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get('result_code') == 0:
        print('Message send succeeded.')
    else:
        print('Message send failed: ' + str(response.json()))


# Ring Alarm
def alarm_led():
    buzz.start(10)
    GPIO.output(LED_PIN, True)
    time.sleep(0.5)
    buzz.stop()
    GPIO.output(LED_PIN, False)


alarm_state = 0
count = 0

try:
    while True:
        temp = temp_read(SENSOR_PIN)

        if temp > 30:
            alarm_state = 1
            # send_msg()          # send kakao msg
        if alarm_state == 1:
            alarm_led()

        if not (count % 5):
            write_db(temp, alarm_state)
            take_photo()

        count += 1
        time.sleep(1)

        # if alarm_state == 0:
        #     if temp_read(SENSOR_PIN) > 30:
        #         alarm_state = 1
        #         # send_msg()      # send kakao msg
        # else:
        #     alarm_led()     # ring buzzer
        #     temp_read(SENSOR_PIN)

        # time.sleep(1)

except KeyboardInterrupt:
    print('\nSTOP')
    pass

finally:
    spi.close()
    buzz.stop()
    GPIO.cleanup()
    cam.close()
