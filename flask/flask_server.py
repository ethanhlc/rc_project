#!/usr/bin/env python

from flask import Flask, render_template, Response
import pymysql
import cv2
import time

app = Flask(__name__)

run_once = 0    # run screen capure once
# Setup DB
db = None
cur = None

sql_read = 'SELECT state, temp FROM sec_status ORDER BY time DESC LIMIT 1'

cap = cv2.VideoCapture(-1, cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


# Create video_feed
def video_stream():
    while True:
        _, frame = cap.read()

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Capture Screen when Intruder Detected
def capture_screen():
    global run_once
    if run_once == 0:
        _, screen = cap.read()
        cv2.imwrite('/home/raspberry/rc_project/flask/static/stream_img.jpg',
                    screen)
        run_once = 1


@app.route('/stream')
def security_stream():
    # DB connection
    db = pymysql.connect(host='127.0.0.1', user='root', password='12345678',
                         db='mysql', charset='utf8')
    cur = db.cursor()
    cur.execute(sql_read)
    result = cur.fetchall()
    result = result[0]
    # if alert, change background to yellow
    if result[0] == 'ALERT':
        capture_screen()
        return render_template('alert_stream.html',
                               state=result[0], temp=result[1])
        # alert_html()
    cur.close()

    return render_template('security_stream.html',
                           state=result[0], temp=result[1])


# Deactivate Alarm & save alarm status to alert_off table
@app.route('/deactivate')
def deactivate():
    sql_deactivate = "INSERT INTO alert_off (alarm) VALUES ('Y')"
    # DB connection
    db = pymysql.connect(host='127.0.0.1', user='root', password='12345678',
                         db='mysql', charset='utf8')
    cur = db.cursor()
    cur.execute(sql_deactivate)
    db.commit()

    cur.execute(sql_read)
    result = cur.fetchall()
    result = result[0]
    cur.close()

    return render_template('security_stream.html',
                           state=result[0], temp=result[1])


@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
