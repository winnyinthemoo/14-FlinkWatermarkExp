import matplotlib.pyplot as plt
import numpy as np

# Watermark 节点
wm_points = [0, 5, 10, 15, 23, 25, 30, 60]

# 对应的丢失数据量 (Missing Count)
missing_counts = [238535, 58220, 5594, 5563, 5498, 1908, 1871, 1575]

# 计算每个区间“救回”的数据量 (即该迟到区间内的数据密度)
recovered_counts = []
labels = []

for i in range(len(wm_points) - 1):
    start = wm_points[i]
    end = wm_points[i + 1]

    # 救回量 = 上一个丢失量 - 当前丢失量
    count = missing_counts[i] - missing_counts[i + 1]
    recovered_counts.append(count)
    labels.append(f"{start}-{end}m")

plt.figure(figsize=(12, 6))

# 使用柱状图展示分布
bars = plt.bar(range(len(labels)), recovered_counts, color='#69b3a2', edgecolor='black', alpha=0.8)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2., height + 2000,
             f'{int(height)}',
             ha='center', va='bottom', fontsize=10)

plt.title('Inferred Data Delay Distribution (Based on Flink Results)', fontsize=14, pad=20)
plt.xlabel('Delay Duration Interval (Minutes)', fontsize=12)
plt.ylabel('Number of Records', fontsize=12)
plt.xticks(range(len(labels)), labels, fontsize=11)
plt.grid(axis='y', alpha=0.3, linestyle='--')

# 添加解释性标注
plt.annotate('Long Tail Starts Here\n(The "Plateau" in results)',
             xy=(2, 5000), xytext=(3, 40000),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.annotate('Majority of Data\n(0-10m Late)',
             xy=(0, 150000), xytext=(1, 150000),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.tight_layout()
plt.show()