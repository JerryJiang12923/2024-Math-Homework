# -*- coding: utf-8 -*-

import os
from datetime import timedelta, datetime

# ��ȡ estimated_time.txt ���洢ÿ�� trail ��ʵ����ʱ�䣨ת��Ϊ�룩
def load_estimated_times(file_path):
    estimated_times = {}
    with open(file_path, 'r') as file:
        for line in file:
            trail, time_str = line.strip().split()
            # ��ʱ��ӷ���ת��Ϊ��
            estimated_times[trail] = int(time_str) * 60
    return estimated_times

def parse_gpx_file(file_path):
    #"""����GPX�ļ��е�ʱ���"""
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
    #"""��GPX�ļ��ж�ȡʱ�䣬����ȷ����ʱ��󱣴浽�µ�GPX�ļ���"""
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

    # �滻 lines �е�ʱ��
    adjusted_lines = []
    time_index = 0
    for line in lines:
        if "<time>" in line:
            new_time_str = adjusted_times[time_index].isoformat() + "Z"
            new_time_str = new_time_str.replace("+00:00Z", "Z")  # �Ƴ������ʱ����־
            adjusted_line = f"      <time>{new_time_str}</time>\n"
            adjusted_lines.append(adjusted_line)
            time_index += 1
        else:
            adjusted_lines.append(line)

    # ���޸ĺ������д���ļ�
    with open(output_path, 'w') as output_file:
        output_file.writelines(adjusted_lines)

# ���� estimated_time.txt �ļ��е�����
estimated_times = load_estimated_times('estimated_time.txt')

# ���� GPX �ļ��洢�� ./gpxfiles Ŀ¼��
gpx_directory = './gpxfiles/'
output_directory = './gpxfiles/adjusted/'  # �����������ļ�

# ȷ�����Ŀ¼����
os.makedirs(output_directory, exist_ok=True)

# ����Ŀ¼�е����� GPX �ļ���ƥ��Ԥ��ʱ�䲢����
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

