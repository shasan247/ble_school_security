import pymysql
from pprint import pprint
import datetime

from flask import Flask, jsonify, request, make_response, Response

import json
import calendar

from datetime import datetime, timedelta, date
from pprint import pprint

from pprint import pprint

app = Flask(__name__)
#app.config['JSON_SORT_KEYS'] = False


host = "127.0.0.1"
user = "root"
password = ""
db = "dmabdcom_school_security"


#--------------------------------------Notification--------------------------------------------------
@app.route('/notification', methods=['POST'])
def notificationapi():
    # current_time = request.form['current_time']
    # branch_id = request.form['branch_id']
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:

        sql ="SELECT `status_type`, `status`FROM `tbl_notification_status_check` WHERE 1"
        cursor.execute(sql)
        status = cursor.fetchall()

        # print(json.dumps(status, sort_keys=True, indent=4))
        # print(status)
        # return jsonify({'brachList' : users, 'branch_status': 'True', 'error_msg': 'No error'})
        
        response= {"result" : status}
        return jsonify(response)
    except Exception as e:
        return jsonify(e)


#-----------------------------------------------------------------------------------------

#----------------------------------login API------------------------------

@app.route('/login', methods=['POST'])                     
def login_with_approval():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        user_name = request.form['user_name']
        password_login = request.form['password']
        fcm_token = request.form['token']
        if user_name != "" and password_login != "" :
            sql ="SELECT user_name, user_id, school_id, password FROM tbl_user where user_name=%s and password=%s"
            cursor.execute(sql,(user_name,password_login))

            if(cursor.rowcount>0):
                users = cursor.fetchall()

                user_data = json.dumps(users)
                user_data2 = json.loads(user_data)

                for userall in user_data2:
                    if userall["user_name"] == user_name and userall["password"] == password_login:
                    	res=[{"user_id": userall["user_id"], "user_name": userall["user_name"], "school_id": userall["school_id"]}]
                    	role_chk_query = "SELECT role_type FROM tbl_user_role LEFT JOIN tbl_user ON tbl_user_role.role_id = tbl_user.role_id WHERE tbl_user.user_name=%s AND tbl_user.password = %s"
                    	cursor.execute(role_chk_query,(user_name,password_login))
                    	print("ROLE ---")
                    	if(cursor.rowcount>0):
                    		role = cursor.fetchall()
                    		role_1 = json.dumps(role)
                    		role_2 = json.loads(role_1);print(role_2);print(type(role_2));
                    		for dataall in role_2:
                    			if dataall["role_type"] == None:
                    				print("Undefined role")
                    				res=[{"user_id": userall["user_id"], "user_name": userall["user_name"], "school_id": userall["school_id"],"role_type": ""}]
                    				return jsonify({"Login_info ":[], "Login_status": "False", "error_msg": "Undefined role"})
                    			else:
                    				print("Defined Role")
		                    		print("Updating in DB")
		                    		update_query = "UPDATE tbl_user SET fcm_token= (%s) where user_name = (%s) and password=(%s)"
		                    		print("Updating query is ok")
		                    		cursor.execute(update_query , (fcm_token,user_name,password_login))
		                    		print("Updating query executed")
		                    		result = conn.commit()
		                    		print("FCM TOken updated in User table!!")
		                    		res=[{"user_id": userall["user_id"], "user_name": userall["user_name"], "school_id": userall["school_id"],"role_type": dataall["role_type"]}]
                    				return jsonify({"Login_info ":res, "Login_status": "True", "error_msg": "No error"})
                    	else:
                    		return jsonify({"Login_info ":[], "Login_status": "False", "error_msg": "No role found"})
                        # return jsonify(res)
                    else:
                        #pass
                        login_arr = []
                        return jsonify({"Login_info ":login_arr, "Login_status": "False", "error_msg": "Wrong userName or password!"})        
            else:
                login_arr = []
                return jsonify({"Login_info ":login_arr, "Login_status": "False", "error_msg": "Wrong userName or password!"})
        else:
            res={"response": "Required field is empty!!!"}
            return jsonify(res)

    except Exception as e:
        print (e)
    cursor.close()  

# # ----------------------------------

#-------------------------------------------QR scan <-code below->------------------------------------


