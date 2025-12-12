import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# 1. 准备数据
# 滚动窗口数据
wm_rolling = [0, 5, 10, 15, 23, 25, 30, 60]
loss_rolling = [79.51, 19.41, 1.86, 1.85, 1.83, 0.64, 0.62, 0.53]
delay_rolling = [10.56, 40.15, 48.35, 47.73, 49.13, 49.13, 50.51, 68.43]

# 滑动窗口数据
wm_sliding = [0, 5, 10, 15, 23, 25, 30, 60]
loss_sliding = [40.69, 10.03, 1.26, 1.25, 1.28, 0.62, 0.53, 0.04]
delay_sliding = [15.69, 30.64, 35.81, 36.11, 38.06, 38.54, 45.89, 75.55]

plt.rcParams['font.family'] = 'sans-serif'


def plot_single_chart(wm, loss, delay, title, filename):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 使用等间距的索引作为 X 轴，解决 0-10 拥挤的问题
    x_pos = np.arange(len(wm))

    # --- 左轴：丢失率 (柱状图) ---
    color_loss = '#4c72b0'  # 稳重的深蓝
    ax1.set_xlabel('Watermark Delay (min)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Data Loss Rate (%)', color=color_loss, fontsize=12, fontweight='bold')

    # 柱子
    bars = ax1.bar(x_pos, loss, color=color_loss, alpha=0.6, width=0.5)
    ax1.tick_params(axis='y', labelcolor=color_loss)

    # 标上数值
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom', fontsize=9, color=color_loss)

    # --- 右轴：系统延迟 (折线图) ---
    ax2 = ax1.twinx()
    color_delay = '#c44e52'  # 柔和的深红
    ax2.set_ylabel('Avg System Delay (min)', color=color_delay, fontsize=12, fontweight='bold')

    # 折线
    ax2.plot(x_pos, delay, color=color_delay, marker='o', linestyle='-',
             linewidth=3, markersize=8)
    ax2.tick_params(axis='y', labelcolor=color_delay)

    # 将 X 轴刻度替换为真实的水位线数值
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(wm, fontsize=11)

    ax1.set_title(title, fontsize=14, pad=20, fontweight='bold')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.5)

    # 自定义图例
    legend_elements = [
        Patch(facecolor=color_loss, alpha=0.6, label='Data Loss Rate (Bar)'),
        Line2D([0], [0], color=color_delay, lw=3, marker='o', label='Avg Latency (Line)')
    ]
    ax1.legend(handles=legend_elements, loc='upper center', ncol=2, frameon=False)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)  # 保存高清图
    plt.show()


# 3. 执行生成
print("正在生成滚动窗口图...")
plot_single_chart(wm_rolling, loss_rolling, delay_rolling,
                  'Tumbling Window: Completeness vs Latency',
                  'tumbling_window_analysis.png')

print("正在生成滑动窗口图...")
plot_single_chart(wm_sliding, loss_sliding, delay_sliding,
                  'Sliding Window: Completeness vs Latency',
                  'sliding_window_analysis.png')