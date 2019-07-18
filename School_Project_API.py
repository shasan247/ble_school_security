from flaskext.mysql import MySQL
from flask import Flask, request, make_response, Response
import pymysql
import datetime
import json
from flask import jsonify
from datetime import datetime, timedelta, date
import calendar

from pprint import pprint
from pytz import timezone 

from flask import Flask, render_template, request


from random import randint

import os
import base64

app = Flask(__name__)
#host = "127.0.0.1"
#user = "root"
#password = ""
#db = "db_ble_school_project"

host = '127.0.0.1'
port = 3306
user = 'root'
password = ''
db = 'ble_school_security'

#conn = pymysql.connect(host=host, user=user, password=password, db=db,cursorclass=pymysql.cursors.DictCursor)

#cursor = conn.cursor() 

@app.route('/', methods=['GET'])                     
def hello():
    return "hello"

#--------------------------------------building_wise_std--------------------------------------------------
@app.route('/building_wise_std', methods=['POST'])
def buildingwisestd():

    current_time = request.form['current_time']
    branch_id = request.form['branch_id']

    print(current_time)
    
    prev_threshold  = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
    next_threshold = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    

    sql_total = "SELECT COUNT(tasl.student_id) std_count, tasl.room_id FROM `tbl_attends_students_list` tasl where tasl.branch_id= %s and tasl.updated_time BETWEEN %s and %s GROUP by room_id"
    cursor.execute(sql_total, (branch_id,prev_threshold,next_threshold))

    rows_total = cursor.fetchall()
    print(rows_total)

    cursor.close()
    conn.close()

    response= {"Building Wise Student" : rows_total}

    return jsonify(response)


#-----------------------------------------------------------------------------------------


#----------------------------------------bullying_notification----------------------------------------------

@app.route('/bullying_notification', methods=['POST'])
def bullying_notification():

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


#----------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------------------------------------------
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

# ----------------------------------

# --------------------------------------------------------------------------------------------



# ---------------------------------Branch List <-code below->---------------------------------

@app.route('/branch', methods=['POST'])                     
def branchList():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        school_id = request.form['school_id']
        
        if school_id != "" :       
            sql ="SELECT branch_id, branch_name,longitude, latitude FROM tbl_branch where school_id=%s" %(school_id)
            cursor.execute(sql)
            
            if(cursor.rowcount>0):
                users = cursor.fetchall()
                return jsonify({'brachList' : users, 'branch_status': 'True', 'error_msg': 'No error'})
            else:
                blank_branch = []
                #res= {"response": "School ID didn't match!"}
                res =  {'brachList' : blank_branch, 'branch_status': 'False', 'error_msg': 'No branch list to show'}
            return jsonify(res)
        else:
            return jsonify({"branch_status" : "False", "error_msg" : "No branch list to show! Please select a School ID."})
        
        
    except Exception as e:
        print (e)

    cursor.close()  


# -----------------------------------------------------------------------------------------
# --------------------------------Floor List <-code below->--------------------------------


# --------------------------------Floor List <-code below->--------------------------------


@app.route('/floor', methods=['POST'])                     
def floorList():
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    try:
        branch_id = request.form['branch_id']
        school_id = request.form['school_id']
        
        if branch_id != "" and school_id !="" :   
            
            sql = "SELECT tbl_floor.floor_id, tbl_floor.floor_no FROM tbl_floor JOIN tbl_branch ON tbl_floor.branch_id = tbl_branch.branch_id WHERE tbl_branch.school_id = '%s' and tbl_branch.branch_id = '%s'" %(school_id,branch_id)
            cursor.execute(sql)
            
            if(cursor.rowcount>0):
                floors = cursor.fetchall()
                return jsonify({'floor_list' : floors, 'floor_status': 'True', 'error_msg': 'No error'})
            else:
                blank_floor = []
                res= {"floorList" : blank_floor, "floor_status" : "False", "error_msg" : "There is no floor list!"}
            return jsonify(res)
        else:
            return jsonify({"floor_status" : "False", "error_msg" : "No floor list to show! Please select both School and Branch ID."})
        
            
    except Exception as e:
        print (e)


#SELECT tbl_floor.floor_id, tbl_floor.floor_no FROM `tbl_floor` JOIN `tbl_branch` ON tbl_floor.branch_id = tbl_branch.branch_id WHERE tbl_branch.school_id = 1 and tbl_branch.branch_id = 1 
# ----------------------------------------------------------------------------------------------

#---------------------------------Get No of students-------------------------------------

