#!/usr/bin/env python

import RPi.GPIO as GPIO
import spidev
import time
import json
import requests
import pymysql

# Setup Code
# Pin Setup
SENSOR_PIN = 5
BUZZER_PIN = 4
LED_PIN = 3

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=False)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzz = GPIO.PWM(BUZZER_PIN, 100)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000

# Setup DB
db = None
cur = None

db = pymysql.connect(
    host="127.0.0.1", user="root", password="12345678", db="mysql", charset="utf8"
)

# Clear Wrong Input From Table: alert_off
cur = db.cursor()
cur.execute("DELETE FROM alert_off WHERE alarm = 'Y'")
cur.execute("DELETE FROM sec_status WHERE state = 'ALERT'")
db.commit()


# Function Defn
# Read DB alert_off
def check_alert():
    # DB connection
    db = pymysql.connect(
        host="127.0.0.1", user="root", password="12345678", db="mysql", charset="utf8"
    )
    cur = db.cursor()
    sql_read = "SELECT alarm FROM alert_off ORDER BY time DESC LIMIT 1"
    cur.execute(sql_read)
    result = cur.fetchall()
    result = result[0]
    print(result)

    if result[0] == "Y":
        return 1
    else:
        return 0


# Write to DB
def write_db(temp, alarm):
    if alarm == 0:
        state = "'OK'"
    elif alarm == 1:
        state = "'ALERT'"
    cur = db.cursor()
    sql_insert = "INSERT INTO sec_status (state, temp) VALUES (%s, %.2f)" % (
        state,
        temp,
    )
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
    usr_token = "LWSqum5U2nEmv1_0hB94ll7tKr8TI97oc96ukH3lCj1zmwAAAYVWf_Dx"

    now = time.strftime("%x %X", time.localtime())

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + usr_token,
    }

    data = {
        "template_object": json.dumps(
            {
                "object_type": "text",
                "text": "Intruder Detected!!\n" + now,
                "link": {
                    "web_url": "https://www.google.com",
                    "mobile_web_url": "https://www.google.com",
                },
            }
        )
    }

    # send kakao msg
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get("result_code") == 0:
        print("Message send succeeded.")
    else:
        print("Message send failed: " + str(response.json()))


# Send Alarm Deactivated MSG
def send_alarmdone():
    # User Token
    usr_token = "LWSqum5U2nEmv1_0hB94ll7tKr8TI97oc96ukH3lCj1zmwAAAYVWf_Dx"

    now = time.strftime("%x %X", time.localtime())

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + usr_token,
    }

    data = {
        "template_object": json.dumps(
            {
                "object_type": "text",
                "text": "Alarm Deactivated\n" + now,
                "link": {
                    "web_url": "https://www.google.com",
                    "mobile_web_url": "https://www.google.com",
                },
            }
        )
    }

    # send kakao msg
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get("result_code") == 0:
        print("Message send succeeded.")
    else:
        print("Message send failed: " + str(response.json()))


# Ring Alarm
def alarm_led():
    global alarm_state
    buzz.start(10)
    GPIO.output(LED_PIN, True)
    time.sleep(0.5)
    buzz.stop()
    GPIO.output(LED_PIN, False)
    if check_alert() == 1:
        alarm_state = 0
        send_alarmdone()


alarm_state = 0
count = 0

try:
    while True:
        temp = temp_read(SENSOR_PIN)

        if temp > 25:
            alarm_state = 1
            send_msg()  # send kakao msg
        if alarm_state == 1:
            alarm_led()

        if not (count % 3):
            write_db(temp, alarm_state)

        count += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("\nSTOP")
    pass

finally:
    spi.close()
    buzz.stop()
    GPIO.cleanup()
