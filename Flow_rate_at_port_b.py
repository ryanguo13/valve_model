import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- 代码开始 ---

def main():
    """
    主函数，用于加载数据并生成三个独立的图表。
    请确保 'positive_mass_flow_data.csv' 和 'valve_data.csv' 
    这两个文件与此脚本位于同一个文件夹中。
    """
    print("开始生成图表...")
    print("=" * 50)

    # --- 数据加载 ---
    # 1. 读取您的两个CSV文件
    mass_flow_filename = 'positive_mass_flow_data.csv'
    valve_data_filename = 'valve_data.csv'
    
    try:
        df_mass_flow = pd.read_csv(mass_flow_filename)
        df_valve = pd.read_csv(valve_data_filename)
        print("两个CSV文件均已成功加载。")
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e.filename}")
        print("请确保 'positive_mass_flow_data.csv' 和 'valve_data.csv' 文件都在正确的路径下。")
        return

    # 2. 提取绘图所需的数据列
    time_data = df_mass_flow['Time (s)']
    mass_flow_data = df_mass_flow['Positive mass flow rate at port B (g/s)']
    
    # --- 图一：时间 vs. 质量流率 ---
    print("\n正在生成图表一: Time vs. Mass Flow Rate...")
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, mass_flow_data, label='Mass Flow Rate at Port B', color='dodgerblue')
    plt.xlabel('Time (s)')
    plt.ylabel('Mass Flow Rate (g/s)')
    plt.title('Positive Mass Flow Rate at Port B vs. Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('time_vs_mass_flow_chart.png')
    print("图表一已成功保存为 'time_vs_mass_flow_chart.png'")

    # --- 图二：线性电压 vs. 质量流率 ---
    print("\n正在生成图表二: Voltage vs. Mass Flow Rate...")
    num_points = len(mass_flow_data)
    voltage_data_linear = np.linspace(5, 10, num_points)
    plt.figure(figsize=(10, 6))
    plt.plot(voltage_data_linear, mass_flow_data, label='Mass Flow Rate at Port B', color='crimson')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Mass Flow Rate (g/s)')
    plt.title('Positive Mass Flow Rate at Port B vs. Voltage (5V-10V)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('voltage_vs_mass_flow_chart.png')
    print("图表二已成功保存为 'voltage_vs_mass_flow_chart.png'")

    # --- 图三：验证图 - 叠加散点图 ---
    print("\n正在生成图表三: Validation Plot (Overlay)...")
    
    plt.figure(figsize=(12, 7))
    
    # 绘制原始的红色线条图
    plt.plot(voltage_data_linear, mass_flow_data, label='Port B Positive Mass Flow (Linear Voltage)', color='crimson', zorder=1)
    
    # 叠加来自 valve_data.csv 的绿色散点图用于验证
    plt.scatter(df_valve['Voltage (volt)'], df_valve['Mass flow rate (g/sec)'], 
                label='Validation Mass Flow (from valve_data.csv)', color='green', marker='o', s=50, zorder=2, alpha=0.8, edgecolor='black')

    # 添加图表的详细信息
    plt.xlabel('Voltage (V)', fontsize=12)
    plt.ylabel('Mass Flow Rate (g/s)', fontsize=12)
    plt.title('Validation: Overlay of Mass Flow Rates vs. Voltage', fontsize=16)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('validation_overlay_chart.png')
    print("图表三已成功保存为 'validation_overlay_chart.png'")
    
    print("\n所有图表已成功生成！")

# --- 运行主函数 ---
if __name__ == "__main__":
    main()

# --- 代码结束 ---
