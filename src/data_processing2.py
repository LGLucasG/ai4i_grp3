import pandas as pd
import os

def read_data_files(data_dir:str="R6", base_dir:str="../../data/"):
    """
    Function that reads the csv files and converts them to list of df with the pose and time columns.

    Args:
        data_dir (str, optional): Name of the folder you want to take the data from (Defaults to "R6")
        base_dir_before (str): The base path where the csv will be taken for (Default to "../../data/")

    Returns:
        all_sensors (list): List of all the dataframes obtained from the files
        name (list): List of the names of the data file contained in each df
    """  
    all_sensors = []
    name = []
    for dir in os.listdir(base_dir):
        if dir.startswith(data_dir):
            path = base_dir + dir
            for i,filename in enumerate(os.listdir(path)):
                if filename.endswith(".csv"):
                    filepath = os.path.join(path, filename)
                    with open(filepath, "r") as file:
                        df = pd.read_csv(filepath)
                        df["time"] = df["header.stamp.secs"] + df["header.stamp.nsecs"]/1e9
                        if i==0:
                            min = df.loc[0, "time"]
                        elif df.loc[0, "time"] < min:
                            min = df.loc[0, "time"]
                        if "child_frame_id" in list(df.columns):
                            df = df.drop(["child_frame_id"], axis=1)
                        df = df.drop(["Time", "header.seq", "header.frame_id", "header.stamp.secs", "header.stamp.nsecs"],axis=1)
                        df = df.drop(columns=df.select_dtypes(exclude=["float64"]).columns) #Drop no-numeric columns
                        df = df.loc[:, (df != 0).any(axis=0)]
                        all_sensors.append(df.rename(columns=lambda x: str(i) + "_" + x if x!="time" else x))
                        name.append(filename)
    # Normalize the time (to start from 0)
    for j in all_sensors:
        j["time"] = j["time"].sub(min)
    return all_sensors, name


def join_data(df_list:list, name_list:list):
    """
    Function that takes all the DataFrames and joins them in one DataFrame.

    Args:
        df_list (list): List of the DataFrames you want to join
        name_list (list): List of the names of the DataFrames you want to join

    Returns:
        df_entrada (DataFrame): All the DataFrames joined in one
    """
    df_entrada = df_list[0]
    for i, df_dentro in enumerate(df_list):
        if i != (name_list.index("odometry-filtered_map.csv") or 0):
            df_entrada = pd.merge(left=df_entrada,right=df_dentro, how='outer', on='time')
    df_entrada = df_entrada.set_index(keys="time").sort_index(ascending=True)
    return df_entrada


def do_interpolation(df_entrada:pd.DataFrame, df_list:list, name_list:list, base_dir:str="../../data/", method_type:str="before", data_dir:str="R6"):
    """
    Function that interpolates a DataFrame.

    Args:
        df_entrada (pd.DataFrame): All the DataFrames joined in one
        df_list (list): List of the DataFrames you want to join
        name_list (list): List of the names of the DataFrames you want to join
        base_dir (str): The base path where the csv will be left (Default to "../../data/")
        method_type (str, optional): Method that will be used to do the interpolation (Defaults to "before")
        data_dir (str, optional): Name of the folder you want to take the data from (Defaults to "R6")

    Returns:
        df (DataFrame): Dataframe with the interpolation done
    """
    if method_type == "before":
        df = df_entrada.ffill().dropna()
        df = pd.merge(df.reset_index(), df_list[name_list.index('odom-hdl.csv')].reset_index()["time"], how="right", on="time").set_index("time").dropna()
        full_path = base_dir + data_dir + "_input_before.csv"
        df.to_csv(full_path)
    else:
        df = df_entrada.interpolate(method="values").dropna()
        df = pd.merge(df.reset_index(), df_list[name_list.index('odom-hdl.csv')].reset_index()["time"], how="right", on="time").set_index("time").dropna()
        df.to_csv(data_dir + "_input_interpolacion.csv")
    return df

def process(base_dir_before:str="../../data/", base_dir_after:str="../../data/", method_type:str="before", data_dir:str="R6"):
    """
    Function that calls subfunctions to read, join and interpolate data.

    Args:
        base_dir_before (str): The base path where the csv will be taken for (Default to "../../data/")
        base_dir_after (str): The base path where the csv will be left (Default to "../../data/")
        method_type (str, optional): Method that will be used to do the interpolation (Defaults to "before")
        data_dir (str, optional): Name of the folder you want to take the data from (Defaults to "R6")
    """
    df_list, name_list = read_data_files(data_dir, base_dir_before)
    df_entrada = join_data(df_list, name_list)
    do_interpolation(df_entrada, df_list, name_list, base_dir_after, method_type, data_dir)
    df_salida = pd.merge(df_entrada.reset_index()["time"], df_list[2], how='outer', on='time')
    df_salida = df_salida.set_index("time").sort_index(ascending=True).interpolate(method="values")
    #Delete the lines that are not in the input so that the input and output length are equal
    df_salida = pd.merge(df_salida.reset_index(), df_entrada.reset_index()["time"], how="right", on="time").set_index("time")
    df_salida.to_csv(data_dir + "_output.csv")

if __name__ == '__main__':
    x = ["R6", "R8", "R9", "R11"]
    for i in x:
        process(data_dir=i)
        process(method_type="values",data_dir=i)