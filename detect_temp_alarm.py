# Send Kakao MSG if temp detected
# Sound alarm

import RPi.GPIO as GPIO
import spidev
import time
import json
import requests

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


# Function Defn
# Read Temp
def temp_read(channel):
    r = spi.xfer2([1, (0x08 + channel) << 4, 0])
    adc_out = ((r[1] & 0x03) << 8) + r[2]
    voltage = adc_out * (3.3 / 1023) * 1000
    temperature = voltage / 10.0

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

try:
    while True:
        if alarm_state == 0:
            if temp_read(SENSOR_PIN) > 30:
                alarm_state = 1
                # send_msg()      # send kakao msg
        else:
            alarm_led()     # ring buzzer

        time.sleep(1)

except KeyboardInterrupt:
    print('\nSTOP')
    pass

finally:
    spi.close()
    buzz.stop()
    GPIO.cleanup()