@app.route('/no_of_students', methods=['POST'])
def no_of_students():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()
    #school_id = request.form['school_id']
    branch_id = request.form['branch_id']
    floor_id = request.form['floor_id']
    current_time =  request.form['current_time']

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])
    print("Current time is-->", curr_time)

    #--------------------Get room id and room no ina floor---------------------------------

    sql = "SELECT tbl_room.room_id, tbl_room.room_no FROM `tbl_room` JOIN `tbl_floor` ON tbl_floor.floor_id = '%s' AND tbl_floor.floor_id = tbl_room.floor_id WHERE tbl_floor.branch_id = '%s'"%(floor_id, branch_id)
    cursor.execute(sql)
    #users = cursor.fetchall()
    #print(users[0])

    room_id_list = []
    romm_no_list = []

    i= 0
    for row in cursor.fetchall():
        room_id_list.append(row[0])
        romm_no_list.append(row[1])

    #current_time = '2019-03-04 10:52:51'
    data2 = []
    #updated_time  = '2019-03-04 10:53:53'
    #--------------------Get room id and room no in a floor---------------------------------
    for row in room_id_list:
        print(row)
        sql = "SELECT student_id FROM `tbl_attends_students_list` where room_id='%s' AND TIME(updated_time)>=('%s') and DATE(updated_time)=('%s')"%(row,curr_time,curr_date)
        print(sql)
        cursor.execute(sql)
        rows_affected=cursor.rowcount
        print("Room Id Rows affected - > ",row , rows_affected )
        students = cursor.fetchall()
        #print(students)
        for row2 in students:
        
            data = {"room_id": row, "student_id": row2[0]}

        #-----------------Show room-no---------------------

        #room_no_sql = "SELECT room_no from tbl_room where room_id='%s'"%(row)
        #cursor.execute(room_no_sql)
        #room_no_arr = cursor.fetchone()
        #room_no = room_no_arr[0]
        #print("Room noo is --->", room_no)
        #data2.append({"room_no": room_no, "no_of_students": rows_affected})
        #-----------------Show room-no---------------------

        data2.append({"room_id": row, "no_of_students": rows_affected})

        
    print(data2)
    data_return = {"room_list": data2, "error": "No Error"}
    print(data_return)
    print("Error")
    return jsonify(data_return)
    cursor.close()






#--------------------Get Student list and RSSI with Room Wise---------------------------------
@app.route('/student_list_room_wise', methods=['POST'])
def student_list_room_wise():
    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()
    #school_id = request.form['school_id']
    branch_id = request.form['branch_id']
    floor_id = request.form['floor_id']
    current_time =  request.form['current_time']

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])
    print("Current time is-->", curr_time)

    sql = "SELECT tbl_room.room_id, tbl_room.room_no FROM `tbl_room` JOIN `tbl_floor` ON tbl_floor.floor_id = '%s' AND tbl_floor.floor_id = tbl_room.floor_id WHERE tbl_floor.branch_id = '%s'"%(floor_id, branch_id)
    cursor.execute(sql)
    #users = cursor.fetchall()
    #print(users[0])

    room_id_list = []
    romm_no_list = []

    i= 0
    for row in cursor.fetchall():
        room_id_list.append(row[0])
        romm_no_list.append(row[1])

    #current_time = '2019-03-04 10:52:51'
    data2 = []
    student_list = []
    #updated_time  = '2019-03-04 10:53:53'
    #--------------------Get room id and room no ina floor---------------------------------
    for row in room_id_list:
        print(row)
        sql = "SELECT student_id, student_name, rssi_value FROM `tbl_attends_students_list` where room_id=%s AND updated_time>=('%s') AND DATE(updated_time)=('%s')"%(row,current_time, curr_date)
        cursor.execute(sql)
        rows_affected=cursor.rowcount
        if(rows_affected>0):
            students = cursor.fetchall()
            #print(students)
            student_list = []
            for row2 in students:
            
                #student_list.append({ "student_name": row2[1]})
                student_list.append({"student_name": row2[1], "rssi_value":row2[2]})
                #print(student_list)

        else:
            student_list = []

        data2.append({"room_id": row, "no_of_students": rows_affected, "student_list":student_list})
    #print(data2)

    data4 = {"room_list": data2, "error": "No Error"}
    print(data4)

    return jsonify(data4)
    cursor.close()



#---------------------------------API ROOM Details-----------------------------------
#---------------------------------API ROOM Details-----------------------------------
@app.route('/room_details', methods=['POST'])
def room_details():

#------------------------------------------------------------------------------------
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
#-----------------------------------Room details API------------------------------






@app.route('/present_student_list', methods=['POST'])
def present_list():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()

    branch_id = request.form['branch_id']
    class_id = request.form['class_id']
    current_time = request.form['current_time']

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])
    print("Current time is-->", curr_time)

    cursor.execute("SELECT start_time FROM tbl_class_time WHERE class_id = ('%s') AND branch_id = ('%s')" %(class_id, branch_id))
    class_data = cursor.fetchone()

    class_time = class_data[0]
    present_time = class_time + timedelta(minutes=10)
    # print(present_time)

    sql = ("SELECT tsi.student_id,tsi.student_first_name,tsi.student_last_name,tsi.contact FROM tbl_attends_students_list as tasl JOIN tbl_student_info as tsi ON tsi.id=tasl.student_id  WHERE tasl.class_id = ('%s') AND tasl.branch_id = ('%s') AND TIME(tasl.updated_time) >= ('%s') AND DATE(tasl.updated_time)=('%s')" %(class_id, branch_id,curr_time,curr_date))
    print(sql)
    cursor.execute(sql)
    #for row in cursor.fetchall():
    #    print(row[0], row[1], row[2], row[3])

    present_student_list ={"present_student_list":[{
        'student_id': row[0],
        'Student_name': row[1],
        'Contact': row[3]
    } for row in cursor.fetchall()]}

    #response = Response( 
    #    json.dumps(present_student_list), status=200, mimetype=JSON_MIME_TYPE)
    #return response

    return jsonify(present_student_list)
    cursor.close()



