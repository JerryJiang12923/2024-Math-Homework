# -*- coding: utf-8 -*-

import gpxpy
import os
import math
import pandas as pd

# ����뾶����λ��
EARTH_RADIUS = 6371000

# ��ȡgpxtracks�е�GPX�ļ��ĺ���
def read_gpx_file_tracks(file_path):
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
                })
    return pd.DataFrame(points)

# ��ȡgpxfiles�е�GPX�ļ��ĺ���
def read_gpx_file_files(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
    points = []
    for route in gpx.routes:
        for point in route.points:
            points.append({
                'latitude': point.latitude,
                'longitude': point.longitude,
                'time': point.time
            })
    return pd.DataFrame(points)

# �ϸ�ƥ�侭γ�ȵ����ݺϲ�
def strict_merge_data(df_tracks, df_files):
    # ��ȷƥ����ͬ��γ�ȵ����ݵ�
    merged_df = pd.merge(df_tracks, df_files, on=['latitude', 'longitude'], how='inner')
    return merged_df

# Haversine��ʽ����������γ�ȵ�֮��ľ���
def haversine(lat1, lon1, lat2, lon2):
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c

# �������ͺ��α仯�ĺ���
def compute_distance_and_elevation(df):
    distances = []
    elevations = []
    times = []
    for i in range(1, len(df)):
        dist = haversine(df.iloc[i-1]['latitude'], df.iloc[i-1]['longitude'], df.iloc[i]['latitude'], df.iloc[i]['longitude'])
        ele_change = df.iloc[i]['elevation'] - df.iloc[i-1]['elevation']
        time_delta = (df.iloc[i]['time'] - df.iloc[i-1]['time']).total_seconds()
        distances.append(dist)
        elevations.append(ele_change)
        times.append(time_delta)
        
    df['distance'] = [0] + distances
    df['elevation_change'] = [0] + elevations
    df['time_delta'] = [0] + times
    df['speed'] = df['distance'] / df['time_delta']
    return df

# ��������ģ��
def energy_consumption(df):
    # ʹ���¶ȼ�����������
    df['slope'] = df['elevation_change'] / df['distance']
    df['energy'] = df.apply(lambda row: row['distance'] * (0.1 + 1.8 * abs(row['slope']) + 3.5) if row['distance'] > 0 else 0, axis=1)
    return df

# ������GPX�ļ������ؼ�����
def process_single_gpx_file(trail_name, directory_tracks, directory_files):
    file_path_tracks = os.path.join(directory_tracks, f"{trail_name}.gpx")
    file_path_files = os.path.join(directory_files, f"{trail_name}.gpx")
    
    if not os.path.exists(file_path_tracks) or not os.path.exists(file_path_files):
        print(f"Skipping {trail_name} due to missing files.")
        return None
    
    df_tracks = read_gpx_file_tracks(file_path_tracks)
    df_files = read_gpx_file_files(file_path_files)
    
    merged_df = strict_merge_data(df_tracks, df_files)
    if merged_df.empty:
        print(f"No data to process for trail: {trail_name}")
        return None
    
    merged_df = compute_distance_and_elevation(merged_df)
    merged_df = energy_consumption(merged_df)
    
    return merged_df

# ��������GPX�ļ���������
def process_all_trails(directory_tracks, directory_files):
    trail_data = {}
    
    for filename in os.listdir(directory_files):
        if filename.endswith(".gpx"):
            trail_name = os.path.splitext(filename)[0]
            df = process_single_gpx_file(trail_name, directory_tracks, directory_files)
            if df is not None and not df.empty:
                trail_data[trail_name] = df
                # ����ÿ��trail�Ľ��Ϊ������CSV�ļ�
                output_file = os.path.join(directory_files, f"{trail_name}_energy_data.csv")
                df.to_csv(output_file, index=False)
    
    return trail_data

# ʹ�ô��벢���������ļ�
directory_tracks = './gpxtracks'
directory_files = './gpxfiles'
trail_data = process_all_trails(directory_tracks, directory_files)
