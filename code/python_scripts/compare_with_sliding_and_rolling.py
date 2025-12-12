import matplotlib.pyplot as plt
import numpy as np

# 滚动窗口数据
wm_roll = [0, 5, 10, 15, 23, 25, 30, 60]
delay_roll = [10.56, 40.15, 48.35, 47.73, 49.13, 49.13, 50.51, 68.43]
error_roll = [82.06, 27.73, 11.01, 11.00, 10.98, 9.89, 9.88, 9.79]
r2_roll = [-0.822, 0.543, 0.955, 0.955, 0.956, 0.977, 0.977, 0.977]
mape_roll = [63.81, 21.47, 10.78, 10.75, 10.73, 10.59, 9.98, 9.88]

# 滑动窗口数据
wm_slide = [0, 5, 10, 15, 23, 25, 30, 60]
delay_slide = [15.69, 30.64, 35.81, 36.11, 38.06, 38.54, 45.89, 75.55]
error_slide = [68.66, 40.63, 32.44, 32.24, 32.93, 31.70, 28.13, 9.55]
r2_slide = [-0.270, 0.427, 0.631, 0.633, 0.628, 0.644, 0.703, 0.979]
mape_slide = [57.66, 35.49, 30.63, 30.11, 32.96, 29.96, 23.64, 9.73]

plt.style.use('seaborn-v0_8-whitegrid')  # 风格


def generate_single_chart(y_roll, y_slide, ylabel, title, filename, is_percent=False):
    plt.figure(figsize=(8, 6))

    # 绘制线条
    plt.plot(wm_roll, y_roll, marker='o', label='Tumbling Window',
             color='#1f77b4', linewidth=2.5, markersize=8)
    plt.plot(wm_slide, y_slide, marker='s', label='Sliding Window',
             color='#ff7f0e', linewidth=2.5, markersize=8)

    # 设置标签
    plt.xlabel('Watermark Delay (min)', fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.title(title, fontsize=14, pad=15, fontweight='bold')

    # 图例
    plt.legend(fontsize=11, frameon=True)

    # 如果是百分比，限制Y轴范围以便观察
    if is_percent:
        plt.ylim(0, max(max(y_roll), max(y_slide)) + 10)

    # 保存与展示
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Generated: {filename}")
    plt.close()


# 1. 系统延迟对比 (Latency)
generate_single_chart(delay_roll, delay_slide,
                      'Avg System Delay (min)',
                      'Latency Comparison: Tumbling vs Sliding',
                      'cmp_latency.png')

# 2. 全局误差对比 (Global Error)
generate_single_chart(error_roll, error_slide,
                      'Global Error (%)',
                      'Accuracy Comparison: Global Error',
                      'cmp_global_error.png', is_percent=True)

# 3. R^2 Score 对比 (Statistical Fit)
# R^2 需要特殊处理一下Y轴范围，因为它有负数
plt.figure(figsize=(8, 6))
plt.axhline(y=0.9, color='gray', linestyle='--', alpha=0.5, label='High Confidence (0.9)')  # 参考线
plt.axhline(y=0, color='black', linewidth=1)  # 0轴
plt.plot(wm_roll, r2_roll, marker='o', label='Tumbling Window', color='#1f77b4', linewidth=2.5)
plt.plot(wm_slide, r2_slide, marker='s', label='Sliding Window', color='#ff7f0e', linewidth=2.5)
plt.xlabel('Watermark Delay (min)', fontsize=12, fontweight='bold')
plt.ylabel('R² Score', fontsize=12, fontweight='bold')
plt.title('Statistical Confidence: R² Score Comparison', fontsize=14, pad=15, fontweight='bold')
plt.legend(fontsize=11, loc='lower right')
plt.tight_layout()
plt.savefig('cmp_r2_score.png', dpi=300)
print("Generated: cmp_r2_score.png")
plt.close()

# 4. MAPE 对比
generate_single_chart(mape_roll, mape_slide,
                      'MAPE (%)',
                      'Stability Comparison: MAPE',
                      'cmp_mape.png', is_percent=True)