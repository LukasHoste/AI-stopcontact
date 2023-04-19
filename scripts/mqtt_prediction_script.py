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
history_array = np.zeros(shape=(1,0)) # Numpy array for the history values
latest_value = np.zeros(shape=(1,0)) # Numpy array for the new values that were sent

# Load in the history
df_history = pd.read_csv(r'../csv_files/synthetic-data/synthetic_data_fast_switch.csv', parse_dates=['timestamp'])

# Load in the model
model = keras.models.load_model('../models/model_prediction/fake_prediction_state_synthetic')

# Load in the scaler (this was saved from the notebook where the model was trained)
scaler = joblib.load('scaler_fake_transfer.gz')

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
    global no_usage
    global states
    global status_counter

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
            history_dataset = mqtt_prediction.history_creation(json_object, df_history, scaler) # Creating our own history (one week)
            global history_array
            history_array = np.array(history_dataset) # Change the history dataset to a numpy array

        # When the history is created then the first prediction can be made
        elif (status_counter >= 1):
            print("THIS IS PREDICTION NUMBER: ", status_counter)
            global latest_value
            print("This is the oldest mqtt message: ", latest_value) 
            if ((latest_value.size)/5 < 1): 
                latest_value = np.append(latest_value, [extracted_value[0], extracted_value[1], extracted_value[2], extracted_value[3], extracted_value[4]]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            else:
                latest_value = np.delete(latest_value, [0,1,2,3,4]) # Delete the latest values first to get an empty numpy array
                latest_value = np.append(latest_value, [extracted_value[0], extracted_value[1], extracted_value[2], extracted_value[3], extracted_value[4]]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            print("This is the latest mqtt message: ", latest_value)
            history_array = np.vstack((history_array, latest_value)) # Add the latest value from MQTT to the history array
            history_array = np.delete(history_array, 0, axis=0) # Remove the first value from the history array
            prediction_array = history_array.reshape((1,2520,5)) # Reshape for the prediction
            print(prediction_array)
            pred = model.predict(prediction_array) # The prediction
            print("The prediction of the next state: ", pred)

            # Some code to change te plug state
            # if(prediction_test > 0.015):
            #     client.publish(message.topic + "/usagePrediction", "on")
        status_counter = status_counter + 1 # This is to go to the next if statement

Connected = False   # global variable for the state of the connection
  
broker_address = "mqtt.devbit.be"
port = 1883  #Broker port

client = mqttClient.Client("Prediction_2")         #create new instance
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