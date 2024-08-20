# -*- coding: utf-8 -*-

import gpxpy
import os
import math
import pandas as pd
from datetime import datetime

# 地球半径，单位米
EARTH_RADIUS = 6371000

# Haversine公式计算两个经纬度点之间的水平距离，并结合海拔差计算实际距离
def haversine(lat1, lon1, lat2, lon2, ele1, ele2):
    # 计算水平距离
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    horizontal_distance = EARTH_RADIUS * c

    # 计算海拔差
    elevation_diff = ele2 - ele1

    # 使用勾股定理计算实际距离
    distance = math.sqrt(horizontal_distance ** 2 + elevation_diff ** 2)
    
    return distance


# 使用ACSM公式计算能量消耗
def acsm_energy_expenditure(distance, elevation_change, speed, weight):
    if distance == 0 or speed == 0:
        return 0  # 如果距离或速度为0，直接返回0的能量消耗
    
    # 计算坡度（fractional grade）
    grade = elevation_change / distance if distance != 0 else 0
    
    if speed > 2.5 :  # 根据速度判断是否为running，2.5 m/s是徒步中常用的步行和跑步的分界速度
        vo2 = 0.2 * speed + 0.9 * speed * grade + 3.5
    else:
        vo2 = 0.1 * speed + 1.8 * speed * grade + 3.5
    
    # 计算总能量消耗，单位为kcal
    energy = vo2 * weight * (distance / (speed *60)) / 200  # kcal = mL/kg/min * kg * min / 1000 * 5
    
    return energy

# 计算路线中的每段距离、海拔变化、速度和能量消耗
def calculate_route_energy(route_points, weight):
    distances = []
    elevations = []
    speeds = []
    energies = []
    
    for i in range(1, len(route_points)):
        lat1, lon1, ele1, time1 = route_points[i-1]
        lat2, lon2, ele2, time2 = route_points[i]
        
        # 传递海拔参数计算实际距离
        dist = haversine(lat1, lon1, lat2, lon2, ele1, ele2)
        ele_change = ele2 - ele1
        time_delta = time2 - time1
        
        if time_delta.total_seconds() > 0:
            speed = dist / time_delta.total_seconds()
        else:
            speed = 0  # 如果时间差为0，速度设为0
        
        energy = acsm_energy_expenditure(dist, ele_change, speed, weight)
        
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
def process_all_gpx_files(directory, weight):
    all_trail_data = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            file_path = os.path.join(directory, filename)
            route_points = extract_route_points(file_path)
            if route_points:
                trail_name = os.path.splitext(filename)[0]
                trail_data = calculate_route_energy(route_points, weight)
                
                # 保存每条trail的结果为单独的CSV文件
                output_file = os.path.join(directory, f"{trail_name}_energy_data.csv")
                trail_data.to_csv(output_file, index=False)
                
                all_trail_data[trail_name] = trail_data
    
    return all_trail_data

# 使用代码并处理所有文件
directory = './gpxfiles'
weight = 70  # 设定用户体重为70kg
trail_data = process_all_gpx_files(directory, weight)
