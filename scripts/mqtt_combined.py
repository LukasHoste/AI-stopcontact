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
from influxdb import InfluxDBClient

# Import class
from prediction_cl import MqttPrediction

# Global variables
normal_usage = np.zeros(shape=(1,0)) # Numpy array for all the normal usage values
states = 0 # Variable for the normal state
status_counter = 0 # A variable to go to the next if-statement, for example the history
message_counter = 0 # A variable
history_array = np.zeros(shape=(1,0)) # Numpy array for the history values
latest_value = np.zeros(shape=(1,0)) # Numpy array for the new values that were sent

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months_of_year = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


flux_client = InfluxDBClient(host= '10.15.51.63', port=8086, username='plug2',password='stop123')
print(flux_client.get_list_database())
flux_client.switch_database('plug_database')

# Load in the history
df_history = pd.read_csv(r'../csv_files/multiple-devices-csv/synthetic_test_faked.csv', parse_dates=['timestamp'])

# Load in the model
model = keras.models.load_model('../models/models_multiple_devices/2devices_lukas')
classification_model = keras.models.load_model('../models/classification_17-04') # loads the model

# Load in the scaler (this was saved from the notebook where the model was trained)
scaler = joblib.load('scaler_2_devices.gz')

classification_scaler = joblib.load('scaler(17-04).gz') # load the scaler, fitted during training

once = True

device = 0

CLASSES=['box', 'laptop', 'monitor', 'pc', 'phone', 'printer','switch','tv'] # list of all the classes, this has to be in the same order as during training

