# Imports
import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
import os
import pandas as pd
import json
from ast import literal_eval
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import joblib
from influxdb import InfluxDBClient
from dotenv import load_dotenv

import argparse

# Import class
from prediction_cl import MqttPrediction

load_dotenv()

influx_user = os.environ.get('INFLUXDB_USER')
influx_pw = os.environ.get('INFLUXDB_PW')
broker = os.environ.get('MQTT_BROKER')
influxip = os.environ.get('INFLUX_ADDRESS')
mqtt_pw = os.environ.get('MQTT_PASS')

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()
    # Optional arguments
    parser.add_argument("-de", "--device", help="choose a device box or laptop", default='box')
    parser.add_argument("-mc", "--mqttclient", help="choose an mqtt client name", default='client')
    # add the --help option to the parser
    #parser.add_argument('--help', action='help', help='Show this help message and exit')
    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 0.8')
    # Parse arguments
    args = parser.parse_args()
    return args

args = parseArguments()
# print(args.history)

# Global variables
normal_usage = np.zeros(shape=(1,0)) # Numpy array for all the normal usage values
states = 0 # Variable for the normal state
status_counter = 0 # A variable to go to the next if-statement, for example the history
message_counter = 0 # A variable
history_array = np.zeros(shape=(1,0)) # Numpy array for the history values
latest_value = np.zeros(shape=(1,0)) # Numpy array for the new values that were sent

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months_of_year = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Load in the history
# df_history = pd.read_csv(r'./data/synthetic_test_faked_new.csv', parse_dates=['timestamp'])
if(args.device == "laptop"):
    df_history = pd.read_csv(r'/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/data/pc_jarno_1w.csv', parse_dates=['timestamp'])
elif(args.device == "box"):
    df_history = pd.read_csv(r'/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/data/synthetic_test_faked_new.csv', parse_dates=['timestamp'])
elif(args.device == "pc"):
    print("loading pc history")
    df_history = pd.read_csv(r'/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/data/PCSynth.csv', parse_dates=['timestamp'])
elif(args.device == "printer"):
    df_history = pd.read_csv(r'/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/data/PrinterSynth.csv', parse_dates=['timestamp'])
elif(args.device == "phone"):
    df_history = pd.read_csv(r'/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/data/PhoneSynth.csv', parse_dates=['timestamp'])
else:
    print("incorrect device from argument")
    exit()

# Load in the model
# model = keras.models.load_model('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/model/2devices_bidirectional')
# model = keras.models.load_model('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/model/2devices_bidirectional') #this is the old model that makes a prediction for box or laptop
model = keras.models.load_model('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/model/all_devicesV4')
classification_model = keras.models.load_model('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/model/classification_15-05_simple') # loads the model

# Load in the scaler (this was saved from the notebook where the model was trained)
scaler = joblib.load('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/scaler/scaler_all.gz')

classification_scaler = joblib.load('/home/vives/Documents/slim/SlimmeStopcontactenVIVES/scripts/Prediction_script_New/scaler/scaler_classificationshort.gz') # load the scaler, fitted during training

device = 0
# last_change = 0

# CLASSES=['box', 'laptop', 'monitor', 'pc', 'phone', 'printer','switch','tv'] # list of all the classes, this has to be in the same order as during training
CLASSES=['box', 'laptop', 'pc', 'phone', 'printer']


prediction_arrays = {} # dictionary for all the arrays that contain the data to make a prediction
prediction_state = {}

def influx_history(client, dataframe):
    history = np.array(dataframe) # Change the history dataset to a numpy array
    print(history, "history for influxdb")
    formatted_data = []
    for row in history:
        timestamp = row[0]
        state = row[1]
        formatted_row = {
            "measurement": "history" + args.device,
            "time": timestamp,
            "fields": {
                "state": float(state)
            }
        }
        formatted_data.append(formatted_row)

    # print(formatted_data)
    client.write_points(formatted_data)

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
    global device
    global days_of_week
    global months_of_year

    # ------------- classification -------------

    # if the topic is not yet in the dictionary, add the topic name as a key to the dictionary and fill it with an empty array
    if(not str(message.topic) in prediction_arrays):
        print("adding topic key to the dictionary :)")
        prediction_arrays[str(message.topic)] = np.zeros(shape=(1,0))
        print("adding key to check if a prediction has already been made")
        prediction_state[str(message.topic)] = False

    
    if((prediction_arrays[str(message.topic)].size/4) <= 9):
    	if(json_object["ENERGY"]["Power"] != 0):
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
        print("executing block two of classification (making the prediction)")
        prediction_arrays[str(message.topic)] = prediction_arrays[str(message.topic)].reshape((1,40))
        # scale/normalize the values in the array
        transformed_array = classification_scaler.transform(prediction_arrays[str(message.topic)]) # copy to not change the original array
        # make a prediction
        pred_test = classification_model.predict(transformed_array)
        print(pred_test)
        # get the index of the highest prediction
        device = np.argmax(pred_test)
        print(device)
        # get the class name
        print("predicted device: ",CLASSES[device])
        # for the demo there are only two devices thus we dont use the index to determine the device
        
        # if(CLASSES[class_index] == "box" and args.device == "box"):
        #     device = 1
        # elif(CLASSES[class_index] == "laptop" and args.device == "laptop"):
        #     device = 0
        # else:
        #     print("incorrect device predicted stopping execution")
        if(str(CLASSES[device]) != str(args.device)):
            print("!!! an incorrect device has been predicted !!!")
            print(CLASSES[device], "VS", args.device)
	   # client.disconnect()
	    #exit()
        print(device)
        # send the result of the prediction back to the topic
        client.publish(message.topic + "/prediction",CLASSES[device]) 
        # if(once == True):
        prediction_state[str(message.topic)] = True

    # ------------ prediction ---------------

    # Second part is to make the prediction 
    elif (normal_usage.size == 10):
        extracted_value = mqtt_prediction.extract_object(json_object, states) # Extracting the values from the json object
        print("These are the extracted values: ", extracted_value)

        # Create the history array and determine the state
        if (status_counter == 0):
            states = mqtt_prediction.state_determination(normal_usage)
            print("This is the normal usage power: ", states)
            if(CLASSES[device] == "box" or CLASSES[device] == "phone"):
                print("turning of box/phone cause off in history")
                client.publish(message.topic + "/usagePrediction", "off")
            # print("The last message added to the history: ", json_object)
            global history_dataset
            history_dataset = mqtt_prediction.history_creation(df_history) # Creating our own history (one week)
            influx_history(flux_client, history_dataset)
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
            scaled_history = mqtt_prediction.scaled_history(scaled_history, scaler,device) # Scale the history
            # print(scaled_history)
            global scaled_history_array
            scaled_history_array = np.array(scaled_history) # Change the history dataset to a numpy array
            new_row = {'timestamp': latest_time, 'state': extracted_value}
            new_row_df = pd.DataFrame([new_row])
            history_dataset = pd.concat([history_dataset,new_row_df],ignore_index=True)
            #history_dataset = history_dataset.append(new_row, ignore_index=True) # Add the latest time and state (+4min) to the original history
            history_dataset = history_dataset.drop(0) # Drop the first row from the original dataset
            print("THIS IS THE NEW HISTORY DATASET: ", history_dataset)
            month = latest_time.month
            hour = latest_time.hour # extract the features of the latest time
            minute = latest_time.minute
            day_of_week = latest_time.weekday()
            global latest_value
            # print("The new last message added to the history: ", json_object)
            print("This is the oldest mqtt message: ", latest_value) 
            if ((latest_value.size)/5 < 1): 
                latest_value = np.append(latest_value, [extracted_value, hour, minute, day_of_week, device]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            else:
                latest_value = np.delete(latest_value, [0,1,2,3,4]) # Delete the latest values first to get an empty numpy array
                latest_value = np.append(latest_value, [extracted_value, hour, minute, day_of_week, device]) # Add the latest values from MQTT to a numpy array
                latest_value = mqtt_prediction.scale_mqtt_message(latest_value, scaler)
            print("This is the latest mqtt message: ", latest_value)
            scaled_history_array = np.vstack((scaled_history_array, latest_value)) # Add the latest value from MQTT to the history array
            scaled_history_array = np.delete(scaled_history_array, 0, axis=0) # Remove the first value from the history array
            prediction_array = scaled_history_array.reshape((1,2520,5)) # Reshape for the prediction
            print(prediction_array)
            pred = model.predict(prediction_array) # The prediction
            print("The prediction of the next state: ", pred)

            # Some code to change the plug state
            if(pred > 0.5):
                client.publish(message.topic + "/usagePrediction", "on")
            elif(pred < 0.5 and json_object["ENERGY"]["Power"] < states): 
                client.publish(message.topic + "/usagePrediction", "off")
            #print(history_dataset['state'].iloc[0])
            client.publish(message.topic + "/latest", "latest prediction = " + str(pred[0][0]) + " | value one week ago/expected = " + str(history_dataset['state'].iloc[0])) #+ " ,hour = " + str(hour) + " ,minute = " + str(minute) + " ,day of the week = " + days_of_week[day_of_week] + ", month = " + months_of_year[month])
            message_counter = 0

        status_counter = status_counter + 1 # This is to go to the next if statement
        message_counter += 1
        # last_change += 1
        print("message counter is now: ", message_counter)

flux_client = InfluxDBClient(host= influxip, port=8086, username=influx_user,password=influx_pw)
print(flux_client.get_list_database())
flux_client.switch_database('plug_database')

Connected = False   # global variable for the state of the connection
  
broker_address = broker
port = 1883  #Broker port

client = mqttClient.Client(args.mqttclient)         #create new instance
client.username_pw_set('vives', password=mqtt_pw)  #set username and password if required
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

#user_input = input("Press enter to calculate the state for nomal usage")
user_input = input("Please enter what plug you would like to use (1 or 2)")

while(user_input != "1" and user_input != "2"):
    print("please enter a valid plug your last input was: ", user_input)
    user_input = input("Please enter what plug you would like to use (1 or 2)")

client.loop_start() #start the loop

if (True): # When the user presses enter, it will subscribe to the topic
    if(user_input == "1"): # all devices that should be off by default
        client.subscribe("ai-stopcontact/tele/opstelling_plug1/SENSOR")
        print("subscribed to plug 1")
        client.publish("ai-stopcontact/tele/opstelling_plug1/SENSOR/usagePrediction", "on")
    elif(user_input == "2"):
        client.subscribe("ai-stopcontact/tele/opstelling_plug2/SENSOR")
        print("subscribed to plug 2")
        client.publish("ai-stopcontact/tele/opstelling_plug2/SENSOR/usagePrediction", "on")

while Connected != True: #Wait for connection
    time.sleep(0.1)

try:
    while True:
        time.sleep(1)
  
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
