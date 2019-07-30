from flask import Flask, render_template, request
from flask import jsonify
import pymysql




from random import randint
import pymysql
import json


from datetime import datetime, timedelta, date
app = Flask(__name__)
host = "127.0.0.1"
user = "root"
password = ""
db = "dmabdcom_school_security"
conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()



@app.route('/bullying_notification', methods=['POST'])
def idcard():

    current_time = request.form['current_time']

    print(current_time)
    
    
    prev_threshold  = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
    next_threshold = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    
    sql_total = "SELECT tan.time, tt.temp, tr.room_no, teg.room_id, tsi.student_first_name, tsi.student_id, tan.movement_status FROM tbl_acc_notification tan INNER JOIN tbl_student_info tsi ON tan.beacon_id=tsi.beacon_id INNER JOIN tbl_entry_gateway teg ON tan.gateway_id=teg.gateway_id INNER JOIN tbl_room tr ON tr.room_id= teg.room_id INNER JOIN tbl_temp tt ON tt.beacon_id=tan.beacon_id WHERE tan.TIME BETWEEN %s AND %s AND tan.movement_status = 'High' AND tan.id in (SELECT Max(tan.id) FROM tbl_acc_notification tan Where tan.TIME BETWEEN %s AND %s AND tan.movement_status = 'High' GROUP BY tan.beacon_id ) GROUP BY tan.beacon_id"
    
    cursor.execute(sql_total, (prev_threshold,next_threshold,prev_threshold,next_threshold))



    rows_total = cursor.fetchall()
    print(rows_total)

    cursor.close()
    conn.close()

    return jsonify(rows_total)

if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0', port=5000)