prediction_arrays = {} # dictionary for all the arrays that contain the data to make a prediction
prediction_state = {}

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
    global days_of_week
    global months_of_year
    global device

    # # classification of device here
    print(message.topic) # print of what topic the received message comes from
    # if the topic is not yet in the dictionary, add the topic name as a key to the dictionary and fill it with an empty array
    if(not str(message.topic) in prediction_arrays):
        print("adding topic key to the dictionary :)")
        prediction_arrays[str(message.topic)] = np.zeros(shape=(1,0))
        print("adding key to check if a prediction has already been made")
        prediction_state[str(message.topic)] = False

    
    if((prediction_arrays[str(message.topic)].size/4) <= 29):
        print("executing block one of classification")
        print(prediction_arrays[str(message.topic)].size)
        prediction_arrays[str(message.topic)] = np.append(prediction_arrays[str(message.topic)],[json_object["ENERGY"]["ApparentPower"],
        json_object["ENERGY"]["Current"],
        # json_object["ENERGY"]["Factor"],
        json_object["ENERGY"]["Power"],
        json_object["ENERGY"]["ReactivePower"]
        ])
        print(prediction_arrays[str(message.topic)]) # print the current prediction array
        normal_usage = np.append(normal_usage, [json_object["ENERGY"]["Power"]]) # Append the normal usage values to a numpy array
    # append new values and make a prediction
    elif(not (prediction_state[str(message.topic)])):
        print(normal_usage)
        print(len(normal_usage))
        print("executing block two of classification (making the prediction)")
        # # add latest values
        # prediction_arrays[str(message.topic)] = np.append(prediction_arrays[str(message.topic)]
        # ,[json_object["ENERGY"]["ApparentPower"],
        # json_object["ENERGY"]["Current"],
        # # json_object["ENERGY"]["Factor"],
        # json_object["ENERGY"]["Power"],
        # json_object["ENERGY"]["ReactivePower"]
        # ])
        # # remove oldest values
        # prediction_arrays[str(message.topic)] = np.delete(prediction_arrays[str(message.topic)],[0,1,2,3])
        # reshape the array for prediction
        prediction_arrays[str(message.topic)] = prediction_arrays[str(message.topic)].reshape((1,120))
        # scale/normalize the values in the array
        transformed_array = classification_scaler.transform(prediction_arrays[str(message.topic)]) # copy to not change the original array
        # make a prediction
        pred_test = classification_model.predict(transformed_array)
        print(pred_test)
        # get the index of the highest prediction
        class_index = np.argmax(pred_test)
        print(class_index)
        # get the class name
        print("predicted device: ",CLASSES[class_index])
        # for the demo there are only two devices thus we dont use the index
        
        if(CLASSES[class_index] == "box"):
            device = 1
        print(device)
            
        print(pred_test)
        # send the result of the prediction back to the topic
        client.publish(message.topic + "/prediction",CLASSES[class_index]) 
        if(once == True):
            print(once)
            print("this topic should only be done once")
            prediction_state[str(message.topic)] = True    
    
    # prediction part starts here

    # elif (normal_usage.size < 1): # Determine what the normal usage of a device is.
    #     print(json_object)
    #     normal_usage = np.append(normal_usage, [json_object["ENERGY"]["Power"]]) # Append the normal usage values to a numpy array
    #     print("normal usage: ",  normal_usage)

    # Second part is to make the prediction 
    elif (normal_usage.size == 30):
 
        extracted_value = mqtt_prediction.extract_object(json_object, states) # Extracting the values from the json object
        print("These are the extracted values: ", extracted_value)

        # Create the history array and determine the state
        if (status_counter == 0):
            states = mqtt_prediction.state_determination(normal_usage)
            print("This is the normal usage power: ", states)
            print("The last message added to the history: ", json_object)
            history_dataset = mqtt_prediction.history_creation(json_object, df_history, scaler, device)[0] # Creating our own history (one week)
            history_dataset_time = mqtt_prediction.history_creation(json_object, df_history, scaler, device)[1] # Creating our own history (one week)
            global history_array
            history_array = np.array(history_dataset) # Change the history dataset to a numpy array
            history_time = np.array(history_dataset_time) # Change the history dataset to a numpy array
            formatted_data = []
            for row in history_time:
                timestamp = row[0]
                state = row[1]

                formatted_row = {
                    "measurement": "box_history_final",
                    "time": timestamp,
                    "fields": {
                      "state": float(state)
                    }
                }
                formatted_data.append(formatted_row)

            # print(formatted_data)
            flux_client.write_points(formatted_data)


        # When the history is created then the first prediction can be made
        elif (status_counter >= 1 and message_counter == 24):
            print("THIS IS PREDICTION NUMBER: ", status_counter)
            global latest_value
            print("The new last message added to the history: ", json_object)

            print("This is the oldest mqtt message: ", latest_value) 
            if ((latest_value.size)/6 < 1): 
                latest_value = np.append(latest_value, [extracted_value[0], extracted_value[1], extracted_value[2], extracted_value[3], extracted_value[4], device]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            else:
                latest_value = np.delete(latest_value, [0,1,2,3,4,5]) # Delete the latest values first to get an empty numpy array
                latest_value = np.append(latest_value, [extracted_value[0], extracted_value[1], extracted_value[2], extracted_value[3], extracted_value[4], device]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            print("This is the latest mqtt message: ", latest_value)
            history_array = np.vstack((history_array, latest_value)) # Add the latest value from MQTT to the history array
            history_array = np.delete(history_array, 0, axis=0) # Remove the first value from the history array
            prediction_array = history_array.reshape((1,2520,6)) # Reshape for the prediction
            print(prediction_array)
            pred = model.predict(prediction_array) # The prediction
            print("The prediction of the next state: ", pred)
            client.publish(message.topic + "/latest", "latest prediction = " + str(pred[0][0]) + " ,hour = " + str(extracted_value[1]) + " ,minute = " + str(extracted_value[2]) + " ,day of the week = " + days_of_week[extracted_value[3]] + " ,month =" + months_of_year[extracted_value[4]])


            # Some code to change te plug state
            if(pred > 0.015):
                client.publish(message.topic + "/usagePrediction", "on")
            else: 
                client.publish(message.topic + "/usagePrediction", "off")
            message_counter = 0
        status_counter = status_counter + 1 # This is to go to the next if statement
        message_counter += 1
        print("message counter is now: ", message_counter)

Connected = False   # global variable for the state of the connection
  
broker_address = "mqtt.devbit.be"
port = 1883  #Broker port

client = mqttClient.Client("Prediction_2_awooga")         #create new instance
# client.username_pw_set(user, password=password)  #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

user_input = input("Press enter to calculate the state for nomal usage and classify the device")

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