import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
import pandas as pd
import json
from ast import literal_eval
import tensorflow as tf
from tensorflow import keras
from datetime import datetime, timedelta

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
      print("Connection failed")

# Global variables
normal_usage = np.zeros(shape=(1,0))
no_usage = np.zeros(shape=(1,0))
count = 0
normal_usage_min = 0
no_usage_max = 0
state = 0
state_checked = 0
history_array = np.zeros(shape=(1,0))
day = 60*60*24
week = 7*day
# year = 365.2425*day

# Load in the history
df_history = pd.read_csv(r'../csv_files/dataset-na-krokus/pc_fake_test2_1w.csv', parse_dates=['timestamp'])

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
    global state_checked
    global df_history
    global history_array
    global state
    global day
    global week

    if (normal_usage.size < 1):
        # user_input = input("Press enter to calculate the state for nomal usage")
        bytes_array = message.payload.decode('utf8')
        json_object = json.loads(bytes_array)
        print(json_object)
        normal_usage = np.append(normal_usage, [json_object["ENERGY"]["Power"]])
        print("normal usage: ",  normal_usage)
        # print(normal_usage)
    elif (normal_usage.size == 1 and count == 0):
        print("!!!!!!!!!!!!!!!!!!!!!!!!! YOU GOT 60 SECONDS TO CHANGE TO STANDBY CONSUMPTION !!!!!!!!!!!!!!!!!!!!!!!!!")
        count += 1
        print(count)
    elif (normal_usage.size == 1 and count < 2):
        count+=1
    if (normal_usage.size == 1 and count == 2 and no_usage.size < 1):
        # if(no_usage.size==0): input("Press enter to calculate the state for no/standby usage")
        bytes_array2 = message.payload.decode('utf8')
        json_object2 = json.loads(bytes_array2)
        print(json_object2)
        no_usage = np.append(no_usage, [json_object2["ENERGY"]["Power"]])
        print("standby: " , no_usage)
        # print(no_usage)
    if (normal_usage.size == 1 and no_usage.size == 1):
        normal_usage_min = np.amin(normal_usage)
        print(normal_usage_min)
        no_usage_max = np.amax(no_usage)
        print(no_usage_max)

    if (normal_usage_min == np.amin(normal_usage)):
        bytes_array3 = message.payload.decode('utf8')
        json_object3 = json.loads(bytes_array3)
        print(json_object3)
        state_checked = state_checked + 1
        print("THIS IS THE CHECK", state_checked)
        # Take the timestamp and split it into hour, minute, day_of_the_month, day_of_the_week, month
        time_stamp = json_object3["Time"]
        time_stamp = pd.to_datetime(time_stamp, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format
        # print(time_stamp)

        # Manier van Jarno
        seconds = time_stamp.timestamp()
        # print(seconds)
        day_sin = np.sin(seconds * (2* np.pi / day))
        day_cos = np.cos(seconds * (2* np.pi / day))
        week_sin = np.sin(seconds * (2* np.pi / week))
        week_cos = np.cos(seconds * (2* np.pi / week))

        # Dit is ook voor dat van Lukas

        # hour = time_stamp.hour
        # # print(hour)
        # minute = time_stamp.minute
        # # print(minute)
        # day_of_month = time_stamp.day
        # # print(day_of_month)
        # day_of_week = time_stamp.weekday()
        # # print(day_of_week)
        # month = time_stamp.month
        # print(month)

        power = json_object3["ENERGY"]["Power"]
        # Convert the power to the state
        if (power >= normal_usage_min):
            state = 1
        if (power <= no_usage_max):
            state = 0

        if (state_checked == 1):
        # Create new timestamp
            mqtt_last_time = json_object3["Time"]

            mqtt_last_time = pd.to_datetime(mqtt_last_time, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format

            # Compute the timestamp one week before the last received time from MQTT
            fake_data_start_time = mqtt_last_time - pd.Timedelta(days=7)

            # Create a new timestamp sequence starting from fake_data_start_time and ending with mqtt_last_time, with a 4-minute increment
            new_timestamps = pd.date_range(start=fake_data_start_time, end=mqtt_last_time, freq='4T')

            # Slice the new timestamp sequence to the same length as the original fake data
            new_timestamps = new_timestamps[-len(df_history):]

            # Replace the timestamps in the fake data with the new timestamps
            df_history['timestamp'] = new_timestamps

            # Get it in the right shape for numpy array
            df_history.index = pd.to_datetime(df_history['timestamp'], format='%d.%m.%Y %H:%M:%S')

            # Manier van Jarno
            df_history['Seconds'] = df_history.index.map(pd.Timestamp.timestamp)
            print(df_history['Seconds'])
            df_history['Day sin'] = np.sin(df_history['Seconds'] * (2* np.pi / day))
            df_history['Day cos'] = np.cos(df_history['Seconds'] * (2 * np.pi / day))
            df_history['Week sin'] = np.sin(df_history['Seconds'] * (2 * np.pi / week))
            df_history['Week cos'] = np.cos(df_history['Seconds'] * (2 * np.pi / week))

            # Dit uncommenten om hetgene van Lukas terug te gebruiken

            # df_history['hour'] = df_history.index.hour
            # df_history['minute'] = df_history.index.minute
            # df_history['day_of_month'] = df_history.index.day
            # df_history['day_of_week'] = df_history.index.dayofweek
            # df_history['month'] = df_history.index.month
            # print(df_history)

            # Append the data to a numpy array
            df_history = df_history.drop(columns=['timestamp'])
            df_history = df_history.drop('Seconds', axis=1) # Dit zou ook moeten commented worden voor terug dat van Lukas
            df_history.dropna()
            history_array = np.array(df_history)
            print(history_array)
            print(history_array.shape)

        if (state_checked >= 2):
        # Add the latest values to a numpy array 
            if ((latest_value.size)/5 <= 1):
                # latest_value = np.append(latest_value, [state, hour, minute, day_of_month, day_of_week, month])
                latest_value = np.append(latest_value, [state, day_sin, day_cos, week_sin, week_cos])
                print(latest_value)
            if ((latest_value.size/5) > 1):
                # latest_value = np.delete(latest_value, [0,1,2,3,4,5])
                latest_value = np.delete(latest_value, [0,1,2,3,4])
                
            # print("latest value from the plug", latest_value)
            history_array = np.vstack((history_array, latest_value))
            # history_array = np.append((history_array), [state, hour, minute, day_of_month, day_of_week, month], axis=len(history_array + 1))
            history_array = np.delete(history_array, 0, axis=0)
            print(history_array)
            print(history_array.shape)
            prediction_array = history_array.reshape((1,2520,5))
            prediction_test = model.predict(prediction_array)
            print(prediction_test)

# Deze gaf wel resultaat maar dan zouden we moeten kijken voor een treshold toe te voegen (model van Lukas zonder de normalisatie)
# model = keras.models.load_model('../models/model_prediction/model_saved_statePredictionFake4min') # Load in the prediction model

# Deze predicte gwn constant het gemiddelde
#model = keras.models.load_model('../models/model_prediction/model_prediction_state_V1_day_week') # Load in the prediction model

model = keras.models.load_model('../models/model_prediction/model_prediction_state_V1_no_norm')

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
    client.subscribe("tele/pc_plug/SENSOR")

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