
import yaml
import collections # For creating ordered dictionary
import json # For creating json data
import os
from pathlib import Path
import statistics
import itertools

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

push_service = FCMNotification(api_key="AAAAESI3hQM:APA91bE1zeJYip6WcfWdJjwDkuy7r4We9MwgWg_Xl_Y1oNQ2EAEmW_9odvOhct8R6GldgXVtJ-mRSoWse5Q5QaHcQ8P0abErn_EpRm9S1q18B6yPFCp-utg-enym148w51sHU1-ae9mX")
#--------------------------

def hex_to_signed(source):
    
    # This assumes that source is the proper length, and the sign bit
    # is the first bit in the first byte of the correct length.

    # hex_to_signed("F") should return -1.
    # hex_to_signed("0F") should return 15.
    
    if not isinstance(source, str):
        raise ValueError("string type required")
    if 0 == len(source):
        raise ValueError("string is empty")
    sign_bit_mask = 1 << (len(source)*4-1)
    other_bits_mask = sign_bit_mask - 1
    value = int(source, 16)
    return -(value & sign_bit_mask) | (value & other_bits_mask)

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

            student_query="SELECT beacon_id FROM tbl_entry_beacon WHERE status=1" %()
            # print(type(student_query))
            student_data = Query.get_all_record(student_query)
            data_std = json.dumps(student_data)
            print("____________Student Data_________\n",data_std)

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

                    if len(data_load) == 52 and beacon_mac_address in data_std:
                        print("++++++++++++++ Acc data +++++++++++++")
                        # print(beacon_mac_address)
                        # print(data_load)

                        # Decoding accelerometer data
                        acc_x = hex_to_signed((k['rawData'][-16:-12]))
                        acc_y = hex_to_signed((k['rawData'][-20:-16]))
                        acc_z = hex_to_signed((k['rawData'][-24:-20]))

                        # print(k['mac'],acc_x)
                        # print(k['mac'],acc_z)
                        # print(k['mac'],acc_y)

                        # dumping the accelerometer data to the db
                        insert_query = 'INSERT INTO `tbl_acc`(`gateway_id`, `beacon_id`, `acc_x`, `acc_y`, `acc_z`) VALUES (%s,%s,%s,%s,%s)', (gateway_address, beacon_mac_address, acc_x, acc_y, acc_z)
                        result = Query.commit(insert_query)


                        # Finding the Standard deviation & dumping to the db
                        # print("dfsfd")
                        # acc_query = ("SELECT gateway_id, beacon_id, acc_x, acc_y, acc_z, DATE_FORMAT(time, '%%Y-%%m-%%d %%H:%%i:%%s') as date_time FROM tbl_acc WHERE beacon_id=%s ORDER BY id DESC LIMIT 6"), (beacon_mac_address)


                        acc_query="SELECT gateway_id, beacon_id, acc_x, acc_y, acc_z, DATE_FORMAT(time, '%%Y-%%m-%%d %%H:%%i:%%s') as date_time FROM tbl_acc WHERE beacon_id='%s' ORDER BY id DESC LIMIT 6" %(beacon_mac_address)
                        print(type(acc_query))
                        acc_data = Query.get_all_record(acc_query)
                        # print(acc_data)

                        

                        json_rows_1  = json.dumps(acc_data)
                        json_rows_2 = json.loads(json_rows_1)

                        acc_x_list = []
                        acc_y_list = []
                        acc_z_list = []
                        temperature_list = []
                        time_list = []

                        for row in json_rows_2:
                            print(row)

                            gateway_address = row[0]

                            # print(gateway_address)
                            acc_x_list.append((row[2]))
                            acc_y_list.append((row[3]))
                            acc_z_list.append((row[4]))
                            time_list.append((row[5]))
                            
                        print(time_list)
                        print("-----------------------")

                        time1 = time_list[0]

                        if len(temperature_list) < 2:
                            sd_temperature = 0
                        else:
                            sd_temperature = statistics.pstdev(temperature_list)

                        if len(acc_x_list) < 2:
                            sd_acc_x = 0
                        else:
                            sd_acc_x = statistics.pstdev(acc_x_list)

                        if len(acc_y_list) < 2:
                            sd_acc_y = 0
                        else:
                            sd_acc_y = statistics.pstdev(acc_y_list)

                        if len(acc_z_list) < 2:
                            sd_acc_z = 0
                        else:
                            sd_acc_z = statistics.pstdev(acc_z_list)
                        print("complete___________________")



                        if sd_acc_x > 1 and sd_acc_y > 1 and sd_acc_z > 1:
                            registration_id = "fvEycKqg5Ng:APA91bGYIx4Opa7h8NlD5jvJniVvWl1SoHG6uq2Avb37h7eNONt1PbS5s0xWh716lpYA7qlF20ML2g_fOFWkrLXItG-MvlVedDT_Fy7rPMmKWA3h4v_fVCvIE610h3ftP6mwoZUT1ThJ"
                            # message_alert="Alert!!"
                            # message_title = "High movement"
                            message_title = "Bully"
                            # message_body = "Floor ID : " + gateway_address+"/n"+ "Student ID : " + Device_Id
                            message_body = "Student ID : " + beacon_mac_address
                            movement_status = "Please Check!!!"
                            # cursor2 = conn.cursor() 
                            # cursor3 = conn.cursor()  
                            # sql_ckh = "SELECT * FROM notification WHERE device_id = %s"
                            # cursor3.execute(sql_ckh,Device_Id)
                            # row = cursor3.fetchone()
                            # print(row)
                            # row_device = row['device_id']
                            # row_time = row['time']
                            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            # current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                            # time_difference  = current_time - row_time       
                            # time_difference_in_minutes = time_difference / timedelta(minutes=1)    
                            # if time_difference_in_minutes >=3:
                            #     print('get a diff')
                            #     sql2 = "UPDATE notification SET notification = %s WHERE device_id = %s"
                            #     cursor2.execute(sql2, (movement_status, Device_Id) )
                            #     conn.commit()
                            
                            result = push_service.notify_single_device(registration_id=registration_id,message_title=message_title, message_body=message_body)
                            print("---------------------FCM Executed----------------")
                            # print(result)

                            #------------Change notification status on db-------------#
                            try:
                                update_notification_querry = "UPDATE `tbl_notification_status_check` SET `status`=1 WHERE `status_type` =%s", ("bully")
                                result = Query.commit(update_notification_querry)
                                print("--------------notification status changed------------")
                            except Exception as e:
                                print("e")

                            # else:
                            #     pass

                            # cursor2.close()
                            # cursor3.close()

                            # # print (result)
                        else:
                            movement_status = "Movement Normal"
                        
                        insert_query = 'INSERT INTO `tbl_acc_notification`(`gateway_id`, `beacon_id`, `sd_acc_x`, `sd_acc_y`, `sd_acc_z`, `movement_status`) VALUES (%s,%s,%s,%s,%s,%s)', (gateway_address, beacon_mac_address, sd_acc_x, sd_acc_y, sd_acc_z, movement_status)
                        result = Query.commit(insert_query)



                    elif len(data_load) == 50:
                        print("++++++++++++++ Temp data +++++++++++++")
                        temp= int ((k['rawData'][-20:-18]),16) + int ((k['rawData'][-18:-16]),16)/256
                        print(temp)
                        # insert_query = 'INSERT INTO `tbl_temp`(`gateway_id`, `beacon_id`, `temp`) VALUES (%s,%s,%s)', (gateway_address, beacon_mac_address, temp)
                        # result = Query.commit(insert_query)
                    else:
                        pass
                        

            #############################################################################

# # How to do querry # #
# Get querry
# student_id_query = ("SELECT student_id from tbl_entry_beacon where beacon_id = '%s'" %(beacon_mac_address))
# student_id_data = Query.get_a_record(student_id_query)
# print("student_data --> ",student_id_data)


# Insert querry
# insert_query = 'INSERT INTO tbl_attends_students_list(class_id, student_id, student_name, updated_time, rssi_value, branch_id, room_id) VALUES (%s,%s,%s,%s,%s,%s,%s)', (class_id, student_id, student_name, time_stamp, beacon_rssi, branch_id, room_id)
# result = Query.commit(insert_query)
# print("Data Inserted Successfully in Attendance Table!!!!")

# # ############################################################################# ##


        except Exception as e:
            print ("Caught exception socket.error : %s \n" % e)
    #############################################################################
