# -*- coding: utf-8 -*-

import gpxpy
import os
import math
import pandas as pd
from datetime import datetime

# 地球半径，单位米
EARTH_RADIUS = 6371000

# Haversine公式计算两个经纬度点之间的距离
def haversine(lat1, lon1, lat2, lon2):
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c

# 使用ACSM公式计算能量消耗
def acsm_energy_expenditure(distance, elevation_change, speed):
    if speed > 4:  # 根据速度判断是否为running，2.5 m/s是个常用的步行和跑步的分界速度
        return 0.2 * distance + 0.9 * distance * elevation_change / distance + 3.5
    else:
        return 0.1 * distance + 1.8 * distance * elevation_change / distance + 3.5

# 计算路线中的每段距离、海拔变化、速度和能量消耗
def calculate_route_energy(route_points):
    distances = []
    elevations = []
    speeds = []
    energies = []
    
    for i in range(1, len(route_points)):
        lat1, lon1, ele1, time1 = route_points[i-1]
        lat2, lon2, ele2, time2 = route_points[i]
        
        dist = haversine(lat1, lon1, lat2, lon2)
        ele_change = ele2 - ele1
        time_delta = time2 - time1
        speed = dist / time_delta.total_seconds() if time_delta.total_seconds() > 0 else 0
        energy = acsm_energy_expenditure(dist, ele_change, speed)
        
        distances.append(dist)
        elevations.append(ele_change)
        speeds.append(speed)
        energies.append(energy)
    
    return pd.DataFrame({
        'distance': distances,
        'elevation_change': elevations,
        'speed': speeds,
        'energy': energies
    })

# 从GPX文件中提取route points数据
def extract_route_points(gpx_file_path):
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    
    route_points = []
    if len(gpx.routes) > 0:
        for route in gpx.routes:
            for point in route.points:
                route_points.append((point.latitude, point.longitude, point.elevation, point.time))
    
    return route_points

# 处理所有GPX文件
def process_all_gpx_files(directory):
    all_trail_data = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            file_path = os.path.join(directory, filename)
            route_points = extract_route_points(file_path)
            if route_points:
                trail_name = os.path.splitext(filename)[0]
                trail_data = calculate_route_energy(route_points)
                
                # 保存每条trail的结果为单独的CSV文件
                output_file = os.path.join(directory, f"{trail_name}_energy_data.csv")
                trail_data.to_csv(output_file, index=False)
                
                all_trail_data[trail_name] = trail_data
    
    return all_trail_data

# 使用代码并处理所有文件
directory = './gpxfiles'
trail_data = process_all_gpx_files(directory)
