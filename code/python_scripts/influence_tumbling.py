import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TIME_COL = 'tpep_pickup_datetime'
TAXI_COL = 'VendorID'
TIP_COL = "tip_amount"
WINDOW_HOURS = 1

df = pd.read_parquet("C:\\Users\\alex\\Downloads\\yellow_tripdata_2024-02_first300k.parquet")

# 过滤日期
start_date = pd.Timestamp('2024-1-01')
end_date = pd.Timestamp('2024-4-10')
df = df[(df[TIME_COL] >= start_date) & (df[TIME_COL] <= end_date)].copy()

# 转换时间格式
df[TIME_COL] = pd.to_datetime(df[TIME_COL], format="%m/%d/%Y %I:%M:%S %p", utc=False)
df[TIME_COL] = df[TIME_COL].dt.tz_localize(None)

# ---------------------------------------------------
# ⭐ 1. 计算累计最大时间
# ---------------------------------------------------
# df['max_seen'] = df[TIME_COL].cummax()
df['max_seen'] = df.groupby(TAXI_COL)[TIME_COL].cummax()

# ---------------------------------------------------
# ⭐ 2. 判断是否处于同一小时段
#    同小时段 → 不计算延迟（delay=0）
#    不同小时段 → 计算延迟
# ---------------------------------------------------
same_hour = df[TIME_COL].dt.hour == df['max_seen'].dt.hour

# 初始化 delay 列
df['delay_minutes'] = 0.0

# 仅在小时不同的行，计算 delay
mask = ~same_hour
df.loc[mask, 'delay_minutes'] = (
    (df.loc[mask, 'max_seen'] - df.loc[mask, TIME_COL]).dt.total_seconds() / 60.0
)

# ---------------------------------------------------
# 3. 过滤迟到数据
# ---------------------------------------------------
late_data = df[df['delay_minutes'] > 0.1]
#late_data=df
q99 = late_data['delay_minutes'].quantile(0.99)
late_data = late_data[late_data['delay_minutes'] <= q99]

# ---------------------------------------------------
# 4. 用 max_seen 的分钟数替代 delay_minutes
# ---------------------------------------------------
late_data['max_seen_minute'] = late_data['max_seen'].dt.minute



# ---------------------------------------------------
# 4. 绘制直方图
# ---------------------------------------------------
plt.figure(figsize=(10, 6))
plt.hist(
    late_data['max_seen_minute'],
    bins=100,
    edgecolor='black'
)
plt.xlabel("late time(minutes)")
plt.ylabel("data count")
plt.title("Late Time Distribution Histogram")
plt.tight_layout()
plt.show()