@app.route('/late_student_list', methods=['POST'])
def late_list():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()
    #school_id = request.form['school_id']
    branch_id = request.form['branch_id']
    #floor_id = request.form['floor_id']
    #room_id = request.form['room_id']
    class_id = request.form['class_id']
    current_time = request.form['current_time']

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])


    cursor.execute("SELECT start_time FROM tbl_class_time WHERE class_id = ('%s') AND branch_id = ('%s')" %(class_id, branch_id))
    class_data = cursor.fetchone()

    class_time = class_data[0]

    present_time10 = class_time + timedelta(minutes=10)
    present_time20 = class_time + timedelta(minutes=20)


    cursor.execute("SELECT tsi.student_id,tsi.student_first_name,tsi.student_last_name,tsi.contact FROM tbl_attends_students_list as tasl JOIN tbl_student_info as tsi ON tsi.id=tasl.student_id  WHERE tasl.class_id = ('%s') AND tasl.branch_id = ('%s') AND TIME(tasl.updated_time)  BETWEEN ('%s') AND ('%s') AND DATE(tasl.updated_time)=('%s')" %(class_id, branch_id,present_time10,present_time20, curr_date))
    late_student_list ={"late_student_list":[{
        'student_id': row[0],
        'Student_name': row[1]+" "+row[2],
        'Contact': row[3]
    } for row in cursor.fetchall()]}


    #response = Response( 
    #    json.dumps(late_student_list), status=200, mimetype=JSON_MIME_TYPE)
    #return response

    return jsonify(late_student_list)
    cursor.close()


@app.route('/absents_student_list', methods=['POST'])
def absents_list():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()
    #school_id = request.form['school_id']
    branch_id = request.form['branch_id']
    #floor_id = request.form['floor_id']
    #room_id = request.form['room_id']
    class_id = request.form['class_id']
    current_time = request.form['current_time']

    curr_date = current_time.split(' ')[0]
    curr_time = str(current_time.split(' ')[1])


    sql = "SELECT student_id FROM tbl_student_class WHERE class_id = %s AND student_id NOT IN(SELECT student_id FROM tbl_attends_students_list WHERE TIME(updated_time)>'%s' AND DATE(updated_time)= '%s' and class_id = %s)" %(class_id, curr_time, curr_date, class_id)
    
    print(sql)
    cursor.execute(sql)

    rows_affected_absent = cursor.rowcount
    print("Absent List-->", rows_affected_absent)


    absents_student_list = []

    for row in cursor.fetchall():
        student_id = row[0]
        print("student_id is-->", student_id)
        sql = "SELECT student_id, student_first_name, student_last_name, contact from tbl_student_info Where id = %s" %(student_id)
        cursor.execute(sql)
        data = cursor.fetchone()
        print("Student info---->", data[0])
        absents_student_list.append({
            'student_id': data[0],
            'Student_name': data[1]+ " " +data[2],
            'Contact': data[3]
        })


    absents_student_list ={"absents_student_list":absents_student_list}
    print(absents_student_list)

    return jsonify(absents_student_list)
    cursor.close()

#------------------------------------------Bullying API--------------------------------------------

@app.route('/bullying_history', methods=['POST'])
def bullying_historical_data():
    try:
        conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        #sql = "SELECT device_id, sd_acc_X, movement_status, avg_temperature, temperature_status FROM analysis_tbl WHERE device_id=%s ORDER BY id DESC LIMIT 1"
        #sql = "SELECT a.id, u.user_id, u.location, a.device_id, a.sd_acc_X, a.movement_status, a.sd_temperature, a.avg_temperature, a.temperature_status, a.next_heat_cycle, a.days_left_for_next_cycle, a.datetime FROM user_tbl AS u INNER JOIN analysis_tbl AS a ON u.device_id = a.device_id WHERE a.id IN( SELECT MAX(a.id) FROM analysis_tbl AS a INNER JOIN user_tbl AS u ON u.device_id = a.device_id GROUP BY u.user_id, u.device_id) AND u.user_id=%s"
        #sql = "SELECT br.branch_name, r.room_no, f.floor_no, si.student_first_name, si.student_last_name FROM tbl_entry_gateway gt INNER JOIN tbl_branch br ON br.branch_id = gt.branch_id INNER JOIN tbl_room r ON r.room_id = gt.room_id INNER JOIN tbl_floor f ON f.floor_id = gt.floor_id INNER JOIN tbl_movement_analysis anl ON anl.gateway_id = gt.gateway_id INNER JOIN tbl_student_info si ON si.`beacon_id` = anl.device_id WHERE anl.movement_status = 'Please Check!!!'"
        

        sql = "SELECT br.branch_name, r.room_no, f.floor_no, si.`student_first_name`, si.`student_id`, anl.time FROM tbl_entry_gateway gt INNER JOIN tbl_branch br ON br.branch_id = gt.branch_id INNER JOIN tbl_room r ON r.room_id = gt.room_id INNER JOIN tbl_floor f ON f.floor_id = gt.floor_id INNER JOIN tbl_movement_analysis anl ON anl.gateway_id = gt.gateway_id INNER JOIN tbl_student_info si ON si.`beacon_id` = anl.device_id WHERE anl.movement_status = 'Please Check!!!'"
        print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(rows)
        cursor.close()
        conn.close()
        return jsonify(rows)
    except:
        return jsonify({"response":"failed"})

#------------------------------------------Bullying API--------------------------------------------




