import pandas as pd
import os
import csv



R6  = "R6"
R11 = "R11"

def read_data_files(data_dir="R6"):
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

df = read_data_files("R6")
print(df[1].head(5))