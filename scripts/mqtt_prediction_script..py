import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
import pandas as pd
import json
from ast import literal_eval
import tensorflow as tf
from tensorflow import keras

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
      print("Connection failed")

normal_usage = np.zeros(shape=(1,0))
no_usage = np.zeros(shape=(1,0))
count = 0
normal_usage_min = 0
no_usage_max = 0

# Load in the history
df_history = pd.read_csv(r'../csv_files/dataset-na-krokus/pc_faked_test_shaped.csv', parse_dates=['timestamp'])
df_history = df_history.drop(columns=['timestamp'])
df_history.dropna()
history_array = np.array(df_history)
print(history_array)

# Numpy array for the new values that were sent
latest_value = np.zeros(shape=(1,0))

def on_message(client, userdata,message):
    global latest_value
    global normal_usage
    global no_usage
    global user_input
    global count
    global normal_usage_min
    global no_usage_max
    print("normal usage: ",  normal_usage)
    print("standby: " , no_usage)
    if (normal_usage.size < 12):
        # user_input = input("Press enter to calculate the state for nomal usage")
        bytes_array = message.payload.decode('utf8')
        json_object = json.loads(bytes_array)
        print(json_object)
        normal_usage = np.append(normal_usage, [json_object["ENERGY"]["Power"]])
        # print(normal_usage)
    elif (normal_usage.size == 12 and count == 0):
        print("!!!!!!!!!!!!!!!!!!!!!!!!! YOU GOT 60 SECONDS TO CHANGE TO STANDBY CONSUMPTION !!!!!!!!!!!!!!!!!!!!!!!!!")
        count += 1
        print(count)
    elif (normal_usage.size == 12 and count < 6):
        count+=1
    if (normal_usage.size == 12 and count ==6 and no_usage.size < 12):
        # if(no_usage.size==0): input("Press enter to calculate the state for no/standby usage")
        bytes_array2 = message.payload.decode('utf8')
        json_object2 = json.loads(bytes_array2)
        print(json_object2)
        no_usage = np.append(no_usage, [json_object2["ENERGY"]["Power"]])
        # print(no_usage)
    if (normal_usage.size == 12 and no_usage.size == 12):
        normal_usage_min = np.amin(normal_usage)
        print(normal_usage_min)
        no_usage_max = np.amax(no_usage)
        print(no_usage_max)

    if (normal_usage_min == np.amin(normal_usage)):
        bytes_array3 = message.payload.decode('utf8')
        json_object3 = json.loads(bytes_array3)
        print(json_object3)

        # Take the timestamp and split it into hour, minute, day_of_the_month, day_of_the_week, month
        time_stamp = json_object3["Time"]
        time_stamp = pd.to_datetime(time_stamp, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format
        # print(time_stamp)
        hour = time_stamp.hour
        # print(hour)
        minute = time_stamp.minute
        # print(minute)
        day_of_month = time_stamp.day
        # print(day_of_month)
        day_of_week = time_stamp.weekday()
        # print(day_of_week)
        month = time_stamp.month
        # print(month)
        power = json_object3["ENERGY"]["Power"]
        # Convert the power to the state
        if (power >= normal_usage_min):
            state = 1
        elif (power <= no_usage_max):
            state = 0
        # Add the latest values to a numpy array 
        if ((latest_value.size)/6 <= 1):
            latest_value = np.append(latest_value, [state, hour, minute, day_of_month, day_of_week, month])
        if ((latest_value.size/6) > 1):
            latest_value = np.delete(latest_value, [0,1,2,3,4,5])
        print("latest value from the plug", latest_value)

        


# def on_message(client, userdata, message):
    # print(message.payload.decode())
    # Convert the message to a json_object
    # bytes_array = message.payload.decode('utf8')
    # json_object = json.loads(bytes_array)
    # print(json_object)

    # Take the timestamp and split it into hour, minute, day_of_the_month, day_of_the_week, month
    # time_stamp = json_object["Time"]
    # time_stamp = pd.to_datetime(time_stamp, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format
    # print(time_stamp)
    # hour = time_stamp.hour
    # print(hour)
    # minute = time_stamp.minute
    # print(minute)
    # day_of_month = time_stamp.day
    # print(day_of_month)
    # day_of_week = time_stamp.weekday()
    # print(day_of_week)
    # month = time_stamp.month
    # print(month)

    # # Power
    # power = json_object["ENERGY"]["Power"]
    # print(power)


model = keras.models.load_model('../models/model_prediction/model_saved_statePredictionFake4min') # Load in the prediction model

Connected = False   #global variable for the state of the connection
  
broker_address= "10.15.51.63"  #Broker address
port = 1883  #Broker port
user = "VIVESStopContact"       #Connection username
password = "stop123"            #Connection password
  
client = mqttClient.Client("Prediction")               #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

user_input = input("Press enter to calculate the state for nomal usage")

client.loop_start() #start the loop

if (user_input == ""):
    client.subscribe("tele/box_plug/SENSOR")

while Connected != True: #Wait for connection
    time.sleep(0.1)
  
# client.subscribe("tele/pc_plug/SENSOR") # Subscribe to the topic

try:
    while True:
        time.sleep(1)
  
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()