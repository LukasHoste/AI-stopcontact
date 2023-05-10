import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
import json
from ast import literal_eval
import tensorflow as tf
from tensorflow import keras
import joblib
import sys

once = sys.argv[1]
if(once == "True"):
    once = True
else:
    once = False


scaler = joblib.load('scaler_classification.gz') # load the scaler, fitted during training
  
# function that determines what to do when connection to a broker is made
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
        client.subscribe("ai-stopcontact/plugs/tele/+/SENSOR") # subscribe to all topics that are subtopics of ai-stopcontact/plugs and have a subtopic SENSOR
    else:
      print("Connection failed")

CLASSES=['box', 'laptop', 'monitor', 'pc', 'phone', 'printer','switch','tv'] # list of all the classes, this has to be in the same order as during training

prediction_arrays = {} # dictionary for all the arrays that contain the data to make a prediction
prediction_state = {}

# how to handle a received message from the broker
def on_message(client, userdata, message):
    print(message.topic) # print of what topic the received message comes from
    # if the topic is not yet in the dictionary, add the topic name as a key to the dictionary and fill it with an empty array
    if(not str(message.topic) in prediction_arrays):
        print("adding topic key to the dictionary :)")
        prediction_arrays[str(message.topic)] = np.zeros(shape=(1,0))
        print("adding key to check if a prediction has already been made")
        prediction_state[str(message.topic)] = False

    # convert the received data to a json_object
    bytes_array = message.payload.decode('utf8')
    json_object = json.loads(bytes_array)
    print(json_object)

    # as long ass the array does not reach its maximum value ((array size)/(number of parameters) <= (maximum size/number of parameters)-1)
    # , just add the new values
    if((prediction_arrays[str(message.topic)].size/4) <= 29):
        print(prediction_arrays[str(message.topic)].size)
        prediction_arrays[str(message.topic)] = np.append(prediction_arrays[str(message.topic)],[json_object["ENERGY"]["ApparentPower"],
        json_object["ENERGY"]["Current"],
        # json_object["ENERGY"]["Factor"],
        json_object["ENERGY"]["Power"],
        json_object["ENERGY"]["ReactivePower"]
        ])
        print(prediction_arrays[str(message.topic)]) # print the current prediction array
    # append new values and make a prediction
    elif(not (prediction_state[str(message.topic)])):
        # add latest values
        prediction_arrays[str(message.topic)] = np.append(prediction_arrays[str(message.topic)]
        ,[json_object["ENERGY"]["ApparentPower"],
        json_object["ENERGY"]["Current"],
        # json_object["ENERGY"]["Factor"],
        json_object["ENERGY"]["Power"],
        json_object["ENERGY"]["ReactivePower"]
        ])
        # remove oldest values
        prediction_arrays[str(message.topic)] = np.delete(prediction_arrays[str(message.topic)],[0,1,2,3])
        # reshape the array for prediction
        prediction_arrays[str(message.topic)] = prediction_arrays[str(message.topic)].reshape((1,120))
        # scale/normalize the values in the array
        transformed_array = scaler.transform(prediction_arrays[str(message.topic)]) # copy to not change the original array
        # make a prediction
        pred_test = model.predict(transformed_array)
        print(pred_test)
        # get the index of the highest prediction
        class_index = np.argmax(pred_test)
        print(class_index)
        # get the class name
        print(CLASSES[class_index])
        print(pred_test)
        # send the result of the prediction back to the topic
        client.publish(message.topic + "/prediction",CLASSES[class_index]) 
        if(once == True):
            print(once)
            print("this topic should only be done once")
            prediction_state[str(message.topic)] = True

model = keras.models.load_model('../models/classification_10-05') # loads the model

Connected = False   #global variable for the state of the connection
  
broker_address= "mqtt.devbit.be"  #Broker address
port = 1883  #Broker port
user = "VIVESStopContact"   #Connection username
password = "stop123"    #Connection password
  
client = mqttClient.Client("classification")    #create new instance
client.username_pw_set(user, password=password) #set username and password
client.on_connect= on_connect   #attach function to callback
client.on_message= on_message   #attach function to callback

client.connect(broker_address, port=port)   #connect to broker

client.loop_start() #start the loop
  
while Connected != True: #Wait for connection
    time.sleep(0.1)

try:
    while True:
        time.sleep(1)
  
# stop mqtt loop on keyboardinterrupt
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()