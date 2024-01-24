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
LIST_FILES = ['cerbere_steering_controller-odom.csv','imu7-data.csv','odom-hdl.csv','odometry-ekf_se_odom.csv','odometry-filtered_map.csv','odometry-gps.csv']  #  WE DONT CARE ABOUT ublox_node-fix.csv
# enum the list of files
CERBERE, IMU7, ODOM_HDL, ODOMETRY_EKF, ODOMETRY_FILTERED, ODOMETRY_GPS = list(LIST_FILES)
# enum the args of the list of files
TIMESTAMP_S, TIMESTAMP_NS, POS_X, POS_Y, POS_Z, ANGULAR_VELOCITY_X, ANGULAR_VELOCITY_Y, ANGULAR_VELOCITY_Z, LINEAR_VELOCITY_X, LINEAR_VELOCITY_Y, LINEAR_VELOCITY_Z, LINEAR_ACC_X, LINEAR_ACC_Y, LINEAR_ACC_Z = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
####################################################################

def read_data_files(data_dir):
    data = {}
    base_dir = "data/"
    for dir in os.listdir(base_dir):
            if dir.startswith(data_dir):
                path = os.path.join(base_dir, dir)
                for filename in os.listdir(path):
                    if filename.endswith(".csv") and filename in LIST_FILES:
                        filepath = os.path.join(path, filename)
                        with open(filepath, "r") as file:
                            reader = csv.DictReader(file)
                            positions = []
                            for row in reader:
                                posx, posy, posz, angvx, angvy, angvz, linvx, linvy, linvz, linax, linay, linaz = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0
                                if row.__contains__("pose.pose.position.x"):
                                    posx, posy, posz = float(row["pose.pose.position.x"]), float(row["pose.pose.position.y"]), float(row["pose.pose.position.z"])
                                if row.__contains__("angular_velocity.x"):
                                    angvx, angvy, angvz = float(row["angular_velocity.x"]), float(row["angular_velocity.y"]), float(row["angular_velocity.z"])
                                if row.__contains__("twist.twist.angular.x"):
                                    angvx, angvy, angvz = float(row["twist.twist.angular.x"]), float(row["twist.twist.angular.y"]), float(row["twist.twist.angular.x"])
                                if row.__contains__("twist.twist.linear.x"):
                                    linvx, linvy, linvz = float(row["twist.twist.linear.x"]), float(row["twist.twist.linear.y"]), float(row["twist.twist.linear.x"])
                                if row.__contains__("linear_acceleration.x"):
                                    linax, linay, linaz = float(row["linear_acceleration.x"]), float(row["linear_acceleration.y"]), float(row["linear_acceleration.z"])
                                positions.append(np.array([float(row["header.stamp.secs"]),float(row["header.stamp.nsecs"]), posx, posy, posz, angvx, angvy, angvz, linvx, linvy, linvz, linax, linay, linaz]))
                            data[filename] = positions
    return data

def plot_data(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for file in data.keys():
        x = [line[POS_X] for line in data[file]]
        y = [line[POS_Y] for line in data[file]]
        z = [line[POS_Z] for line in data[file]]
        ax.plot(x, y, z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
    return

#Calculate the standar deviation of each column
def mean_standard_deviation(data, filename):
    mean = np.mean(data[filename], axis=0)
    std = np.std(data[filename], axis=0)
    return mean, std

# for each file in data, calculate the length and take the max length
def compute_max_length(data):
    max_len = 0
    file_max_len = ""
    for file in data.keys():
        if len(data[file]) > max_len:
            max_len = len(data[file])
            file_max_len = file
    return file_max_len,max_len

def interpolate_data(data):
    interpolated_data = deepcopy(data)
    file_max_length, max_length = compute_max_length(data)
    for file in data.keys():
        if len(data[file]) == max_length:
            interpolated_data_file.append(data[file])
        else:
            timestamps = deepcopy([line[TIMESTAMP_S] + line[TIMESTAMP_NS]*0.1**(len(str(line[TIMESTAMP_NS]))) for line in data[file]])
            new_timestamps = deepcopy([line[TIMESTAMP_S] + line[TIMESTAMP_NS]*0.1**(len(str(line[TIMESTAMP_NS]))) for line in data[file_max_length]])
            interpolated_data_file = [[line[TIMESTAMP_S] for line in data[file_max_length]], [line[TIMESTAMP_NS] for line in data[file_max_length]]]
            for i in range(POS_X, LINEAR_ACC_Z + 1):
                interp = np.interp(new_timestamps, timestamps, [line[i] for line in data[file]])
                interpolated_data_file.append(interp)
            interpolated_data[file] = np.array(interpolated_data_file).T
    return interpolated_data

def check_interpolation(data):
    print("Checking interpolation ...")
    file_max_length, max_length = compute_max_length(data)
    ok_counter = 0
    for file in data.keys():
        if len(data[file]) != max_length or len(data[file][0]) != LINEAR_ACC_Z+1:
            print("ERROR")
            print(file, len(data[file]), "should be", max_length)
            print(file, len(data[file][0]), "should be", 11)
        else:
            ok_counter += 1
        if ok_counter == len(data.keys()):
            print("OK")
    return

def filter_data(data):
    filtered_data = deepcopy(data)
    std_derivative, mean = {}, {}
    for file in data.keys():
        to_delete =[]
        for i in range(ANGULAR_VELOCITY_X, LINEAR_ACC_Z + 1):
            mean[file], std_derivative[file] = mean_standard_deviation(data, file)
            for j in range(1, len(data[file])):
                if (data[file][j][i] > (mean[file][i] + std_derivative[file][i])) or (data[file][j][i] < (mean[file][i] - std_derivative[file][i])):
                    to_delete.append(j)
        filtered_data[file] = np.delete(filtered_data[file], to_delete, 0)
    return filtered_data

def check_filtering(data):
    print("Checking filtering ...")
    for file in filtered_data_.keys():
        print("filename :", file, "filelen :", len(filtered_data_[file]))
    print("OK")
    return

if __name__ == "__main__":
    data_ = read_data_files(DATA_DIRECTORY)
    interpolated_data_ = interpolate_data(data_)
    check_interpolation(interpolated_data_)
    # plot_data(data_)
    # plot_data(interpolated_data_)
    filtered_data_ = filter_data(interpolated_data_)
    for file in filtered_data_.keys():
        print(file, len(filtered_data_[file]))
    # plot_data(interpolated_data_)
    plot_data(filtered_data_)