@app.route('/qrcode', methods=['POST']) 

def qrcode():
	conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
	cursor = conn.cursor()
	
	qr_id = request.form['qr_id']
	print(qr_id)
	print(type(qr_id))

	try:

		sql = "SELECT beacon_id from tbl_entry_beacon where qr_id=%s AND status=0"
	
		cursor.execute(sql, qr_id)
		data = cursor.fetchone()
		print(data)
		if data == None:
			return jsonify({"error": "true", "description": "beacon id not available", "beacon_id": ""})
		return jsonify({"error": "false", "description": "beacon_id available", "beacon_id": data['beacon_id']})

	except Exception as e:
		return jsonify({"error": "true", "description": "error in server:"+ str(e), "beacon_id": ""})
		print (e)
		


# ----------------------------------------------------------------------------------------------------------

# ------------------------------------registration <-code below->-------------------------------------------

@app.route('/reg', methods=['POST'])                     
def student_registration():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        qr_id=request.form['qr_id']
        beacon_id = request.form['beacon_id']
        student_id = request.form['student_id']
        student_first_name = request.form['student_first_name']
        student_last_name = request.form['student_last_name']
        blood_group = request.form['blood_group']
        address = request.form['address']
        contact = request.form['contact']
        school_id = request.form['school_id']
        branch_id = request.form['branch_id']
        mode_of_transport = request.form['mode_of_transport']

		
        if beacon_id!="" and student_id!="" and student_first_name!="" and student_last_name!="" and blood_group!="" and address!="" and contact!="" and school_id!="" and branch_id!="":
            print("Parameters Okay")
            sql = "INSERT INTO tbl_student_info(qr_id,beacon_id,student_id, student_first_name, student_last_name, blood_group, address, contact, school_id, branch_id, mode_of_transport) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            values = (qr_id,beacon_id,student_id,student_first_name,student_last_name,blood_group,address,contact,school_id,branch_id,mode_of_transport)
            cursor.execute(sql, values)
            conn.commit()
            update_query = "UPDATE tbl_entry_beacon SET status= (%s) where beacon_id = (%s)"
            cursor.execute(update_query , ('1',beacon_id))
            print("Updating query executed")
				
            print(cursor.rowcount)
            if(cursor.rowcount >0):
                conn.commit()
                print("Status updated")
                return jsonify({"description": "reg success and status change", "error": "false", "data" : mode_of_transport})
            else:
                print(" no Status updated")
                return jsonify({"description": "failure", "error": "true", "data" : ""})
            # else:
            #     return jsonify({"description": "reg unsuccess", "error": "true", "data" : ""})
        else:
            return jsonify({"description": "Parameters empty!", "error": "true", "data" : ""})
    except Exception as e:
        print (e)
# ----------------------------------------------------------------------------------------------------------

@app.route('/self', methods=['POST'])                     
def student_self():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        student_id = request.form['student_id']
        vehiclePlate = request.form['vehiclePlate']
        car_model = request.form['car_model']
        

		
        if student_id!="" and vehiclePlate!="" and car_model!="" :
            print("Parameters Okay")
            sql = "INSERT INTO tbl_whitelistvehicle( student_id,vehiclePlate, car_model) VALUES (%s,%s,%s)"
            values = ( student_id,vehiclePlate,car_model)
            cursor.execute(sql, values)

            if(cursor.rowcount >0):
                conn.commit()
                print("Status updated")
                return jsonify({"description": "Registration Successful", "error": "false", "data" : "Success"})
            else:
                print(" no Status updated")
                return jsonify({"description": "failure", "error": "true", "data" :""})
            
        else:
            return jsonify({"description": "Parameters empty!", "error": "true", "data" :""})
    except Exception as e:
        print (e)
        
# ----------------------------------------------------------------------------------------------------------