#----------------------------------------------------------------------------------------------
#------------------------------------------LPR Camera------------------------------------------
#----------------------------------------------------------------------------------------------
#------------------------------------------LPR Camera History----------------------------------
#------------------------------------------LPR Camera History----------------------------------
#------------------------------------------LPR Camera History----------------------------------
@app.route('/lprcamerahistory', methods=['POST'])
def lprcamera1history():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()

    user_name = request.form['user_name']
    #password = request.form['password']
    camera_id = request.form['camera_id']
    secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
    cursor.execute("SELECT secret_key FROM tbl_camera WHERE id=%s",camera_id)
    secret_key_db = cursor.fetchone()[0]

    if secret_key == secret_key_db:
        #cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id ORDER BY tbl_lprcamera.id")#
        # cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id WHERE tbl_lprcamera.blorwh = '1' ORDER BY tbl_lprcamera.id")
        cursor.execute("SELECT tbl_whitelistvehicle.id,tbl_whitelistvehicle.entryTime, tbl_whitelistvehicle.vehiclePlate,tbl_whitelistvehicle.blorwh,tbl_student_info.student_id,tbl_whitelistvehicle.owner,tbl_student_info.student_first_name FROM tbl_whitelistvehicle LEFT JOIN tbl_student_info ON tbl_whitelistvehicle.student_id=tbl_student_info.student_id WHERE tbl_whitelistvehicle.blorwh = '1' ORDER BY tbl_whitelistvehicle.id")
        lprcamera1history = cursor.fetchall()

        #print(len(lprcamera1history))
        #print(lprcamera1history[0])

        #for row in lprcamera1history:
        #    print(row[0], row[1], row[2], row[3])
        

        lprcamera1history ={ "error": "false", "description": "lpr camera history successfull", "lpr_camera1_history":[{
            'id': str(row[0]),
            'entryTime:': row[1],
            'vehiclePlate': row[2],
            'blorwh': row[3],
            'studentid': str(row[4]),
            'owner': row[5],
            'student_name': str(row[6])
        } for row in lprcamera1history]}
        return jsonify(lprcamera1history)
        print(lprcamera1history)
    else:
        return jsonify({'error': 'true', 'description': 'wrong secret key', "lpr_camera1_history": []})
    cursor.close()

#------------------------------------------LPR Camera History----------------------------------
#------------------------------------------LPR Camera History----------------------------------
# #------------------------------------------Black List History----------------------------------
# @app.route('/blacklisthostory', methods=['POST'])
# def blacklisthostory():

#     conn = pymysql.connect(host=host, user=user, password=password, db=db)
#     cursor = conn.cursor()

#     user_name = request.form['user_name']
#     #password = request.form['password']
#     camera_id = request.form['camera_id']
#     secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
#     cursor.execute("SELECT secret_key FROM tbl_camera WHERE id=%s",camera_id)
#     secret_key_db = cursor.fetchone()[0]

#     if secret_key == secret_key_db:
#         #cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id ORDER BY tbl_lprcamera.id")#
#         cursor.execute("SELECT tbh.id, tbh.entryTime, tbh.vehiclePlate, tbh.owner FROM tbl_blacklisthistory tbh ORDER BY tbh.id")
#         blacklisthostory = cursor.fetchall()   

#         blacklist_history ={ "error": "false", "description": "blacklist hostory successfull", "blacklisthostory":[{
#             'id': str(row[0]),
#             'entryTime:': row[1],
#             'vehiclePlate': row[2],
#             'owner': row[3],
#         } for row in blacklisthostory]}
#         return jsonify(blacklist_history)
#     else:
#         return jsonify({'error': 'true', 'description': 'wrong secret key', "blacklisthostory": []})
#     cursor.close()

# #------------------------------------------------------------------------------

#------------------------------------------Add Vehicle----------------------------------
@app.route('/addwhitelistvehicle', methods=['POST'])
def addwhitelistvehicle():
	user_name = request.form['user_name']

	#student_name = request.form['student_name']
	student_id = request.form['student_id']
	vehiclePlate = request.form['vehicle_plate']
	owner = request.form['owner']
	secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric


	print(user_name, vehiclePlate, secret_key, owner)
	#student name, student id, car plate, owner ,secret_key

	if user_name != "" or student_name != "" or student_id != "" or vehiclePlate != "" or secret_key != "" or owner  != "":

	    if secret_key =='hfjKricAdD':
	        try:        
	            conn = pymysql.connect(host=host, user=user, password=password, db=db)
	            cursor = conn.cursor()
	            currentDT = datetime.now()
	            cursor.execute("SELECT student_first_name,id FROM tbl_student_info WHERE student_id=%s",student_id)
	            name_query = cursor.fetchone()
	            print (name_query)	
	            if name_query == None:
	            	return jsonify({'error': 'true', 'description': 'invalid student id'})
	            elif name_query != None:
                        student_first_name = name_query[0]
                        student_id = name_query[1]
                        print(student_id)
                        sql_insert_query = """ INSERT INTO `tbl_whitelistvehicle`
                                            (`entryTime`,`student_id`,`vehiclePlate`, `owner`, `addedBy`, `blorwh`) VALUES (%s,%s,%s,%s,%s,%s)"""
                        sql_values = (currentDT, student_id, vehiclePlate,owner,user_name,'1')
                        cursor.execute(sql_insert_query,sql_values)
                        conn.commit()
                        print (cursor.rowcount, "Record inserted successfully into tbl_whitelistvehicle table")
                        if cursor.rowcount == 1:
                            return jsonify({'error': 'false', 'description': 'Vehicle addition successfull'})
                        else:
                            return jsonify({'error': 'true', 'description': 'Vehicle addition failure'})
                        # else:
                        # 	return jsonify({'error': 'true', 'description': 'invalid student id'})
	        except pymysql.err.IntegrityError as e:
	            if e.args[0] == 1062:
	                return jsonify({'error': 'true', 'description': 'Dublicate entry error!'})
	            else:
	                return jsonify({'error': 'true', 'description': e.args[0]})
	    else:
	        return jsonify({'error': 'true', 'description': 'Wrong secret key!'})
	else:
		return jsonify({'error': 'true', 'description': 'Input parameter empty'})
	cursor.close()

