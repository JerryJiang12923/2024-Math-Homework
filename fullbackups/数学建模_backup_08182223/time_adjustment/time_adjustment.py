# -*- coding: utf-8 -*-

import os
from datetime import timedelta, datetime

# 读取 estimated_time.txt 并存储每个 trail 的实际总时间（转换为秒）
def load_estimated_times(file_path):
    estimated_times = {}
    with open(file_path, 'r') as file:
        for line in file:
            trail, time_str = line.strip().split()
            # 将时间从分钟转换为秒
            estimated_times[trail] = int(time_str) * 60
    return estimated_times

def parse_gpx_file(file_path):
    #"""解析GPX文件中的时间戳"""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    times = []
    for line in lines:
        if "<time>" in line:
            time_str = line.strip().replace("<time>", "").replace("</time>", "")
            times.append(datetime.fromisoformat(time_str.replace("Z", "+00:00")))

    total_time = sum((times[i] - times[i-1]).total_seconds() for i in range(1, len(times)))
    return total_time, times, lines

def adjust_times_and_save(file_path, output_path, estimated_total_time):
    #"""从GPX文件中读取时间，并正确调整时间后保存到新的GPX文件中"""
    total_gpx_time, times, lines = parse_gpx_file(file_path)

    time_scale_factor = estimated_total_time / total_gpx_time

    adjusted_times = [times[0]]
    for i in range(1, len(times)):
        previous_time = adjusted_times[-1]
        original_time = times[i]
        time_diff = (original_time - times[i - 1]).total_seconds()
        adjusted_time_diff = time_diff * time_scale_factor
        adjusted_time = previous_time + timedelta(seconds=adjusted_time_diff)
        adjusted_times.append(adjusted_time)

    # 替换 lines 中的时间
    adjusted_lines = []
    time_index = 0
    for line in lines:
        if "<time>" in line:
            new_time_str = adjusted_times[time_index].isoformat() + "Z"
            new_time_str = new_time_str.replace("+00:00Z", "Z")  # 移除多余的时区标志
            adjusted_line = f"      <time>{new_time_str}</time>\n"
            adjusted_lines.append(adjusted_line)
            time_index += 1
        else:
            adjusted_lines.append(line)

    # 将修改后的内容写回文件
    with open(output_path, 'w') as output_file:
        output_file.writelines(adjusted_lines)

# 加载 estimated_time.txt 文件中的数据
estimated_times = load_estimated_times('estimated_time.txt')

# 假设 GPX 文件存储在 ./gpxfiles 目录下
gpx_directory = './gpxfiles/'
output_directory = './gpxfiles/adjusted/'  # 保存调整后的文件

# 确保输出目录存在
os.makedirs(output_directory, exist_ok=True)

# 遍历目录中的所有 GPX 文件，匹配预期时间并调整
for gpx_file_name in os.listdir(gpx_directory):
    if gpx_file_name.endswith('.gpx'):
        trail_name = gpx_file_name.replace('.gpx', '')
        if trail_name in estimated_times:
            gpx_file_path = os.path.join(gpx_directory, gpx_file_name)
            output_file_path = os.path.join(output_directory, gpx_file_name.replace('.gpx', '_adjusted.gpx'))
            estimated_time = estimated_times[trail_name]
            adjust_times_and_save(gpx_file_path, output_file_path, estimated_time)
            print(f"Processed {gpx_file_name} with estimated time {estimated_time / 60} minutes.")

print("All files processed.")