@app.route('/drop_off', methods=['POST'])                     
def student_drop_off():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        student_id = request.form['student_id']
        vehiclePlate = request.form['vehiclePlate']
        car_model = request.form['car_model']
        owner = request.form['owner']
        gurdian_name_one = request.form['gurdian_name_one']
        gurdian_name_two = request.form['gurdian_name_two']
        

        if student_id!="" and vehiclePlate!="" and car_model!="" and owner!="" and gurdian_name_one!="" and gurdian_name_two!="" :
            print("Parameters Okay")
            sql = "INSERT INTO tbl_whitelistvehicle(student_id, vehiclePlate, car_model,owner,gurdian_name_one,gurdian_name_two) VALUES (%s,%s,%s,%s,%s,%s)"
            values = (student_id,vehiclePlate,car_model,owner,gurdian_name_one,gurdian_name_two)
            cursor.execute(sql, values)

            if(cursor.rowcount >0):
                conn.commit()
                print("Status updated")
                return jsonify({"description": "Registration Successful", "error": "false", "data" : "Success"})
            else:
                print(" no Status updated")
                return jsonify({"description": "failure", "error": "true", "data" :""})
     
        else:
            return jsonify({"description": "Parameters empty!", "error": "true", "data" :""})
    except Exception as e:
        print (e)

# ----------------------------------------------------------------------------------------------------------


# #-----------------All branch student count-------------------

@app.route('/overall_std_count', methods=['POST'])
def stdcount():

    current_time = request.form['current_time']
    print(current_time)
    
    prev_threshold  = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
    next_threshold = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    

    sql_total = "SELECT COUNT(tasl.student_id) std_count, tasl.branch_id, tb.branch_name FROM `tbl_attends_students_list` tasl INNER JOIN tbl_branch tb on tasl.branch_id = tb.branch_id where tasl.updated_time BETWEEN %s and %s GROUP by branch_id"
    cursor.execute(sql_total, (prev_threshold,next_threshold))

    rows_total = cursor.fetchall()
    print(rows_total)

    cursor.close()
    conn.close()

    response= {"total student count" : rows_total}

    return jsonify(response)



@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        #school_id = request.form['school_id']
        branch_id = request.form['branch_id']
        floor_id = request.form['floor_id']
        current_time =  request.form['current_time']

        curr_date = current_time.split(' ')[0]
        curr_time = (current_time.split(' ')[1])
        print("Current date -->", curr_date)
        print("Current time -->", curr_time)
        date_obj = datetime.strptime(curr_date, '%Y-%m-%d')
        week_day = date_obj.strftime("%A")
        print(week_day)
     

        prev_threshold  = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
        next_threshold = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
        conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        

        #sql = "SELECT room_id, class_id, COUNT(student_id) total_green from tbl_attends_students_list where room_id in (Select DISTINCT room_id from tbl_class_time WHERE branch_id = %s AND floor_id =%s AND day = %s AND %s BETWEEN start_time and end_time) GROUP BY room_id"
        sql_total = "Select tct.class_id, tct.branch_id,tct.room_id, COUNT(tsc.student_id) total_class_students from tbl_class_time  tct INNER JOIN tbl_student_class tsc ON tsc.class_id = tct.class_id WHERE tct.branch_id = %s AND tct.floor_id =%s AND tct.day = %s AND %s BETWEEN tct.start_time and tct.end_time GROUP BY tct.class_id"
        #cursor.execute(sql, (branch_id, floor_id, week_day, _current_time))
        cursor.execute(sql_total, (branch_id, floor_id, week_day, curr_time))
        print('-------------------------------')

        rows_total = cursor.fetchall()
        pprint(rows_total)

        sql_present = "SELECT class_id, COUNT(student_id) green_count from tbl_attends_students_list WHERE student_id in (SELECT student_id FROM `tbl_student_class` where class_id in (SELECT class_id from tbl_class_time where branch_id = %s AND floor_id =%s AND day = %s AND %s BETWEEN start_time and end_time GROUP BY class_id)) AND updated_time BETWEEN %s and %s GROUP BY class_id"
        cursor.execute(sql_present, (branch_id, floor_id, week_day, curr_time, prev_threshold, next_threshold ))
        rows_present = cursor.fetchall()
        print("rows_present: ")
        pprint(rows_present)
   

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
# #------------------------------------------Dashboard-------------------------------------------



