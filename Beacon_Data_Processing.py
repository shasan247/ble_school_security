
import yaml
import collections # For creating ordered dictionary
import json # For creating json data
import os
from pathlib import Path

from datetime import datetime, date
from pytz import timezone 
import calendar

import random
import names

import Database_Ble

#----------newly added----
import pymysql
from pprint import pprint
#import datetime
from pyfcm import FCMNotification
import requests

push_service = FCMNotification(api_key="AAAAL-M_qjo:APA91bFDT028Itamu_P5o_qSw61l7t-5mwHvMP1Cri85wuRwkeeP8plh25JfDaBUVvAyeWvkQpB3ZJ3uuDVye9z9jgoVdB6NTsde3XDnPIlYygkAqWMLoKITz5IyMcukEFv8q9L5tdic")
#--------------------------

def Notification_for_outside_class(student_id, room_id):
    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'user_name':'Shanta','secret_key':'hfjKricAdD'}
    r = requests.post('http://182.163.112.219:9193/fcmtokenget', data = payload)

    print(r.text)
    print(r.json())
    r_json = r.json()
    print(type(r_json))

    description = r_json['description']
    error = r_json['error']
    fcm_token = r_json['fcm_token'][0]

    registration_id = fcm_token#"eVyxoZJlGmM:APA91bH4EUKRxsG3EbyV_jqX9dKd772H3tLbJ985adSx2NSjEMOapxzfW7luV76R7OV7qEhcEXUsChdEzNaYKuq4PTNVo8Ss5mtRJJWBtk-nKsr3L3cYgk9arpMJVbLdBf9pmFQ3hPqX"
    registration_ids = [registration_id]
    message_title = "Outside Class"
    message_body = 'student id: ' + str(student_id) + ', room id: '+ str(room_id) +', Date & Time: ' + datetime.datetime.now().strftime('%B %d, %Y - %H:%M')
    result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)


class Query(Database_Ble.Query):
    pass

#Query.create_connection()

