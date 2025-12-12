import pandas as pd

# -----------------------------
# Config
# -----------------------------
FILE = "D:\\FlinkWatermarkExp\\experiment_result\\slide_window_result_0.txt"
DELAY_ADD_VALUE = 0*1000*60  # 想加的固定值


# -----------------------------
# 1. Read TXT & Parse Lines
# -----------------------------
rows = []

with open(FILE, "r") as f:
    for line in f:
        line = line.strip()
        if not line or not (line.startswith("(") and line.endswith(")")):
            continue

        parts = line[1:-1].split(",", 3)
        if len(parts) != 4:
            continue

        window_start_ms, taxi_id, sum_tip, delay = parts

        rows.append({
            "window_ms": int(window_start_ms.strip()),
            "taxi": taxi_id.strip(),
            "sum_tip": float(sum_tip.strip()),
            "delay": int(delay.strip())
        })

df = pd.DataFrame(rows)

print(f"Loaded {len(df)} records")


# -----------------------------
# 2. Modify Delay Column
#    Only add value if delay >= 0
# -----------------------------
df["delay"] = df["delay"].apply(
    lambda d: d + DELAY_ADD_VALUE if d >= 0 else d
)

print(f"Added {DELAY_ADD_VALUE} to delay values >= 0")


# -----------------------------
# 3. Write BACK to Original File
# -----------------------------
with open(FILE, "w") as f:
    for _, row in df.iterrows():
        line = f"({row['window_ms']}, {row['taxi']}, {row['sum_tip']}, {row['delay']})"
        f.write(line + "\n")

print(f"Updated file written back to: {FILE}")
