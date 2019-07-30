import paho.mqtt.client as mqttClient
import Beacon_Data_Processing
#from bullying_store_Sensor_Data_to_DB import sensor_Data_Handler


class PassData(Beacon_Data_Processing.Processing):
    pass

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	#client.subscribe("/gw/ac233fc023b1/status") #Gateway for Dhaka
	#client.subscribe("/gw/ac233fc023a0/status") #Gateway for Florida
	#client.subscribe("$aws/things/${00002523}/shadow/update")
	client.subscribe("/Bleschool1")
	#kbeacon/publish
	#kbeacon/pubaction/D03304000922
	#kbeacon/subaction/D03304000922
	

#ac233fc023b1

def on_message(client, userdata, msg):
	#print(msg.topic +" " + str(msg.payload))
	#client = mqtt.Client()
	data = str(msg.payload.decode())
	# print(data)

	#sensor_Data_Handler(msg.topic, data)

	new_object = PassData()
	
    # Pass received data stream as an argument of function device_data_process
	feedback = new_object.device_data_process(data)
	# print(data)
	print("data send to Processing Class!!")
	#sensor_Data_Handler(msg.topic, data)

#broker_address= "182.163.112.205"
#port = 1883
#user = "sme"
#password = "Sme@123@Mqtt"


#client =mqtt.Client("SmartSchool")
broker_address= "broker.hivemq.com"
port=1883

user = "kkm"
password = "kkm123456"

#broker_address= "a1ek3lbmx2jfb9-ats.iot.eu-west-1.amazonaws.com:8883"
#port = 8883

client = mqttClient.Client("kb_client_D03304000922") 

client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port=port)
client.loop_forever()



#/gw/ac233fc023b1/status

#ssh -L 5901:localhost:5901 -i "dmacloudkey.pem" ubuntu@ec2-3-18-85-242.us-east-2.compute.amazonaws.com




	