#----------------------------------------------------------------------------------------------
#------------------------------------------LPR Camera------------------------------------------
#----------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------
#------------------------------------------FCM Token Get------------------------------------------------
#----------------------------------------------------------------------------------------------
@app.route('/fcmtokenget', methods=['POST'])
def fcmtokenget():
    user_name = request.form['user_name']
    secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
    
    print(user_name, secret_key)

    if secret_key =='hfjKricAdD':
        if user_name == 'GetAll':                
            try:        
                conn = pymysql.connect(host=host, user=user, password=password, db=db)
                cursor = conn.cursor()
                sql_select_query = """select user_name,fcm_token from tbl_user"""
                cursor.execute(sql_select_query)
                fcm_token_array = cursor.fetchall()
                print(fcm_token_array)
                return jsonify({'error': 'false', 'description': 'Get FCM Token successfull', 'fcm_token': fcm_token_array})

            except pymysql.err.IntegrityError as e:
                return jsonify({'error': 'true', 'description': e.args[0] , 'fcm_token': fcm_token_array})

        elif user_name == 'GetAllNotNull':                
            try:        
                conn = pymysql.connect(host=host, user=user, password=password, db=db)
                cursor = conn.cursor()
                sql_select_query = """select user_name,fcm_token from tbl_user WHERE fcm_token IS NOT NULL AND fcm_token!=''"""
                cursor.execute(sql_select_query)
                fcm_token_array = cursor.fetchall()
                print(fcm_token_array)
                return jsonify({'error': 'false', 'description': 'Get FCM Token successfull', 'fcm_token': fcm_token_array})

            except pymysql.err.IntegrityError as e:
                return jsonify({'error': 'true', 'description': e.args[0] , 'fcm_token': fcm_token_array})

        else:

            try:        
                conn = pymysql.connect(host=host, user=user, password=password, db=db)
                cursor = conn.cursor()

                sql_select_query = """select fcm_token from tbl_user where user_name = %s"""
                cursor.execute(sql_select_query, (user_name, ))


                fcm_token_array = cursor.fetchone()
                print(fcm_token_array)
                if(cursor.rowcount>0):
                    #fcm_token_array = cursor.fetchall()
                    #print(fcm_token_array)
                    return jsonify({'error': 'false', 'description': 'Get FCM Token successfull', 'fcm_token': fcm_token_array})
                else:
                    return jsonify({'error': 'false', 'description': 'User not found', 'fcm_token': []})

            except pymysql.err.IntegrityError as e:
                return jsonify({'error': 'true', 'description': e.args[0], 'fcm_token': []})

        

    else:
        return jsonify({'error': 'true', 'description': 'wrong secret key', 'fcm_token': []})
    cursor.close()

#----------------------------------------------------------------------------------------------
#------------------------------------------QR Scan------------------------------------------
#----------------------------------------------------------------------------------------------

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
            if(mode_of_transport== "self" or mode_of_transport== "dropoff"):
                print("Status updated")
                return jsonify({"description": "", "error": "false", "data" : mode_of_transport})
            elif (mode_of_transport== "bus" or mode_of_transport== "other"):
                return jsonify({"description": "Registration Successful", "error": "false", "data" : "Success"})
                

            else:
                print(" no Status updated")
                return jsonify({"description": "failure", "error": "true", "data" :""})

        else:
            return jsonify({"description": "Parameters empty!", "error": "true", "data" :""})
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


#------------------------------------------blacklisted_car_history----------------------------------
@app.route('/blacklisted_car_history', methods=['POST'])
def blacklisted_car_history():

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    cursor = conn.cursor()

    user_name = request.form['user_name']
    #password = request.form['password']
    camera_id = request.form['camera_id']
    secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
    cursor.execute("SELECT secret_key FROM tbl_camera WHERE id=%s",camera_id)
    secret_key_db = cursor.fetchone()[0]

    if secret_key == secret_key_db:
        #cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id ORDER BY tbl_lprcamera.id")#
        cursor.execute("SELECT tbl_lprcamera.vehiclePlate,tbl_lprcamera.student_id,tbl_lprcamera.owner,tbl_lprcamera.entryTime,tbl_lprcamera.reason,tbl_student_info.student_first_name,tbl_lprcamera.blorwh FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.id WHERE tbl_lprcamera.blorwh = '0' ORDER BY tbl_lprcamera.id")
        blacklisthostory = cursor.fetchall()   

        blacklist_history ={ "error": "false", "description": "blacklisted_car_history successfull", "blacklisted_car_history":[{
            'vehicle_id': str(row[0]),
            'student_id:': row[1],
            'owner': str(row[2]),
            'entryTime': row[3],
            'reason': row[4],
            'student_first_name': str(row[5]),
            'blorwh': row[6],
        } for row in blacklisthostory]}
        return jsonify(blacklist_history)
    else:
        return jsonify({'error': 'true', 'description': 'wrong secret key', "blacklisted_car_history": []})
    cursor.close()

