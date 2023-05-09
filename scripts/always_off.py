import pandas as pd
import datetime
import json
import numpy as np
# import matplotlib.pyplot as plt
import paho.mqtt.publish as publish

df = pd.read_csv(r'../csv_files/17-04/tv_jarno_with0.csv', parse_dates=['time'])
df = df.dropna()

# add column for state
df['state'] = np.where(df['Power'] > 40, 1, 0)
df.head()

df.set_index('time', inplace=True)
df_hourly = df.resample('15T').ffill()
df_hourly.head()

df_hourly = df_hourly.dropna()
df_hourly = df_hourly.drop(columns=['Power'])
# df = df.drop(columns=['timestamp'])
df_hourly.describe()
# print(df)

grouped = df['state'].groupby(df.index.hour)
proportions = grouped.mean()
print(grouped)
print(proportions)

# Identify the hours where the device is off all the time
always_on_hours = proportions[proportions > 0].index
print(always_on_hours)
always_on_hours = always_on_hours.values
print(always_on_hours)
always_on_hours = always_on_hours.tolist()

# Convert the array to a JSON string
array_str = json.dumps(always_on_hours)

# # Publish the array string to an MQTT topic
# publish.single("ai-stopcontact/plugs/test", payload=array_str, hostname="mqtt.devbit.be")

# print("The device is always off during these hours:", always_on_hours)