# -*- coding: utf-8 -*-

import gpxpy
import os
import pandas as pd

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

# ������GPX�ļ�������ƥ����
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
                output_file = os.path.join(directory_files, f"{trail_name}_matched_data.csv")
                df.to_csv(output_file, index=False)
    
    return trail_data

# ʹ�ô��벢���������ļ�
directory_tracks = './gpxtracks'
directory_files = './gpxfiles'
trail_data = process_all_trails(directory_tracks, directory_files)
