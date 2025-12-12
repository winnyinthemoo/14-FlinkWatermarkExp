import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 配置
PARQUET_FILE = "yellow_tripdata_2024-02.parquet"
TIME_COL = 'tpep_pickup_datetime'


def analyze_hour_jump():
    print("Loading data...")
    # 读取数据（模拟 Flink Source 的读取顺序）
    df = pd.read_parquet(PARQUET_FILE)

    # 按照文件物理顺序截取（和实验一致）
    df = df.head(300000).copy()

    # 时间转换
    df[TIME_COL] = pd.to_datetime(df[TIME_COL], utc=False).dt.tz_localize(None)

    # 1. 计算全局 MaxSeen (模拟 Flink 的 Watermark 生成机制)
    df['max_seen'] = df[TIME_COL].cummax()

    # 2. 寻找“小时跳变点”
    # 提取 MaxSeen 的小时部分 (归整到 :00:00)
    df['max_seen_hour'] = df['max_seen'].dt.floor('h')

    # 找到每个新小时出现的“第一行数据”
    # drop_duplicates 会保留每个小时第一次出现的那一行
    hour_trigger_points = df.drop_duplicates(subset=['max_seen_hour'], keep='first').copy()

    # 3. 计算“跳变幅度” (Jump Minute)
    # 计算这第一条数据的时间，距离它所属的小时起始点过了多久
    # 例如：MaxSeen 变成了 13:23，所属小时是 13:00，则跳变幅度为 23 分钟
    hour_trigger_points['jump_minute'] = (hour_trigger_points['max_seen'] - hour_trigger_points[
        'max_seen_hour']).dt.total_seconds() / 60.0

    # 过滤掉 jump_minute = 0 的（说明数据很完美，xx:00 就来了，没有跳变）
    jump_data = hour_trigger_points[hour_trigger_points['jump_minute'] > 1.0]

    print(f"Total Hours Analyzed: {len(hour_trigger_points)}")
    print(f"Significant Jumps Found: {len(jump_data)}")

    plt.figure(figsize=(10, 6))

    # 绘制直方图，看看跳变分钟数主要集中在哪里
    n, bins, patches = plt.hist(jump_data['jump_minute'], bins=range(0, 61, 1),
                                color='#e74c3c', edgecolor='black', alpha=0.7)

    plt.xlabel("Minute of the First Record in New Hour (Jump Magnitude)", fontsize=12)
    plt.ylabel("Frequency (Count of Hours)", fontsize=12)
    plt.title("Why the Plateau Exists: Distribution of Hour-Crossing Jumps", fontsize=14)
    plt.grid(axis='y', alpha=0.3)

    plt.axvspan(10, 25, color='yellow', alpha=0.3, label='Plateau Zone (10-23m)')
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    analyze_hour_jump()
