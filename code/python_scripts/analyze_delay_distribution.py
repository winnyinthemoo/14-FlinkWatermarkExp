import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PARQUET_FILE = "yellow_tripdata_2024-02.parquet"

def analyze_delay_distribution():
    print("正在读取数据...")
    df = pd.read_parquet(PARQUET_FILE)

    df = df.head(300000)

    time_col = 'tpep_pickup_datetime'

    # 转换时间
    df[time_col] = pd.to_datetime(df[time_col], utc=False).dt.tz_localize(None)

    print("正在计算迟到时长 (Delay Duration)...")

    # 模拟流式处理：计算每条数据的“迟到时长”
    # 逻辑：Delay = (目前为止见到的最大时间) - (当前数据时间)
    # 如果 Delay < 0，说明数据是新的最大时间（有序），Delay记为0

    # 1. 计算累积最大时间 (Cummax)
    df['max_seen'] = df[time_col].cummax()

    # 2. 计算延迟 (单位：分钟)
    df['delay_minutes'] = (df['max_seen'] - df[time_col]).dt.total_seconds() / 60.0

    # 3. 过滤掉非迟到数据 (Delay=0) 以便观察迟到数据的分布
    late_data = df[df['delay_minutes'] > 0.1]  # 只看迟到超过0.1分钟的数据

    print(f"总数据量: {len(df)}")
    print(f"迟到数据量: {len(late_data)} (占比 {len(late_data) / len(df) * 100:.2f}%)")

    plt.figure(figsize=(12, 6))

    # 直方图：迟到时长的分布
    # 重点关注 0~70 分钟的范围，因为你的实验 Watermark 就在这个范围
    bins = np.arange(0, 70, 1)  # 0到70分钟，每1分钟一个柱子

    n, bins, patches = plt.hist(late_data['delay_minutes'], bins=bins, color='skyblue', edgecolor='black', alpha=0.7)

    plt.title('Distribution of Data Arrival Delay (Time Lag)', fontsize=14)
    plt.xlabel('Delay Duration (Minutes)', fontsize=12)
    plt.ylabel('Number of Records', fontsize=12)
    plt.grid(axis='y', alpha=0.5)

    wm_points = [5, 10, 15, 23, 30, 60]
    colors = ['red', 'orange', 'green', 'green', 'blue', 'purple']

    for wm, color in zip(wm_points, colors):
        plt.axvline(x=wm, color=color, linestyle='--', linewidth=2, label=f'WM={wm}m')

    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    analyze_delay_distribution()