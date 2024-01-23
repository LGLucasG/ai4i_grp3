import os
import csv
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

dtype = [('s', 'int64'), ('ns', 'int64'), ('x', 'float64'), ('y', 'float64'), ('z', 'float64')]



def read_data_files(data_dir):
    all_positions = []

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
                                if row.__contains__("pose.pose.position.x"):
                                    positions = np.array([float(row["header.stamp.secs"]),float(row["header.stamp.nsecs"]),float(row["pose.pose.position.x"]), float(row["pose.pose.position.y"]), float(row["pose.pose.position.z"])], dtype=dtype)
                                all_positions.append(positions)
    return cerbere, imu7, odom_hdl

print(read_data_files("R6"))

# positions = read_data_files("R6")
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# for pos in positions:
#     x = [p[0] for p in pos]
#     y = [p[1] for p in pos]
#     z = [p[2] for p in pos]
#     ax.plot(x, y, z)
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')
# plt.show()

