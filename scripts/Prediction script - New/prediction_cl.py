import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta, time

class MqttPrediction:

  # Method that returns the minimum power from the usage array and also calculates the maximum power from the no_usage array
  def state_determination(self, normal_usage):
    normal_usage_min = 0
    normal_usage_min = np.amin(normal_usage)
    return normal_usage_min
  
  # Method which extracts the timestamp from a json object and determines if the power is state -> 1 or if it is state -> 0
  def extract_object(self, json_object, normal_usage_min):
      # Take the power from the last json_object
      power = json_object["ENERGY"]["Power"]
      # Convert the power to the state
      if (power >= normal_usage_min):
          state = 1
      if (power < normal_usage_min):
          state = 0
      return state

  # Method which creates our own history with normalization
  def history_creation(self, df_history):
      # mqtt_last_time = json_object["Time"]
      # mqtt_last_time = pd.to_datetime(mqtt_last_time, format='%Y.%m.%d %H:%M:%S') #The timestamp in a format

      specific_time = time(23,56,0)
      date = datetime(2023, 2, 5)
      fake_data_start_time = datetime.combine(date,specific_time) # Date starts on a monday
      # # Compute the timestamp one week before the last received time from MQTT
      fake_data_last_time = fake_data_start_time + pd.Timedelta(days=7)

      # Create a new timestamp sequence starting from fake_data_start_time and ending with mqtt_last_time, with a 4-minute increment
      new_timestamps = pd.date_range(start=fake_data_start_time, end=fake_data_last_time, freq='4T')

      # # Slice the new timestamp sequence to the same length as the original fake data
      new_timestamps = new_timestamps[-len(df_history):]

      # # Replace the timestamps in the fake data with the new timestamps
      df_history['timestamp'] = new_timestamps

      return df_history
  
  def scaled_history(self, history_dataset, scaler, device):
    # Get it in the right shape for numpy array
    scaled_history = history_dataset
    scaled_history.index = pd.to_datetime(scaled_history['timestamp'], format='%d.%m.%Y %H:%M:%S')
    scaled_history['hour'] = scaled_history.index.hour
    scaled_history['minute'] = scaled_history.index.minute
    # df_history['day_of_month'] = df_history.index.day
    scaled_history['day_of_week'] = scaled_history.index.dayofweek
    # df_history['month'] = df_history.index.month
    scaled_history['device'] = device
    # Normalize the history
    # When the scaling is done with sigmoid, then you need to uncomment the line below
    # df_history[['state','hour','minute','day_of_week','month']] = scaler.transform(df_history[['state','hour','minute','day_of_week','month']])

    # When the scaling is done with tanh, then you need to uncomment the line below
    # df_history[['hour','minute','day_of_week','month','device']] = scaler.transform(df_history[['hour','minute','day_of_week','month','device']])
    scaled_history[['hour','minute','day_of_week','device']] = scaler.transform(scaled_history[['hour','minute','day_of_week','device']])

    # Append the data to a numpy array
    scaled_history = scaled_history.drop(columns=['timestamp'])
    scaled_history.dropna()

    return scaled_history
  
  # Method that scales our latest message from the MQTT
  def scale_mqtt_message(self, latest_value, scaler):
      # reshape for normalization
      latest_value = latest_value.reshape(1,-1)
      # When the scaling is done with sigmoid, then you need to uncomment the line below
      # latest_value= scaler.transform(latest_value)
                  
      # When the scaling is done with tanh, then you need to uncomment the lines below
      # print(latest_value)
      # print(latest_value[0,1:5])
      # latest_value[0,1:6] = scaler.transform(latest_value[0,1:6].reshape(1,-1)) # This is when the month is still a feature
      latest_value[0,1:5] = scaler.transform(latest_value[0,1:5].reshape(1,-1))
      latest_value = latest_value.reshape(-1)
      return latest_value
