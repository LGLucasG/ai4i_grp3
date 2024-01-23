import os
import csv


R6  = "R6_2024_01_04_05_47_05_patrouille_TAC_dechetterie_clean"
R11 = "R11_2024_01_04_07_58_48_parc_check_clean"

def read_data_files(data_dir="R6"):
    all_positions = []
    base_dir = "data/"
    for dir in os.listdir(base_dir):
            if dir.startswith(data_dir):
                path = base_dir + dir
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

print(read_data_files())