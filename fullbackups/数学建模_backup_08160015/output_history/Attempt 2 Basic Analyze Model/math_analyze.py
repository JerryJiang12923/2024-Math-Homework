# -*- coding: utf-8 -*-

import gpxpy
import gpxpy.gpx
import os
import math
import pandas as pd

# ����뾶����λ��
EARTH_RADIUS = 6371000

# ��ȡGPX�ļ��ĺ���
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

# �������ͺ��α仯�ĺ���
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

# ��������ģ��
def energy_consumption(df):
    df['slope'] = df['elevation_change'] / df['distance']
    df['energy'] = df.apply(lambda row: row['distance'] + (row['elevation_change'] * 10) if row['elevation_change'] > 0 else row['distance'], axis=1)
    return df

# ������GPX�ļ������ؼ�����
def process_single_gpx_file(file_path):
    df = read_gpx_file(file_path)
    df = compute_distance_and_elevation(df)
    df = energy_consumption(df)
    return df

# ��������GPX�ļ������ؼ�����
def process_all_trails(directory):
    trail_data = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            file_path = os.path.join(directory, filename)
            trail_name = os.path.splitext(filename)[0]
            df = process_single_gpx_file(file_path)
            trail_data[trail_name] = df
            
            # ����ÿ��trail�Ľ��Ϊ������CSV�ļ�
            output_file = os.path.join(directory, f"{trail_name}_energy_data.csv")
            df.to_csv(output_file, index=False)
    
    return trail_data

# ʹ�ô��벢���������ļ�
directory = './gpxfiles'
trail_data = process_all_trails(directory)

# ���ڣ�ÿ��trail�����ݷֱ𱣴��ڶ�Ӧ��CSV�ļ��У�trail_data�ֵ���Ҳ������ÿ��trail�����ݿ�

