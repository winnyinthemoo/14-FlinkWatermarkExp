import pandas as pd
import numpy as np

# -----------------------------
# Config
# -----------------------------
PARQUET_FILE = "C:\\Users\\alex\\Downloads\\yellow_tripdata_2024-02_first300k.parquet"
FLINK_OUTPUT_FILE = "D:\\FlinkWatermarkExp\\experiment_result\\window_result_60.txt"

TIME_COL = 'tpep_pickup_datetime'
TAXI_COL = 'VendorID'
TIP_COL = "tip_amount"
WINDOW_HOURS = 1

# -----------------------------
# 1. Load Ground Truth
# -----------------------------
df = pd.read_parquet(PARQUET_FILE)

df[TIP_COL] = df[TIP_COL].replace({r'\$': ''}, regex=True).astype(float)
df[TAXI_COL] = df[TAXI_COL].astype(str)

df[TIME_COL] = pd.to_datetime(df[TIME_COL], format="%m/%d/%Y %I:%M:%S %p", utc=False)
df[TIME_COL] = df[TIME_COL].dt.tz_localize(None)

df["hour_window"] = df[TIME_COL].dt.floor(f"{WINDOW_HOURS}h")

ground_truth_df = df.groupby(["hour_window", TAXI_COL])[TIP_COL].sum().reset_index()

ground_truth = {
    (row["hour_window"], row[TAXI_COL]): row[TIP_COL]
    for _, row in ground_truth_df.iterrows()
}

print(f"Ground truth: {len(ground_truth)} keys loaded")

# -----------------------------
# 2. Load Flink Output
# -----------------------------
flink_results = {}
tot_delay = 0
tot_cnt = 0
with open(FLINK_OUTPUT_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if not line or not (line.startswith("(") and line.endswith(")")):
            continue

        parts = line[1:-1].split(",", 3)
        window_start_ms, taxi_id, sum_tip, delay = parts

        window_start = pd.to_datetime(int(window_start_ms.strip()), unit='ms').tz_localize(None)
        taxi_id = taxi_id.strip()
        sum_tip = float(sum_tip.strip())
        delay = int(delay.strip())
        if delay <922337032760357:
            tot_delay += delay
            tot_cnt +=1
        flink_results[(window_start, taxi_id)] = sum_tip

print(f"Flink results: {len(flink_results)} keys loaded")
print(f"Average delay: {tot_delay / (tot_cnt*1000*60) if tot_cnt>0 else 0} min over {tot_cnt} records")
# -----------------------------
# 3. Align Keys into One DataFrame
# -----------------------------
all_keys = set(ground_truth.keys()) | set(flink_results.keys())

rows = []
for key in all_keys:
    rows.append({
        "window": key[0],
        "taxi": key[1],
        "true_tip": ground_truth.get(key, 0.0),
        "flink_tip": flink_results.get(key, 0.0)
    })

compare_df = pd.DataFrame(rows)

# -----------------------------
# 4. Compute Metrics
# -----------------------------
true_sum = compare_df["true_tip"].sum()
flink_sum = compare_df["flink_tip"].sum()

# Global error (percentage difference of totals)
global_error = abs(true_sum - flink_sum) / true_sum * 100

# Mean Absolute Error
mae = np.mean(np.abs(compare_df["flink_tip"] - compare_df["true_tip"]))

# Mean Absolute Percentage Error (exclude true_tip = 0)
nonzero = compare_df[compare_df["true_tip"] > 1e-9]
mape = np.mean(np.abs((nonzero["flink_tip"] - nonzero["true_tip"]) / nonzero["true_tip"])) * 100

# R² score
ss_res = np.sum((compare_df["flink_tip"] - compare_df["true_tip"]) ** 2)
ss_tot = np.sum((compare_df["true_tip"] - compare_df["true_tip"].mean()) ** 2)
r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

# -----------------------------
# 5. Print Results
# -----------------------------
print("======================================")
print(f"Total keys (window,taxi): {len(all_keys)}")
print("------ Global Metrics ------")
print(f"True total tip:  {true_sum:.2f}")
print(f"Flink total tip: {flink_sum:.2f}")
print(f"Global error:    {global_error:.4f}%")

print("------ Per-Record Metrics ------")
print(f"MAE:  {mae:.6f}")
print(f"MAPE: {mape:.4f}%")

print("------ Fit Metric ------")
print(f"R^2 score: {r2:.6f}")