class Processing:

    def device_data_process(self, client_data):

        # Try-catch block
        try:
            #print(type(client_data))
            dictionary_data = yaml.load(client_data)
            #print("Dictionary data--> ", dictionary_data)
            # print(type(dictionary_data))
            Query.create_connection()

            # print("DATA ------------------------------------->", dictionary_data)
            print("Data end---------------------------------------------------")
            #############################################################################
            # Required for retrieving device number from data stream
            #def device_data_analysis(gateway_address, beacon_mac_address, beacon_rssi,beacon_data):
            #    length = len(beacon_data)
            #    print("Data Length is-->", length)

            #i=0
            #for obj in dictionary_data:
            #    if(i==0):
            #        gateway_address = obj['mac']
            #        print("gateway_address is-->", gateway_address)
            #    else:

            #dictionary_data = json.loads(client_data)
            gateway_address = ''

            # for key, value in dictionary_data.items():
            #     if key == 'gmac':
            #         gateway_address = value
            #         print("Gateway address is ---->", gateway_address )
            #     if key == 'obj':
            #         #print(value)
            #         for i in value:
            #             beacon_mac_address = i['dmac']
            #             data_load= i['data1']
            #             beacon_rssi = i['rssi']
            for k in dictionary_data:
                if k["type"] == 'Gateway':
                    gateway_address = k["mac"]
                    print("Gateway ID is --> ", gateway_address)

                if k["type"] == 'Unknown':
                    beacon_mac_address = k['mac']
                    data_load = k['rawData']
                    beacon_rssi = k['rssi']
                    # print("++++++++++++++data decoded+++++++++++++")
                    #print(beacon_mac_address)

                    if beacon_mac_address == 'AC233FA17A7B' or beacon_mac_address == 'AC233FA17A70' or beacon_mac_address == 'AC233FA17A01' or beacon_mac_address == 'AC233FA179F8':
                        print("++++++++++++++Beacon matche Found+++++++++++++")
                        # conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
                        # cursor = conn.cursor()
                        #length = len(data_load)
                            
                        #beacon_mac_address = obj['mac']
                        #beacon_rssi = obj['rssi']
                        #print("rssi is-->", beacon_rssi)
                        #if(beacon_mac_address.startswith(('AC233F29', 'ac233f29'))):
                        #if(beacon_mac_address=='AC233F292726' or beacon_mac_address=='AC233F292731'):
                        print("Gateway address--->", gateway_address)
                        print("beacon_mac_address is-->", beacon_mac_address)
                        print("RSSI--->", beacon_rssi)
                        #ts = time.time()
                        #time_stamp =  datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        #print("Time is-->", time_stamp)

                        #florida = timezone('US/Eastern')

                        florida = timezone('Asia/Dhaka')
                        florida_time = datetime.now(florida)
                        time_stamp = florida_time.strftime('%Y-%m-%d %H:%M:%S')
                        print("Time is-->", time_stamp)
                        
                        curr_date = time_stamp.split(' ')[0]
                        curr_time = str(time_stamp.split(' ')[1])
                        print("Current DATE is-->", curr_date)
                        print("Current TIME is-->", curr_time)

                        #-------------Find Day from Date------------------------
                        my_date = date.today()

                        day = calendar.day_name[my_date.weekday()]  #'Wednesday'
                        print("day is --->", day)
                        #-------------Find Day from Date------------------------



                        #Retrieve Student_id and Gateway_id using Beacon_address
                        #----------------Retrieve Student_id and Gateway_id using Beacon_address------------------
                        student_id_query = ("SELECT student_id from tbl_entry_beacon where beacon_id = '%s'" %(beacon_mac_address))
                        student_id_data = Query.get_a_record(student_id_query)
                        print("student_data --> ",student_id_data)


                        #------------------- Random name and id generate part-------------------
                        if(str(student_id_data)=='None'):
                            pass
                            #print("In if condition")
                            #Insert a random name and random id for register student
                            #student_id = random.randint(13112,19999)
                            #print("Student id is--->", student_id)
                            #student_name = names.get_first_name()
                            #print("Student name is--->", student_name)
                            
                            #Insert beacon_id and random_id to tbl_beacon_entry
                            #insert_query = ('INSERT INTO tbl_entry_beacon(beacon_id) VALUES (%s)',(beacon_mac_address))    
                            #result = Query.commit(insert_query)
                            #print("Random Data Inserted Successfully in tbl_entry_beacon!!")

                        #Insert random_id and rand_name to tbl_student_info
                            # insert_query = ('INSERT INTO tbl_student_info(student_id,beacon_id,student_first_name) VALUES (%s,%s,%s)',(student_id,beacon_mac_address, student_name))    
                            # result = Query.commit(insert_query)
                            # print("Random Data Inserted Successfully in tbl_student_info!!")

                            # get_id_query = "SELECT id from tbl_student_info where student_id='%s'", (student_id)
                            # print(get_id_query)
                            # st_uniqe_id_arr  = Query.get_a_record2(get_id_query)
                            # print(st_uniqe_id_arr)
                            # st_uniqe_id = st_uniqe_id_arr[0]
                            # print("st_uniqe_id-->", st_uniqe_id)

                            # #Insert beacon_id and random_id to tbl_beacon_entry
                            # insert_query = ('INSERT INTO tbl_entry_beacon(beacon_id,student_id) VALUES (%s,%s)',(beacon_mac_address,st_uniqe_id))    
                            # result = Query.commit(insert_query)
                            # print("Random Data Inserted Successfully in tbl_entry_beacon!!")
                        #------------------- Random name and id generate part-------------------



                        else:
                       



                            student_id = student_id_data[0]
                            print("student_id is------>", student_id)
                            print("gateway_address is------>", gateway_address)

                            #----------------Retrieve Student_id and Gateway_id using Beacon_address---------------------------------

                            #-----------------Get student name and branch_id using studennt_id---------------
                            student_query = ("SELECT student_first_name, branch_id from tbl_student_info where id= '%s'" %(student_id))
                            student_data = Query.get_a_record(student_query)
                            print("student data is---> ", student_data)

                            if(str(student_data)=='None'):
                                pass
                            else:
                                print("PROBLEM Student data is--->", student_data)

                                student_name = student_data[0]
                                print("student_name is------->", student_name)

                                branch_id = student_data[1]
                                print("branch_id is-------->", branch_id)
                                #-----------------Get student name and branch_id using studennt_id---------------


                                #-----------------Get Room_ID-----------------------------------------------------
                                #AC233FC023B1

                                get_room_id_query = "SELECT room_id from tbl_entry_gateway where gateway_id = '%s'" %(gateway_address)
                                get_room_id_arr = Query.get_all_record(get_room_id_query)
                                # room_id = get_room_id_arr[0]
                                room_id = get_room_id_arr
                                for i in get_room_id_arr:
                                    # room_id[i]
                                    room = list(i)
                                    for room_id in room:
                                        print("\n \n\n \n\n \n Room id is--------------->", room_id)
                                        #-----------------Get Room_ID-----------------------------------------------------
                                    


                                        #-----------------Get Class_ID-----------------------------------------------------
                                        get_class_id_query = "SELECT tbl_student_class.class_id from tbl_student_class JOIN tbl_class_time ON tbl_student_class.class_id = tbl_class_time.class_id AND '%s'>=start_time and '%s'<=end_time and student_id='%s' and day = '%s' and room_id = '%s'" %(curr_time, curr_time, student_id, day, room_id)
                                        get_class_id_arr = Query.get_a_record(get_class_id_query)
                                        
                                        print("\n \n \n \nThis is the class id array",get_class_id_arr)


                                        if(str(get_class_id_arr)=='None'):
                                            # #id_class_exist_query = ("SELECT student_id from tbl_attends_students_list where student_id = (%s) and branch_id=(%s) and room_id=(%s)" %(student_id, branch_id, room_id))
                                            # id_class_exist_query = ("SELECT student_id from tbl_attends_students_list where student_id = (%s)" %(student_id))

                                            # print(id_class_exist_query)
                                            # id_class_exist_data = Query.get_a_record(id_class_exist_query)
                                            # if(str(id_class_exist_data)=='None'):
                                            #     print("Inside of insert query ")
                                            #     insert_query = 'INSERT INTO tbl_attends_students_list(student_id, student_name, updated_time, rssi_value, branch_id, room_id) VALUES (%s,%s,%s,%s,%s,%s)', (student_id, student_name, time_stamp, beacon_rssi, branch_id, room_id)
                                            #     result = Query.commit(insert_query)
                                            #     print("Data Inserted Successfully in Attendance Table!!!!")
                                            # else:
                                            #     #update 
                                            #     update_query = ('UPDATE tbl_attends_students_list SET student_name = (%s), updated_time = (%s), rssi_value = (%s), branch_id = (%s), room_id = (%s) where student_id = (%s)',(student_name, time_stamp,beacon_rssi,branch_id, room_id,student_id))
                                            #         # Update a previous recordupdated_time
                                            #     result = Query.commit(update_query)
                                            #     print("Data updated in Attendance Table!!")
                                            pass
                                        else:
                                            class_id = get_class_id_arr[0]
                                            print("Class id is--->", class_id)
                                            print("Class id is --->", class_id)

                                            #-----------------Get Class_ID-----------------------------------------------------




                                            #--------INSERET student in attendance table---------------------------------

                                            #If id exist in a particular class don't insert 
                                            #If id is not exist just insert
                                            id_class_exist_query = ("SELECT student_id from tbl_attends_students_list where student_id = (%s)" %(student_id))

                                            #id_class_exist_query = ("SELECT student_id from tbl_attends_students_list where student_id = (%s) and class_id=(%s) and branch_id=(%s) and room_id=(%s)" %(student_id, class_id, branch_id, room_id))
                                            print(id_class_exist_query)
                                            id_class_exist_data = Query.get_a_record(id_class_exist_query)
                                            #id_exist = id_exist_data[0]
                                            print("id_class_exist_data, -->", id_class_exist_data)
                                            #id_exist_data = str(id_exist_data)
                                            if(str(id_class_exist_data)=='None'):
                                                print("Inside of insert query ")
                                                insert_query = 'INSERT INTO tbl_attends_students_list(class_id, student_id, student_name, updated_time, rssi_value, branch_id, room_id) VALUES (%s,%s,%s,%s,%s,%s,%s)', (class_id, student_id, student_name, time_stamp, beacon_rssi, branch_id, room_id)
                                                result = Query.commit(insert_query)
                                                print("Data Inserted Successfully in Attendance Table!!!!")
                                            else:
                                                #update 
                                                update_query = ('UPDATE tbl_attends_students_list SET class_id= (%s), student_name = (%s), updated_time = (%s), rssi_value = (%s), branch_id = (%s), room_id = (%s) where student_id = (%s)',(class_id, student_name, time_stamp,beacon_rssi,branch_id, room_id,student_id))
                                                    # Update a previous recordupdated_time
                                                result = Query.commit(update_query)
                                                print("Data updated in Attendance Table!!")


                    #------------INSERT student in attendance table-------------------
                            





                        #-------------Ignore rest of the code, those are for notification---------------------
                        #---------------Get Room Type from gateway id---------------

                        #get_room_type_query = ("SELECT room_type  from tbl_entry_gateway where gateway_id = '%s'" %(gateway_address))
                        #get_room_type_data = Query.get_a_record(get_room_type_query)
                        #print(get_room_type_data)
                        #curent_room_type = get_room_type_data[0]
                        #print("current room_type is-->", curent_room_type)
                        #---------------Get Room Type from gateway id---------------

                        #------Check from decision table student last status--------
                        #prev_room_type_query=("SELECT room_type from tbl_decision where student_id='%s'" %(student_id))
                        #prev_room_type_data = Query.get_a_record(prev_room_type_query)

                        #if(str(prev_room_type_data)=='None'):
                        #    select_query = ("SELECT room_type from tbl_entry_gateway where id = (%s)" %(class_id))
                        #    room_type_data = Query.get_a_record(select_query)

                        #    room_type = room_type_data[0]
                        #    print("room_type for new student", room_type)
                        #    insert_query = ("INSERT INTO tbl_decision(student_id, room_type) VALUES (%s, %s)", (student_id, room_type))
                        #    result = Query.commit(insert_query)
                        #    print("Data Inserted Successfully for new comer!!")

                        #    prev_room_type = room_type
                        #else:
                        #    prev_room_type= prev_room_type_data[0]
                        #    print("prev_room_type is --> ", prev_room_type)
                        #------Check from decision table student last status--------

                        #---If consecutive two 0 in class room and two 1 in washroom----------
                        #if(prev_room_type=='washroom' and curent_room_type == 'washroom'):
                        #    print("Student is in washroom, send notification")
                        #    print("True")
                            
                            #student_id 
                            #student_name
                            #alarm_status


                        #    alarm_status = "True"
                        #    message = "washroom"

                            #---------Send Student_id, student_name and alarm_status----
                            #insert_query = ('INSERT INTO tbl_api_notification(student_id, student_name, message, updated_time) VALUES (%s,%s,%s,%s)',(student_id, student_name, message, time_stamp))    
                            #result = Query.commit(insert_query)
                            #print("Data Inserted Successfully!!")

                        #    id_exist_query = ("SELECT student_id from tbl_api_notification where student_id = (%s)"%(student_id))
                        #    id_exist_data = Query.get_a_record(id_exist_query)
                            
                        #    print("id_exist -->", id_exist_data)
                        #    id_exist_data = str(id_exist_data)
                        #    if(id_exist_data=='None'):
                        #        print("student id is not in tbl_api_notification")

                        #        insert_query = ('INSERT INTO tbl_api_notification(student_id, student_name, message, updated_time) VALUES (%s,%s,%s,%s)',(student_id, student_name, message, time_stamp))    
                        #        print("insert query--->", insert_query)
                        #        result = Query.commit(insert_query)
                        #        print("Data Inserted Successfully!!")

                        #    else:
                        #        id_exist = id_exist_data[0]
                        #        print("student id is in tbl_api_notification")
                        #        update_query = ('UPDATE tbl_api_notification SET student_name = (%s), message = (%s), updated_time = (%s) where student_id = (%s)',(student_name, message,time_stamp, student_id))
                        #        print("Update query--->", update_query)
                                # Update a previous record
                        #        result = Query.commit(update_query)
                        #        print("Data Updated Successfully in tbl_api_notification!!!")
                            #---------Send Student_id, student_name and alarm_status----

                        #if(prev_room_type=='classroom' and curent_room_type == 'classroom'):
                        #    print("Student in classroom, no need to send any notification")
                        #    print("False")
                        #else:
                        #    print("False")
                        #    alarm_status = "False"
                        #---If consecutive two 0 in class room and two 1 in washroom---------- 
                        #-------------Ignore  those are for nootification---------------------

                #i+=1



    


            return "Hello"

            #############################################################################


        except Exception as e:
            print ("Caught exception socket.error : %s \n" % e)
    #############################################################################