@app.route('/room_details', methods=['POST'])
def room_details():

    branch_id = request.form['branch_id']
    room_id = request.form['room_id']
    current_time = request.form['current_time']


    #branch_id = 1
    #room_id = 1
    #current_time ='2019-03-04 10:13:52'

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])
    print("Current time is-->", curr_time)

    curr_date = datetime.strptime(curr_date, '%Y-%m-%d')

    day = calendar.day_name[curr_date.weekday()]  #'Wednesday'
    print("day is --->", day)

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()
    try:

        #-----------------find room_id
        sql = ("SELECT room_no FROM tbl_room where room_id = '%s'" %(room_id))
        cursor.execute(sql)
        room_name = cursor.fetchone()
        print(room_name)
        if(str(room_name)=='None'):
            response = {
                'error' : 'true',
                'error msg': 'No room name found',
                'room_name': '',
                'room_details': []             

            }



            return jsonify(response)
            cursor.close()        
        else:
            room_name = room_name[0]
            #-----------------Find class id, subject and teacher's name ------------------------------------
            sql = ("SELECT class_id, subject, teacher from tbl_class_time where room_id = ('%s') and start_time<='%s' and '%s'<=end_time and day='%s'" %(room_id, curr_time, curr_time, day))
            cursor.execute(sql)
            class_id_arr = cursor.fetchone()

            student_list = []

            if(str(class_id_arr)=='None'):
                response = {
                'error' : 'true',
                'error msg': 'Wrong room id',
                'room_name': '',
                'room_details': []             

                }

                return jsonify(response)
                cursor.close()
            else:


                class_id = class_id_arr[0]
                subject = class_id_arr[1]
                teachers_name = class_id_arr[2]

                print("class id is-->", class_id)
                print("Subject name --->", subject)
                print("teachers_name-->", teachers_name)

                #-----------------Find class id, subject and teacher's name ------------------------------------

                #---------- Find present student list------------------------------
                cursor.execute("SELECT start_time FROM tbl_class_time WHERE class_id = ('%s') AND branch_id = ('%s')" %(class_id, branch_id))
                class_data = cursor.fetchone()

                if(str(class_data) == 'None'):
                    response = {
                    'error' : 'true',
                    'error msg': 'This is break time',
                    'room_name': '',
                    'room_details': []             

                    }

                    return jsonify(response)
                    cursor.close()

                else:
                    class_time = class_data[0]
                    present_time = class_time + timedelta(minutes=10)
                    # print(present_time)
                    sql = ("SELECT tsi.student_id,tsi.student_first_name,tsi.student_last_name,tsi.contact,DATE(tasl.updated_time),TIME(tasl.updated_time), tasl.room_id FROM tbl_attends_students_list as tasl JOIN tbl_student_info as tsi ON tsi.id=tasl.student_id  WHERE tasl.class_id = ('%s') AND tasl.branch_id = ('%s') AND tasl.room_id = ('%s') AND TIME(tasl.updated_time) >= ('%s') AND DATE(tasl.updated_time)=('%s')" %(class_id, branch_id, room_id, curr_time,curr_date))
                    print(sql)
                    cursor.execute(sql)
                    rows_affected_present=cursor.rowcount
                    print("Present is---?>", rows_affected_present)

                    if(rows_affected_present>0):
                        students_present = cursor.fetchall()
                        print("----------------?>")
                        print(students_present)
                        print(type(room_name))
                        print("----------------?>")
                        for row in students_present:
                            student_list.append({
                                "student_id": row[0], 
                                "student_name":row[1]+ " " +row[2],
                                #'present': 'true',
                                #'absent' : 'false',
                                #'remarks' : '',
                                'class_name' : subject,
                                'attendance' : 'present',
                                'current_loc' : room_name,
                                'date' : str(row[4]),
                                'time' : str(row[5])

                                })
                    #---------- Find present student list------------------------------

                    #---------- Find Absent student list------------------------------
                    sql = "SELECT student_id FROM tbl_student_class WHERE class_id = %s AND student_id NOT IN(SELECT student_id FROM tbl_attends_students_list WHERE TIME(updated_time)>='%s' AND DATE(updated_time)= '%s' and class_id = %s and room_id = %s)" %(class_id, curr_time, curr_date, class_id, room_id)

                    print(sql)
                    cursor.execute(sql)

                    rows_affected_absent = cursor.rowcount
                    print("Absent List-->", rows_affected_absent)

                    if rows_affected_absent > 0:
                        students = cursor.fetchall()
                        print(students)



                        for student in students:
                            print(student)
                            student_id = student[0]
                            print(student_id)

                            sql = ("SELECT student_id,student_first_name,student_last_name,contact FROM tbl_student_info WHERE id = ('%s')" %(student_id))
                            print(sql)
                            cursor.execute(sql)


                            data = cursor.fetchone()
                            if(str(data) == "None"):
                                pass
                            else:
                                print(data)
                                student_id_ = data[0]
                                student_first_name = data[1]
                                student_last_name = data[2]
                                class_name = subject
                                #print(student_id_,student_first_name,student_last_name,class_name)



                                sql = "SELECT class_id, room_id, TIME(updated_time) , DATE(updated_time) FROM tbl_attends_students_list WHERE student_id = %s AND TIME(updated_time)>='%s' AND DATE(updated_time)= '%s'" %(student_id, curr_time, curr_date)
                                print(sql)
                                cursor.execute(sql)
                                #if cursor.rowcount > 0:
                                data2 = cursor.fetchone()
                                    #print(data2)

                                if(data2== None):

                                    student_list.append({
                                    "student_id": student_id_, 
                                    "student_name":data[1]+ " " +data[2],
                                    'class_name' : subject,
                                    'attendance' : 'absent',
                                    'current_loc' : 'outside campus',
                                    'date' : str(curr_date).split(' ')[0],
                                    'time' : str(curr_time)

                                    })

                                else:                                     
                                    sql = "SELECT room_no FROM tbl_room WHERE room_id = '%s'" %(data2[1])
                                    print(sql)
                                    cursor.execute(sql)
                                    #if cursor.rowcount > 0:
                                    data3 = cursor.fetchone()

                                    if data3 != None:
                                        room = data3[0]
                                    else:
                                        room = 'unknown'

                                    

                                    student_list.append({
                                        "student_id": student_id_, 
                                        "student_name":data[1]+ " " +data[2],
                                        'class_name' : subject,
                                        'attendance' : 'absent',
                                        'current_loc' : room,
                                        'date' : str(row[4]),
                                        'time' : str(row[5])

                                        })



                    room_details ={
                        'error' : 'false',
                        'error msg': '',
                        'room_name': room_name,
                        'room_details': student_list  
                        }

                    return jsonify(room_details)
                    cursor.close()
                                #---------- Find Absent student list------------------------------
            
    except Exception as e:
        print (e)
