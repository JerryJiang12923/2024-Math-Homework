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
    return pd.DataFrame(points), gpx

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
        return None, None
    
    df_tracks = read_gpx_file_tracks(file_path_tracks)
    df_files, gpx = read_gpx_file_files(file_path_files)
    
    merged_df = strict_merge_data(df_tracks, df_files)
    if merged_df.empty:
        print(f"No data to process for trail: {trail_name}")
        return None, None
    
    return merged_df, gpx

# ��ƥ��������ΪGPX�ļ�
def save_to_gpx(merged_df, gpx, output_file_path):
    new_gpx = gpxpy.gpx.GPX()
    route = gpxpy.gpx.GPXRoute()

    for _, row in merged_df.iterrows():
        point = gpxpy.gpx.GPXRoutePoint(
            latitude=row['latitude'],
            longitude=row['longitude'],
            elevation=row['elevation'],
            time=row['time']
        )
        route.points.append(point)

    new_gpx.routes.append(route)

    with open(output_file_path, 'w') as f:
        f.write(new_gpx.to_xml())

# ��������GPX�ļ���������
def process_all_trails(directory_tracks, directory_files):
    for filename in os.listdir(directory_files):
        if filename.endswith(".gpx"):
            trail_name = os.path.splitext(filename)[0]
            merged_df, gpx = process_single_gpx_file(trail_name, directory_tracks, directory_files)
            if merged_df is not None and not merged_df.empty:
                # ������ΪGPX�ļ�
                output_file = os.path.join(directory_files, f"{trail_name}_matched.gpx")
                save_to_gpx(merged_df, gpx, output_file)

# ʹ�ô��벢���������ļ�
directory_tracks = './gpxtracks'
directory_files = './gpxfiles'
process_all_trails(directory_tracks, directory_files)