#------------------------------------------------------------------------------



#------------------------------------------Class Schedule--------------------------------------------


@app.route('/classschedule', methods=['POST'])
def classsche():
	conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
	cursor = conn.cursor()

	_start_time = request.form['start_time']
	_end_time = request.form['end_time']
	_branch_id = request.form['branch_id']
	_floor_id = request.form['floor_id']
	_room_id = request.form['room_id']
	_day = request.form['day']
	_subject = request.form['subject']
	_teacher = request.form['teacher']
    
	if _start_time != "" and _end_time != "" and _branch_id != "" and _floor_id != "" and _room_id != "" and _day != "":
	    


	    # _start_time = request.form['start_time']
	    # _end_time = request.form['end_time']
	    # _branch_id = request.form['branch_id']
	    # _floor_id = request.form['floor_id']
	    # _room_id = request.form['room_id']
	    # _day = request.form['day']
	    # _subject = request.form['subject']
	    # _teacher = request.form['teacher']

	    
	    if  request.form['subject'] ==  "" and  request.form['teacher'] == "":
	        _subject = ""
	        _teacher = ""    
	        

	        sql = "INSERT INTO tbl_class_time(start_time, end_time, branch_id,floor_id, room_id, day, subject,teacher) VALUES(%s, %s,%s,%s, %s, %s,%s,%s)"
	        cursor.execute(sql,(_start_time,_end_time,_branch_id, _floor_id, _room_id, _day, _subject, _teacher))
	        conn.commit()
	    
	        return jsonify({"status": "success"}), 200   

	    else:
	        

	        sql = "INSERT INTO tbl_class_time(start_time, end_time, branch_id,floor_id, room_id, day, subject,teacher) VALUES(%s, %s,%s,%s, %s, %s,%s,%s)"
	        cursor.execute(sql,(_start_time,_end_time,_branch_id, _floor_id, _room_id, _day, _subject, _teacher))
	        conn.commit()
	    
	        return jsonify({"status": "success"}), 200
	    
	else:
	    return jsonify({"status": "Empty Field"})


#------------------------------------------Class Schedule--------------------------------------------


#------------------------------------------Dashboard-------------------------------------------
@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        _branch_id = request.form['branch_id']
        _floor_id = request.form['floor_id']
        _current_time = request.form['current_time']
        curr_date = _current_time.split(' ')[0]
        curr_time = _current_time.split(' ')[1]
        print("Current date -->", curr_date)
        print("Current time -->", curr_time)
        date_obj = datetime.strptime(curr_date, '%Y-%m-%d')
        week_day = date_obj.strftime("%A")
        print(week_day)

        prev_threshold  = datetime.strptime(_current_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=5)
        next_threshold = datetime.strptime(_current_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)

        conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        #sql_all = "SELECT tsc.student_id, tct.class_id, tct.room_id FROM tbl_class_time INNER JOIN tbl_student_class tsc ON tct.class_id = tsc.class_id where tct.floor_id = %s and tct.branch_id = %s and tct.day = %s AND %s BETWEEN tct.start_time and tct.end_time AND tsc.student_id IN (SELECT student_id FROM tbl_student_arrival WHERE date = %s and time < %s) "


        sql_all =  "SELECT COUNT(tsc.student_id) total_class_students, tct.class_id, tct.room_id FROM `tbl_class_time` tct INNER JOIN tbl_student_class tsc ON tct.class_id = tsc.class_id where tct.branch_id = %s and tct.floor_id = %s  and tct.day = %s and %s BETWEEN tct.start_time and tct.end_time AND tsc.student_id IN (SELECT student_id FROM `tbl_student_arrival` WHERE date = %s and arrivalTime < %s) GROUP BY tct.class_id"


        params = (_branch_id, _floor_id, week_day, curr_time, curr_date, curr_time)

        cursor.execute(sql_all, params)

        rows_all = cursor.fetchall()

        pprint(rows_all)
        print("-----------")

        if len(rows_all) > 0:
            student_distribution = []
            for row_a in rows_all:
                sql_students = "SELECT student_id FROM `tbl_student_class` where class_id = %s and student_id in (SELECT student_id FROM `tbl_student_arrival` WHERE date = %s and arrivalTime < %s)"
                cursor.execute(sql_students, (row_a['class_id'], curr_date, curr_time))
                rows_students = cursor.fetchall()
                #print(rows_students)
                row_a['green_count'] = 0

                for row_stu in rows_students:
                    print(row_stu['student_id'])
                    sql_student_present_check = "SELECT EXISTS (SELECT * FROM `tbl_attends_students_list` WHERE student_id = %s AND room_id = %s) student_present"
                    cursor.execute(sql_student_present_check, (row_stu['student_id'], row_a['room_id']))
                    student_present_check = cursor.fetchone()
                    print(student_present_check)
                    if student_present_check['student_present'] == 1:
                        row_a['green_count'] += 1
                    else :
                        pass
                print("....................")

                row_a['red_count'] = row_a['total_class_students'] - row_a['green_count']
                student_distribution.append(row_a)
            pprint("rows_all:")
            pprint(rows_all)

            # print("==========================")
            # print("student_distribution:")
            # pprint(student_distribution)

            total_students = 0
            total_green = 0
            total_red = 0

            for row in rows_all:
                total_students += row['total_class_students']
                total_green += row['green_count']
                total_red += row['red_count']

            # print(total_students)
            # print(total_green)
            # print(total_red)
            response = {"total_students": total_students, "total_green": total_green, "total_red": total_red, "student_distribution": rows_all }
            return jsonify(response)

        else:
            student_distribution = []
            total_students = 0
            total_green = 0
            total_red = 0
            response = {"total_students": total_students, "total_green": total_green, "total_red": total_red, "student_distribution": rows_all }
            return jsonify(response)

    except Exception as e:
        print(e)

        return jsonify({"response": "failed"})


