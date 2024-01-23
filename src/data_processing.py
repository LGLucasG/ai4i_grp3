import os
import csv
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
R6  = "R6_2024_01_04_05_47_05_patrouille_TAC_dechetterie_clean"
R11 = "R11_2024_01_04_07_58_48_parc_check_clean"

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
                                    positions.append([float(row["pose.pose.position.x"]), float(row["pose.pose.position.y"]), float(row["pose.pose.position.z"])])
                            all_positions.append(positions)
    return all_positions

# Plot positions in 3D
positions = read_data_files("R6")
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for pos in positions:
    x = [p[0] for p in pos]
    y = [p[1] for p in pos]
    z = [p[2] for p in pos]
    ax.plot(x, y, z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

