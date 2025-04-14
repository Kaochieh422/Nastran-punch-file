# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 13:34:37 2025

@author: TSENG KAO CHIEH
"""

import re
import numpy as np
import matplotlib.pyplot as plt

filepath = r"D:\0859\APEX_Working_Directory\5_sol111_sin vibration-1_2.pch"  # 輸入檔案路徑
title_filter = 'CASE_1_X'  # 要搜尋的 $TITLE
target_grids = [6726, 83103, 83274, 84061, 84599, 84813, 504817, 510401, 510402]  # 節點 ID 列表
target_component = 'T1'  # 改這裡選方向，例：T1, T2, T3, R3, T1.imag...
G = 9806.65  # 加速度單位轉換為 G（重力加速度），不需要時改1
# G = 1
# 方向索引
component_map = {
    'T1': 0, 'T2': 1, 'T3': 2,
    'R1': 3, 'R2': 4, 'R3': 5,
    'T1.imag': 6, 'T2.imag': 7, 'T3.imag': 8,
    'R1.imag': 9, 'R2.imag': 10, 'R3.imag': 11
}

def read_pch_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin1', errors='ignore') as f:
            return f.read()

def extract_acceleration_block(text_block, grid_id):
    lines = text_block.strip().splitlines()
    values = []
    reading = False

    for line in lines:
        line = re.sub(r'\s+\d+\s*$', '', line)
        if not reading:
            if re.match(rf'\s*{grid_id}\s+G', line):
                nums = re.findall(r'[-+]?\d*\.\d+E[+-]?\d+', line)
                values.extend([float(n) for n in nums])
                reading = True
        else:
            if '-CONT-' in line:
                nums = re.findall(r'[-+]?\d*\.\d+E[+-]?\d+', line)
                values.extend([float(n) for n in nums])
            else:
                break
        if len(values) >= 12:
            break

    return values if len(values) == 12 else None

component_index = component_map.get(target_component)
if component_index is None:
    print(f"無效方向名稱: {target_component}")

text = read_pch_file(filepath)
blocks = re.split(r'\$TITLE\s*=\s*', text)
freq_list = []
accel_dict = {grid_id: [] for grid_id in target_grids}

for block in blocks:
    if block.strip().startswith(title_filter):
        lines = block.splitlines()
        current_freq = None

        for i, line in enumerate(lines):
            if '$FREQUENCY' in line:
                freq_match = re.search(r'[-+]?\d*\.\d+E[+-]?\d+', line)
                if freq_match:
                    current_freq = float(freq_match.group())

            for grid_id in target_grids:
                if re.match(rf'\s*{grid_id}\s+G', line):
                    block_text = '\n'.join(lines[i:i+4])
                    acc_vals = extract_acceleration_block(block_text, grid_id)
                    if acc_vals and current_freq is not None:
                        if not current_freq in freq_list:
                            freq_list.append(current_freq)
                        accel_dict[grid_id].append(acc_vals[component_index])

# 畫圖
if freq_list:
    # plt.figure(figsize=(8, 5))
    # plt.figure(figsize=(10, 6))
    for grid_id, accel_list in accel_dict.items():
        if accel_list:
            plt.plot(freq_list, np.array(accel_list) / G, marker='o', markersize=6, label=f'Grid {grid_id} - {target_component}')

    plt.ticklabel_format(useOffset=False, style='plain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel(f'{target_component} Acceleration (g)')
    plt.title(f'{title_filter} - Acceleration vs Frequency')
    plt.legend()
    
    # xticks = np.arange(0.0, 121.0, 20)
    # plt.xticks(xticks)
    # yticks = np.arange(31.29, 31.31, 0.003)
    # plt.yticks(yticks)
    
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("沒找到任何符合條件的頻率資料")
