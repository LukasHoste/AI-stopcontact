# Imports
import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
import pandas as pd
import json
from ast import literal_eval
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import joblib

# Import class
from prediction_cl import MqttPrediction

# Global variables
normal_usage = np.zeros(shape=(1,0)) # Numpy array for all the normal usage values
states = 0 # Variable for the normal state
status_counter = 0 # A variable to go to the next if-statement, for example the history
message_counter = 0 # A variable
history_array = np.zeros(shape=(1,0)) # Numpy array for the history values
latest_value = np.zeros(shape=(1,0)) # Numpy array for the new values that were sent

# Load in the history
df_history = pd.read_csv(r'./data/synthetic_test_faked_new.csv', parse_dates=['timestamp'])

# Load in the model
model = keras.models.load_model('./model/2devices_weak_sloped')

# Load in the scaler (this was saved from the notebook where the model was trained)
scaler = joblib.load('./scaler/scaler_new.gz')

# Method to connect to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  #Use global variable
        Connected = True  #Signal connection 
    else:
      print("Connection failed")

# The on message method
def on_message(client, userdata, message):
    # Create class object
    mqtt_prediction = MqttPrediction()

    # Decode message
    bytes_array = message.payload.decode('utf8') # Get the message from the payload
    global json_object
    json_object = json.loads(bytes_array) # Convert the message to a json object

    # First part is to determine the on/off-state of the device
    global normal_usage
    global states
    global status_counter
    global message_counter

    if (normal_usage.size < 1): # Determine what the normal usage of a device is.
        print(json_object)
        normal_usage = np.append(normal_usage, [json_object["ENERGY"]["Power"]]) # Append the normal usage values to a numpy array
        print("normal usage: ",  normal_usage)

    # Second part is to make the prediction 
    elif (normal_usage.size == 1):
        extracted_value = mqtt_prediction.extract_object(json_object, states) # Extracting the values from the json object
        print("These are the extracted values: ", extracted_value)

        # Create the history array and determine the state
        if (status_counter == 0):
            states = mqtt_prediction.state_determination(normal_usage)
            print("This is the normal usage power: ", states)
            # print("The last message added to the history: ", json_object)
            global history_dataset
            history_dataset = mqtt_prediction.history_creation(df_history) # Creating our own history (one week)
            # global history_array
            # history_array = np.array(history_dataset) # Change the history dataset to a numpy array
            # print(history_array)
            print(history_dataset)

        # When the history is created then the first prediction can be made
        elif (status_counter >= 1 and message_counter == 1): # 24
            # print("THIS IS PREDICTION NUMBER: ", status_counter)
            latest_time = history_dataset['timestamp'].iloc[-1] # Retrieve the latest time from the history dataset
            print("THIS IS THE LATEST TIME: ", latest_time)
            latest_time = latest_time + timedelta(0,240) # Add 4 minutes to the latest time
            print("THIS IS THE TIME WITH + 4min: ", latest_time)
            global scaled_history
            # print(history_dataset)
            scaled_history = history_dataset.copy() # Take a copy from the original history
            scaled_history = mqtt_prediction.scaled_history(scaled_history, scaler) # Scale the history
            # print(scaled_history)
            global scaled_history_array
            scaled_history_array = np.array(scaled_history) # Change the history dataset to a numpy array
            new_row = {'timestamp': latest_time, 'state': extracted_value}
            history_dataset = history_dataset.append(new_row, ignore_index=True) # Add the latest time and state (+4min) to the original history
            history_dataset = history_dataset.drop(0) # Drop the first row from the original dataset
            print("THIS IS THE NEW HISTORY DATASET: ", history_dataset)
            hour = latest_time.hour # extract the features of the latest time
            minute = latest_time.minute
            day_of_week = latest_time.weekday()
            global latest_value
            # print("The new last message added to the history: ", json_object)
            print("This is the oldest mqtt message: ", latest_value) 
            if ((latest_value.size)/5 < 1): 
                latest_value = np.append(latest_value, [extracted_value, hour, minute, day_of_week, 1]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            else:
                latest_value = np.delete(latest_value, [0,1,2,3,4]) # Delete the latest values first to get an empty numpy array
                latest_value = np.append(latest_value, [extracted_value, hour, minute, day_of_week, 1]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            print("This is the latest mqtt message: ", latest_value)
            scaled_history_array = np.vstack((scaled_history_array, latest_value)) # Add the latest value from MQTT to the history array
            scaled_history_array = np.delete(scaled_history_array, 0, axis=0) # Remove the first value from the history array
            prediction_array = scaled_history_array.reshape((1,2520,5)) # Reshape for the prediction
            print(prediction_array)
            pred = model.predict(prediction_array) # The prediction
            print("The prediction of the next state: ", pred)

            # Some code to change te plug state
            # if(pred > 0.4):
            #     client.publish(message.topic + "/usagePrediction", "on")
            # elif(pred < 0.8): 
            #     client.publish(message.topic + "/usagePrediction", "off")
            message_counter = 0

        status_counter = status_counter + 1 # This is to go to the next if statement
        message_counter += 1
        print("message counter is now: ", message_counter)

Connected = False   # global variable for the state of the connection
  
broker_address = "mqtt.devbit.be"
port = 1883  #Broker port

client = mqttClient.Client("Prediction_2_")         #create new instance
# client.username_pw_set(user, password=password)  #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

user_input = input("Press enter to calculate the state for nomal usage")

client.loop_start() #start the loop

if (user_input == ""): # When the user presses enter, it will subscribe to the topic
    client.subscribe("ai-stopcontact/plugs/tele/box_plug/SENSOR")

while Connected != True: #Wait for connection
    time.sleep(0.1)

try:
    while True:
        time.sleep(1)
  
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()