import paho.mqtt.client as mqttClient #pip install paho-mqtt
import time
import numpy as np
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

CLASSES=['laptop', 'phone_charging', 'school_box', 'school_pc', 'school_printer']

numpy_array = np.zeros(shape=(1,50))
i = 0

def on_message(client, userdata, message):
    global i
    global numpy_array
    bytes_array = message.payload
    data = literal_eval(bytes_array.decode('utf8'))
    json_string = json.dumps(data, indent=4,sort_keys=True)
    json_object = json.loads(json_string)
    print(message.payload)
    # print(json_object["ENERGY"]["Current"])
    if(i < 10):
        print(i)
        numpy_array[0][i] = json_object["ENERGY"]["ApparentPower"]
        numpy_array[0][i+1] = json_object["ENERGY"]["Current"]
        numpy_array[0][i+2] = json_object["ENERGY"]["Factor"]
        numpy_array[0][i+3] = json_object["ENERGY"]["Power"]
        numpy_array[0][i+4] = json_object["ENERGY"]["ReactivePower"]
        i = i+1
    if (i == 10):
        pred_test = model.predict(numpy_array)
        print(pred_test)
        class_index = np.argmax(pred_test)
        print(class_index)
        print(CLASSES[class_index])
        i = 0
        numpy_array = np.zeros(shape=(1,50))
    # numpy_array[0][0] = json_object["ENERGY"]["ApparentPower"]
    # numpy_array[0][1] = json_object["ENERGY"]["Current"]
    # numpy_array[0][2] = json_object["ENERGY"]["Factor"]
    # numpy_array[0][3] = json_object["ENERGY"]["Power"]
    # numpy_array[0][4] = json_object["ENERGY"]["ReactivePower"]
    # print(numpy_array)
    # pred_test = model.predict(numpy_array)
    # print(pred_test)
    # class_index = np.argmax(pred_test)
    # print(class_index)
    # print(CLASSES[class_index])



model = keras.models.load_model('../models/model_multiple_samples/model_saved')

Connected = False   #global variable for the state of the connection
  
broker_address= "10.15.51.63"  #Broker address
port = 1883  #Broker port
user = "VIVESStopContact"                    #Connection username
password = "stop123"            #Connection password
  
client = mqttClient.Client("Python")               #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

client.loop_start() #start the loop
  
while Connected != True:    #Wait for connection
    time.sleep(0.1)
  
client.subscribe("tele/tasmota_B4D6BC/SENSOR")



try:
    while True:
        time.sleep(1)
  
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()