#-----------------------------------Room details API------------------------------

# #----------------------------------------bullying_notification----------------------------------------------

app.route('/bullying_history', methods=['POST'])
def stdcount():

    current_time = request.form['current_time']
    print(current_time)
    
    prev_threshold  = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=1000)
    next_threshold = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=60)
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    

    sql_total = "SELECT br.branch_name, f.floor_no, si.`student_first_name`, si.`student_id`, anl.time, gt.zone_id FROM tbl_entry_gateway gt INNER JOIN tbl_branch br ON br.branch_id = gt.branch_id INNER JOIN tbl_floor f ON f.floor_id = gt.floor_id INNER JOIN tbl_acc_notification anl ON anl.gateway_id = gt.gateway_id INNER JOIN tbl_student_info si ON si.`beacon_id` = anl.beacon_id WHERE anl.movement_status = 'Please Check!!!' AND anl.time BETWEEN %s AND %s"
    cursor.execute(sql_total, (prev_threshold,next_threshold))

    rows_total = cursor.fetchall()
    print(rows_total)

    cursor.close()
    conn.close()

    response= {"total student count" : rows_total}

    return jsonify(response)


# #----------------------------------------------------------------------------------------------

#-------------------------------------------------------------id_card-----------------------------------------------------------------
@app.route('/id_card', methods=['POST'])
def idcard():

    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    student_id = request.form['student_id']

    sql_total = "Select student_first_name,student_last_name,gurdian_name,contact,class FROM tbl_student_info WHERE student_id = %s"
    
    cursor.execute(sql_total, (student_id))

    rows_total = cursor.fetchone()
    print(rows_total)

    cursor.close()
    conn.close()

    return jsonify(rows_total)

#-----------------------------------------------------------id_card--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0', port=5000)