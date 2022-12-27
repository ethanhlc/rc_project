from flask import Flask, render_template
import pymysql
import time

# Setup DB
db = None
cur = None

sql_read = 'SELECT state, temp FROM sec_status ORDER BY time DESC LIMIT 1'

app = Flask(__name__)


@app.route('/stream')
def security_stream():
    # DB connection
    db = pymysql.connect(host='127.0.0.1', user='root', password='12345678', db='mysql', charset='utf8')
    cur = db.cursor()
    cur.execute(sql_read)
    result = cur.fetchall()
    result = result[0]
    cur.close()

    return render_template('security_stream.html', state=result[0], temp=result[1])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