#------------------------------------------Dashboard-------------------------------------------

#------------------------------------------Red List-------------------------------------------

@app.route('/red_list', methods=['POST'])
def red_list():
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

    try:
        conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        sql_all = "SELECT tsc.student_id, tct.class_id, tct.room_id FROM tbl_class_time tct INNER JOIN tbl_student_class tsc ON tct.class_id = tsc.class_id where tct.floor_id = %s and tct.branch_id = %s and tct.day = %s and %s BETWEEN tct.start_time and tct.end_time"

        params = (_floor_id, _branch_id, week_day, curr_time)

        cursor.execute(sql_all, params)

        rows_all = cursor.fetchall()

        pprint(rows_all)

        red_list_details = []

        for rows_a in rows_all:
            sql_check = "SELECT EXISTS (SELECT * FROM tbl_attends_students_list WHERE student_id = %s and class_id = %s and updated_time BETWEEN %s and %s) present"
            params = (rows_a['student_id'], rows_a['class_id'], prev_threshold, next_threshold)


            cursor.execute(sql_check, params)
            row_check = cursor.fetchone()
            #print(prev_threshold, next_threshold)
            print('student id ->', rows_a['student_id'])
            print(row_check)

            if (row_check['present'] == 0):
                #print("Not arrived ->", rows_a['student_id'])
                print("see if the red_list:")
                sql_arrived = "SELECT EXISTS (SELECT * FROM `tbl_student_arrival` WHERE student_id = %s and date = %s and arrivalTime < %s) red_list"
                cursor.execute(sql_arrived, (rows_a['student_id'], curr_date, curr_time))
                row_red_list_check = cursor.fetchone()
                #absent from class students:

                if (row_red_list_check['red_list'] == 1):
                    print("find red_list student location: ")
                    print("red_list ids -> ", rows_a['student_id'])
                    sql_curr = "SELECT tasl.student_id, tsc.class_id expected_class_id,tr.room_no expected_room_no, tcr.room_no current_room_no, DATE_FORMAT(tasl.updated_time, '%%Y-%%m-%%d %%H:%%i:%%s') last_seen_time FROM tbl_attends_students_list tasl INNER JOIN tbl_student_class tsc ON tsc.student_id = tasl.student_id INNER JOIN tbl_class_time tct on tct.class_id = tsc.class_id INNER JOIN tbl_room tr ON tr.room_id = tct.room_id INNER JOIN  tbl_room tcr ON tcr.room_id =   tasl.room_id WHERE tasl.student_id = %s ORDER BY tasl.updated_time DESC LIMIT 1"
                    cursor.execute(sql_curr, rows_a['student_id'])
                    row_curr = cursor.fetchone()
                    red_list_details.append(row_curr)
                    #print(row_curr)
                else:
                    #Not arrived students
                    print("Not arrived ids ->", rows_a['student_id'])
            else:
                pass
            print("..............")

        print(red_list_details)
        cursor.close()
        conn.close()
        return jsonify({"red_listed_details": red_list_details})

    except Exception as e:
        print(e)

        return jsonify({"response": "failed"})


# --------------------------------------------vehicle history for guard(one day)--------------------------------



