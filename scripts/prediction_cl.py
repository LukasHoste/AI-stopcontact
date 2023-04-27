import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

class MqttPrediction:

  # Method that returns the minimum power from the usage array and also calculates the maximum power from the no_usage array
  def state_determination(self, normal_usage):
    normal_usage_min = 0
    normal_usage_min = np.amin(normal_usage)
    return normal_usage_min
  
  # Method which extracts the timestamp from a json object and determines if the power is state -> 1 or if it is state -> 0
  def extract_object(self, json_object, normal_usage_min):
      # Take the timestamp and split it into hour, minute, day_of_the_month, day_of_the_week, month
      time_stamp = json_object["Time"]
      time_stamp = pd.to_datetime(time_stamp, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format
      hour = time_stamp.hour    
      minute = time_stamp.minute
      # day_of_month = time_stamp.day
      # print(day_of_month)
      day_of_week = time_stamp.weekday()
      month = time_stamp.month
      power = json_object["ENERGY"]["Power"]
      # Convert the power to the state
      if (power >= normal_usage_min):
          state = 1
      if (power < normal_usage_min):
          state = 0
      return state, hour, minute, day_of_week, month

  # Method which creates our own history with normalization
  def history_creation(self, json_object, df_history, scaler, device):
      mqtt_last_time = json_object["Time"]
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
      df_history['hour'] = df_history.index.hour
      df_history['minute'] = df_history.index.minute
      # df_history['day_of_month'] = df_history.index.day
      df_history['day_of_week'] = df_history.index.dayofweek
      df_history['month'] = df_history.index.month
      df_history['device'] = 1

      print(df_history)
      # Normalize the history
      # When the scaling is done with sigmoid, then you need to uncomment the line below
      # df_history[['state','hour','minute','day_of_week','month']] = scaler.transform(df_history[['state','hour','minute','day_of_week','month']])

      # When the scaling is done with tanh, then you need to uncomment the line below
      df_history[['hour','minute','day_of_week','month','device']] = scaler.transform(df_history[['hour','minute','day_of_week','month','device']])
      print(df_history)

      df_with_timestamp = df_history
      # Append the data to a numpy array
      df_history = df_history.drop(columns=['timestamp'])
      df_history.dropna()
      return df_history, df_with_timestamp

  # Method that scales our latest message from the MQTT
  def scale_mqtt_message(self, latest_value, scaler):
      # reshape for normalization
      latest_value = latest_value.reshape(1,-1)
      # When the scaling is done with sigmoid, then you need to uncomment the line below
      # latest_value= scaler.transform(latest_value)
                  
      # When the scaling is done with tanh, then you need to uncomment the lines below
      # print(latest_value)
      # print(latest_value[0,1:5])
      latest_value[0,1:6] = scaler.transform(latest_value[0,1:6].reshape(1,-1))
      latest_value = latest_value.reshape(-1)
      return latest_value
