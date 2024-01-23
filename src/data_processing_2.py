import pandas as pd
import numpy as np
import os
import csv



R6  = "R6"
R11 = "R11"

def read_data_files(data_dir="R6"):
    '''Function that reads the csv files and converts them
       to a df with the pose and time columns'''
    all_sensors = []
    base_dir = "data/"
    for dir in os.listdir(base_dir):
            if dir.startswith(data_dir):
                path = base_dir + dir
                for filename in os.listdir(path):
                    if filename.endswith(".csv"):
                        filepath = os.path.join(path, filename)
                        with open(filepath, "r") as file:
                            df = pd.read_csv(filepath)
                            if "pose.pose.position.x" in list(df.columns):
                                all_sensors.append(df[["header.stamp.secs", "header.stamp.nsecs","pose.pose.position.x", "pose.pose.position.y", "pose.pose.position.z"]])
                return all_sensors
            
def substraction(a:float, b:float, std:float):
    if abs(a-b) >= std:
        return False
    return True

df_list = read_data_files("R6")
print(df_list[1].head(5))
std = df_list[1].std()
std["pose.pose.position.x"]

#First sensor
df1 = df_list[1]
std = df1.std() #Calculate the standar deviation of each column
difference = df1.diff() #Substraction
comp = difference.gt(std) #Compare the value
print(comp)
     