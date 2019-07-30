import pymysql
from pprint import pprint
import datetime

from flask import Flask, jsonify, request, make_response, Response

import json

from datetime import datetime, timedelta, date
from pprint import pprint

from pprint import pprint

app = Flask(__name__)
#app.config['JSON_SORT_KEYS'] = False


host = "127.0.0.1"
user = "root"
password = ""
db = "ble_school_security"

@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        #school_id = request.form['school_id']
        _branch_id = request.form['branch_id']
        _floor_id = request.form['floor_id']
        _current_time =  request.form['current_time']

        curr_date = _current_time.split(' ')[0]
        curr_time = (_current_time.split(' ')[1])
        print("Current date -->", curr_date)
        print("Current time -->", curr_time)
        date_obj = datetime.strptime(curr_date, '%Y-%m-%d')
        week_day = date_obj.strftime("%A")
        print(week_day)

        prev_threshold  = datetime.strptime(_current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
        next_threshold = datetime.strptime(_current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
        conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        #sql = "SELECT room_id, class_id, COUNT(student_id) total_green from tbl_attends_students_list where room_id in (Select DISTINCT room_id from tbl_class_time WHERE branch_id = %s AND floor_id =%s AND day = %s AND %s BETWEEN start_time and end_time) GROUP BY room_id"
        sql_total = "Select tct.class_id, tct.room_id, COUNT(tsc.student_id) total_class_students from tbl_class_time  tct INNER JOIN tbl_student_class tsc ON tsc.class_id = tct.class_id WHERE tct.branch_id = %s AND tct.floor_id =%s AND tct.day = %s AND %s BETWEEN tct.start_time and tct.end_time GROUP BY tct.class_id"
        #cursor.execute(sql, (_branch_id, _floor_id, week_day, _current_time))
        cursor.execute(sql_total, (_branch_id, _floor_id, week_day, curr_time))

        rows_total = cursor.fetchall()
        pprint(rows_total)

        sql_present = "SELECT class_id, COUNT(student_id) green_count from tbl_attends_students_list WHERE student_id in (SELECT student_id FROM `tbl_student_class` where class_id in (SELECT class_id from tbl_class_time where branch_id = %s AND floor_id =%s AND day = %s AND %s BETWEEN start_time and end_time GROUP BY class_id)) AND updated_time BETWEEN %s and %s GROUP BY class_id"
        cursor.execute(sql_present, (_branch_id, _floor_id, week_day, curr_time, prev_threshold, next_threshold ))
        rows_present = cursor.fetchall()
        print("rows_present: ")
        pprint(rows_present)
        # for row in rows:
        #     class_id = row['class_id']
        #     sql_total_class_students = "SELECT COUNT(student_id) total_class_students FROM `tbl_student_class` where class_id = %s"
        #     cursor.execute(sql_total_class_students, row['class_id'])
        #     total_class_students = cursor.fetchone()
        #     total_red = total_class_students['total_class_students'] - row['total_green']
        #     print("Total class students ->", total_class_students['total_class_students'])
        #     print("Present students ->", row['total_green'])
        #     print("Outside students ->", total_red)
        #     row['total_red'] = total_red
        #     del row['student_id']
        #     row.pop('class_id', None)

        cursor.close()
        conn.close()
        print("length of rows_present:", len(rows_present))
        room_list = set()

        if len(rows_present) != 0:
            for row_t in rows_total:
                for item in rows_present:
                    if row_t["class_id"] == item["class_id"]:
                        row_t["green_count"] = item["green_count"]
                        row_t["red_count"] = row_t['total_class_students'] - row_t['green_count']
                        # row_t.append(row_t["class_id"])
                        # room_list = room_list + (tuple(row_t["class_id"]))
                        room_list.add(row_t["class_id"])

                        # row_t["process"] = "done"
                        print("\n \n")
                        print("______processing red count______\n",row_t)
                        pass
                    else:
                        if row_t["class_id"] in room_list:
                            pass
                        else:
                            row_t['green_count'] = 0
                            row_t["red_count"] = row_t['total_class_students'] - row_t['green_count']
                            print("\n \n")
                            print("for else",row_t)
            print("\n \n")
            print(rows_total)

            total_students = 0
            total_green = 0
            total_red = 0
            
            for i in rows_total:
                total_students += i['total_class_students']
                total_green += i['green_count']
                total_red += i['red_count']
            # print(total_students)
            # print(total_green)
            # print(total_red)

            response = {"total_students": total_students, "Present": total_green, "total_red": total_red, "student_distribution": rows_total }
            return jsonify(response)

        else:
            for row_t in rows_total:
                row_t["green_count"] = 0
                row_t["red_count"] = row_t['total_class_students'] - row_t['green_count']
            print(rows_total)

            total_students = 0
            total_green = 0
            total_red = 0
            for i in rows_total:
                total_students += i['total_class_students']
                total_green += i['green_count']
                total_red += i['red_count']
            # print(total_students)
            # print(total_green)
            # print(total_red)

            response = {"total_students": total_students, "total_green": total_green, "total_red": total_red, "student_distribution": rows_total }
            return jsonify(response)

    except Exception as e:
        print(e)

        return jsonify({"response": "failed"})





if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0', port=5000)