@app.route('/vehhisforguard', methods=['POST'])
def vehhisforguard():

    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    user_name = request.form['user_name']
    #password = request.form['password']
    camera_id = request.form['camera_id']
    secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
    room_type = request.form['room_type']#main_entry
    print(user_name,camera_id,secret_key,room_type)


    florida = timezone('Asia/Dhaka')
    florida_time = datetime.now(florida)
    time_stamp = florida_time.strftime('%Y-%m-%d %H:%M:%S')
    print("Time is-->", time_stamp)

    curr_date = time_stamp.split(' ')[0]
    curr_time = str(time_stamp.split(' ')[1])
    print("Current DATE is-->", curr_date)
    print("Current TIME is-->", curr_time)

    cursor.execute("SELECT secret_key FROM tbl_camera WHERE id=%s",camera_id)
    secret_key_db = cursor.fetchone()['secret_key']
    print(secret_key_db)
    if secret_key == secret_key_db:
        #cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id ORDER BY tbl_lprcamera.id")#
        # cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id WHERE tbl_lprcamera.blorwh = '1' ORDER BY tbl_lprcamera.id")
        #cursor.execute("SELECT tlc.vehiclePlate,tsi.student_first_name,tsi.student_last_name,tsi.student_id,tlc.entryTime FROM tbl_lprcamera1 as tlc LEFT JOIN tbl_student_info as tsi ON tlc.student_id=tsi.id WHERE DATE(tlc.entryTime)=(%s) ORDER BY tlc.entryTime",(curr_date))
        cursor.execute("SELECT tlc.entryTime, tlc.blorwh, tlc.vehiclePlate, tlc.imageLoc, twv.owner, tsi.student_first_name,tsi.student_last_name,tsi.student_id,tlc.entryTime FROM tbl_lprcamera1 as tlc LEFT JOIN tbl_whitelistvehicle as twv ON twv.vehiclePlate=tlc.vehiclePlate LEFT JOIN tbl_student_info as tsi ON tlc.student_id=tsi.id WHERE DATE(tlc.entryTime)=(%s) ORDER BY tlc.entryTime DESC",(curr_date))
        vehhisforguard = cursor.fetchall()

        print(len(vehhisforguard))
        print(vehhisforguard)
        vehhistoryforguard ={ "error": "false", "description": "vehhisforguard successfull", "car_list":[{
            'date': str(row['entryTime']).split(" ")[0],
            'time': str(row['entryTime']).split(" ")[1].split(".")[0],
            #'blorwh': row['blorwh'],
            'access': 'Permitted' if str(row['blorwh']) == '1' else 'Not Registered',
            'driver': str(row['owner']),
            'vehicle_id': str(row['vehiclePlate']),
            'student_id:': row['student_id'] if row['student_id'] != None else  "",
            #'owner': str(row['owner']),
            'student_name': str(row['student_first_name'])+ " " + str(row['student_last_name']) if str(row['student_first_name']) != "None" and str(row['student_last_name']) != "None" else  "",
            'location': 'Front Gate',
            'car_photo_url':row['imageLoc']
        } for row in vehhisforguard]}

        return jsonify(vehhistoryforguard)

        if len(vehhisforguard) == 0:
            return jsonify({'error': 'false', 'description': 'empty data', "vehhisforguard": vehhisforguard})
        else:
            return jsonify({'error': 'false', 'description': 'succes', "vehhisforguard": vehhisforguard})
        #print(lprcamera1history)
    else:
        return jsonify({'error': 'true', 'description': 'wrong secret key', "vehhisforguard": []})
    cursor.close()


# --------------------------------------------vehicle history for guard(one day)-------------------------------------

# --------------------------------------------vehicle history for guard(all day)--------------------------------



@app.route('/vehhisforguardall', methods=['POST'])
def vehhisforguardall():

    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    user_name = request.form['user_name']
    #password = request.form['password']
    camera_id = request.form['camera_id']
    secret_key = request.form['secret_key']#hfjKricAdD#10digit alphanumeric
    room_type = request.form['room_type']#main_entry
    print(user_name,camera_id,secret_key,room_type)





    cursor.execute("SELECT secret_key FROM tbl_camera WHERE id=%s",camera_id)
    secret_key_db = cursor.fetchone()['secret_key']
    print(secret_key_db)
    if secret_key == secret_key_db:
        #cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id ORDER BY tbl_lprcamera.id")#
        # cursor.execute("SELECT tbl_lprcamera.id,tbl_lprcamera.entryTime, tbl_lprcamera.vehiclePlate,tbl_lprcamera.blorwh,tbl_student_info.student_id,tbl_lprcamera.owner,tbl_student_info.student_first_name FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.student_id WHERE tbl_lprcamera.blorwh = '1' ORDER BY tbl_lprcamera.id")
        cursor.execute("SELECT tbl_lprcamera1.vehiclePlate,tbl_student_info.student_first_name, tbl_student_info.student_last_name,tbl_student_info.student_id,tbl_lprcamera1.entryTime FROM tbl_lprcamera LEFT JOIN tbl_student_info ON tbl_lprcamera.student_id=tbl_student_info.id ORDER BY tbl_lprcamera.entryTime")
        vehhisforguard = cursor.fetchall()

        #print(len(vehhisforguard))
        #print(vehhisforguard)

        for row in vehhisforguard:
            #print(type(row))
            if row['student_first_name'] == None or row['student_last_name'] == None or row['student_id'] == None:
                #print("Student is none")
                #del row[student_name]
                row['student_name'] = ""
                row['student_id'] = ""
                #print(row['student_name'])
                #print(row['student_id'])
                row['ble_id'] = "Don't Match"
                row['status'] = "Blacklisted"
                #print(row['entryTime'])

            else:
                row['student_name'] = row['student_first_name'] + ' ' + row['student_last_name']
                #print(row['student_name'])
                row['ble_id'] = "Matched"
                row['status'] = "Arrived"

            del row['student_first_name']
            del row['student_last_name']
            #2019-05-08 00:08:20.817000
            veh_date = row['entryTime'].strftime("%B %d, %Y")
            veh_time = row['entryTime'].strftime("%I:%M:%S %p")
            row['veh_date'] = veh_date
            row['veh_time'] = veh_time

        return jsonify({'error': 'false', 'description': 'vehhisforguard success', "vehhisforguard": vehhisforguard})
        #print(lprcamera1history)
    else:
        return jsonify({'error': 'true', 'description': 'wrong secret key', "vehhisforguard": []})
    cursor.close()


# --------------------------------------------vehicle history for guard(all day)-------------------------------------




if __name__ == '__main__':
    app.run(debug=True,host= '182.163.112.219', port=9193)
