# -*- coding: utf-8 -*-


import gpxpy
import os

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
    return points

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
    return points

# ��ӡ�����ļ���ǰ���������ϸ��Ϣ
def print_points_info(trail_name, directory_tracks, directory_files):
    file_path_tracks = os.path.join(directory_tracks, f"{trail_name}.gpx")
    file_path_files = os.path.join(directory_files, f"{trail_name}.gpx")
    
    if not os.path.exists(file_path_tracks) or not os.path.exists(file_path_files):
        print(f"Skipping {trail_name} due to missing files.")
        return
    
    points_tracks = read_gpx_file_tracks(file_path_tracks)
    points_files = read_gpx_file_files(file_path_files)
    
    if not points_tracks or not points_files:
        print(f"No data found for trail: {trail_name}")
        return
    
    print(f"\nPoints from {trail_name} in gpxtracks:")
    for i, point in enumerate(points_tracks[:5]):  # ��ӡǰ5����
        print(f"Point {i}: Latitude={point['latitude']}, Longitude={point['longitude']}, Elevation={point['elevation']}")
    
    print(f"\nPoints from {trail_name} in gpxfiles:")
    for i, point in enumerate(points_files[:5]):  # ��ӡǰ5����
        print(f"Point {i}: Latitude={point['latitude']}, Longitude={point['longitude']}, Time={point['time']}")

# ʹ�ô��벢���������ļ�
directory_tracks = './gpxtracks'
directory_files = './gpxfiles'

# ѡ��һ��trail���жԱ�
trail_name = 'Shisun_Gang_'  # ��ʵ���ļ����滻
print_points_info(trail_name, directory_tracks, directory_files)
