import os
import csv
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

#### MODIFY HERE ####
# Choose the data directory
DATA_DIRECTORY = "R6"  ## "R6" or "R11"
######################


#### DO NOT MODIFY IF YOU ARE NOT SURE ABOUT WHAT YOU ARE DOING ####
# List of files
LIST_FILES = ['CERBERE_steering_controller-odom.csv','IMU7-data.csv','odom-hdl.csv','odometry-ekf_se_odom.csv','odometry-filtered_map.csv','odometry-gps.csv']  #  WE DONT CARE ABOUT ublox_node-fix.csv
# enum the list of files
CERBERE, IMU7, ODOM_HDL, ODOMETRY_EKF, ODOMETRY_FILTERED, ODOMETRY_GPS = list(LIST_FILES)
# enum the args of the list of files
TIMESTAMP_S, TIMESTAMP_NS, X_POS, Y_POS, Z_POS, X_ANGULAR_VELOCITY, Y_ANGULAR_VELOCITY, Z_ANGULAR_VELOCITY, X_LINEAR_ACC, Y_LINEAR_ACC, Z_LINEAR_ACC = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
####################################################################

def read_data_files(data_dir):
    data = {}
    base_dir = "data/"
    for dir in os.listdir(base_dir):
            if dir.startswith(data_dir):
                path = os.path.join(base_dir, dir)
                for filename in os.listdir(path):
                    if filename.endswith(".csv"):
                        filepath = os.path.join(path, filename)
                        with open(filepath, "r") as file:
                            reader = csv.DictReader(file)
                            positions = []
                            for row in reader:
                                posx, posy, posz, angx, angy, angz, linx, liny, linz = 0, 0, 0, 0, 0, 0, 0, 0, 0
                                if row.__contains__("pose.pose.position.x"):
                                    posx, posy, posz = float(row["pose.pose.position.x"]), float(row["pose.pose.position.y"]), float(row["pose.pose.position.z"])
                                if row.__contains__("angular_velocity.x"):
                                    angx, angy, angz = float(row["angular_velocity.x"]), float(row["angular_velocity.y"]), float(row["angular_velocity.z"])
                                if row.__contains__("linear_acceleration.x"):
                                    linx, liny, linz = float(row["linear_acceleration.x"]), float(row["linear_acceleration.y"]), float(row["linear_acceleration.z"])
                                positions.append(np.array([float(row["header.stamp.secs"]),float(row["header.stamp.nsecs"]), posx, posy, posz, angx, angy, angz, linx, liny, linz]))
                            data[filename] = positions
    return data

def plot_data(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for file in data.keys():
        x = [line[X_POS] for line in data[file]]
        y = [line[Y_POS] for line in data[file]]
        z = [line[Z_POS] for line in data[file]]
        ax.plot(x, y, z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

data_ = read_data_files(DATA_DIRECTORY)

# plot_data(data_)

#Calculate the standar deviation of each column
def standar_deviation(data, filename):
    std = np.std(data[filename], axis=0)
    return std

# for each file in data, calculate the length and take the max length
def max_length(data):
    max_len = 0
    file_max_len = ""
    for file in data.keys():
        if len(data[file]) > max_len:
            max_len = len(data[file])
            file_max_len = file
    return file_max_len,max_len

file_max_length_, max_length_ = max_length(data_)

timestamp_length_ = 10

def interpolate_data(data_):
    interpolated_data = deepcopy(data_)
    for file in data_.keys():
        timestamps = deepcopy([line[TIMESTAMP_S]*10 + line[TIMESTAMP_NS] for line in data_[file]])
        new_timestamps = deepcopy([line[TIMESTAMP_S]*10 + line[TIMESTAMP_NS] for line in data_[file_max_length_]])
        values = deepcopy([line[X_POS] for line in data_[file]])
        interpolated_data_file = [[line[TIMESTAMP_S] for line in data_[file_max_length_]], [line[TIMESTAMP_NS] for line in data_[file_max_length_]]]
        for i in range(X_POS, Z_LINEAR_ACC + 1):
            interp = np.interp(new_timestamps, timestamps, [line[i] for line in data_[file]])
            interpolated_data_file.append(interp)
        interpolated_data[file] = np.array(interpolated_data_file).T
    return interpolated_data

interpolated_data_ = interpolate_data(data_)

def check_interpolation(data_):
    print("Checking interpolation ...")
    ok_counter = 0
    for file in data_.keys():
        if len(data_[file]) != max_length_ or len(data_[file][0]) != 11:
            print("ERROR")
            print(file, len(data_[file]), "should be", max_length_)
            print(file, len(data_[file][0]), "should be", 11)
        else:
            ok_counter += 1
        if ok_counter == len(data_.keys()):
            print("OK")
    return

check_interpolation(interpolated_data_)