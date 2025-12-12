import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TIME_COL = 'tpep_pickup_datetime'
TAXI_COL = 'VendorID'
TIP_COL = "tip_amount"
WINDOW_HOURS = 1
SLIDE_MINUTES = 30  # 滑动步长 30 分钟

df = pd.read_parquet("C:\\Users\\alex\\Downloads\\yellow_tripdata_2024-02_first300k.parquet")

# 过滤日期
start_date = pd.Timestamp('2024-1-01')
end_date = pd.Timestamp('2024-4-10')
df = df[(df[TIME_COL] >= start_date) & (df[TIME_COL] <= end_date)].copy()

# 转换时间格式
df[TIME_COL] = pd.to_datetime(df[TIME_COL], format="%m/%d/%Y %I:%M:%S %p", utc=False)
df[TIME_COL] = df[TIME_COL].dt.tz_localize(None)

# ---------------------------------------------------
# 1. 生成滑动窗口边界
# ---------------------------------------------------
window_start = pd.date_range(start=df[TIME_COL].min(), end=df[TIME_COL].max(), freq=f'{SLIDE_MINUTES}min')
window_end = window_start + pd.Timedelta(hours=WINDOW_HOURS)

results = []

# ---------------------------------------------------
# 2. 遍历每个滑动窗口，计算延迟
# ---------------------------------------------------
for start, end in zip(window_start, window_end):
    window_df = df[(df[TIME_COL] >= start) & (df[TIME_COL] < end)].copy()
    
    if window_df.empty:
        continue
    
    # 计算每个 VendorID 的最大时间（类似 max_seen）
    window_df['max_seen'] = window_df.groupby(TAXI_COL)[TIME_COL].cummax()
    
    # 计算 delay（同小时不算）
    same_hour = window_df[TIME_COL].dt.hour == window_df['max_seen'].dt.hour
    window_df['delay_minutes'] = 0.0
    mask = ~same_hour
    window_df.loc[mask, 'delay_minutes'] = (
        (window_df.loc[mask, 'max_seen'] - window_df.loc[mask, TIME_COL]).dt.total_seconds() / 60.0
    )
    
    # 过滤延迟
    late_data = window_df[window_df['delay_minutes'] > 0.1]
    q99 = late_data['delay_minutes'].quantile(0.99)
    late_data = late_data[late_data['delay_minutes'] <= q99]
    
    late_data['max_seen_minute'] = late_data['max_seen'].dt.minute
    results.append(late_data['max_seen_minute'])

# ---------------------------------------------------
# 3. 绘制直方图
# ---------------------------------------------------
all_minutes = pd.concat(results)
plt.figure(figsize=(10, 6))
plt.hist(all_minutes, bins=100, edgecolor='black')
plt.xlabel("Minutes of First Record in New Window")
plt.ylabel("Influenced late data count")
plt.title("Sliding Window (1h length, 30min slide) Influence Histogram")
plt.tight_layout()
plt.show()
