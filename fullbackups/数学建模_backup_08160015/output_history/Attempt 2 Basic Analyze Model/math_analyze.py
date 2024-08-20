# -*- coding: utf-8 -*-

import gpxpy
import gpxpy.gpx
import os
import math
import pandas as pd

# 地球半径，单位米
EARTH_RADIUS = 6371000

# 读取GPX文件的函数
def read_gpx_file(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time
                })
    return pd.DataFrame(points)

# 计算距离和海拔变化的函数
def haversine(lat1, lon1, lat2, lon2):
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c

def compute_distance_and_elevation(df):
    distances = []
    elevations = []
    for i in range(1, len(df)):
        dist = haversine(df.iloc[i-1]['latitude'], df.iloc[i-1]['longitude'], df.iloc[i]['latitude'], df.iloc[i]['longitude'])
        ele_change = df.iloc[i]['elevation'] - df.iloc[i-1]['elevation']
        distances.append(dist)
        elevations.append(ele_change)
        
    df['distance'] = [0] + distances
    df['elevation_change'] = [0] + elevations
    return df

# 能量消耗模型
def energy_consumption(df):
    df['slope'] = df['elevation_change'] / df['distance']
    df['energy'] = df.apply(lambda row: row['distance'] + (row['elevation_change'] * 10) if row['elevation_change'] > 0 else row['distance'], axis=1)
    return df

# 处理单个GPX文件并返回计算结果
def process_single_gpx_file(file_path):
    df = read_gpx_file(file_path)
    df = compute_distance_and_elevation(df)
    df = energy_consumption(df)
    return df

# 处理所有GPX文件并返回计算结果
def process_all_trails(directory):
    trail_data = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            file_path = os.path.join(directory, filename)
            trail_name = os.path.splitext(filename)[0]
            df = process_single_gpx_file(file_path)
            trail_data[trail_name] = df
            
            # 保存每条trail的结果为单独的CSV文件
            output_file = os.path.join(directory, f"{trail_name}_energy_data.csv")
            df.to_csv(output_file, index=False)
    
    return trail_data

# 使用代码并处理所有文件
directory = './gpxfiles'
trail_data = process_all_trails(directory)

# 现在，每个trail的数据分别保存在对应的CSV文件中，trail_data字典中也包含了每个trail的数据框

