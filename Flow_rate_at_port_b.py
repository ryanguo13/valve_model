import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- 代码开始 ---

def main():
    """
    主函数，用于加载数据并生成两个独立的图表。
    """
    # --- 数据加载 ---
    # 1. 读取您指定的CSV文件。
    csv_filename = 'positive_mass_flow_data.csv'
    try:
        df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        print(f"错误: 文件 '{csv_filename}' 未找到。")
        print("请确保文件名正确，并且文件与脚本在同一个文件夹中。")
        return

    # 2. 提取需要绘图的数据列
    time_data = df['Time (s)']
    mass_flow_data = df['Positive mass flow rate at port B (g/s)']
    
    print("数据加载成功，开始生成图表...")
    print("=" * 50)

    # --- 图一：时间 vs. 质量流率 (您的原始代码) ---
    print("正在生成图表一: Time vs. Mass Flow Rate...")
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, mass_flow_data, label='Mass Flow Rate at Port B', color='dodgerblue')
    plt.xlabel('Time (s)')
    plt.ylabel('Mass Flow Rate (g/s)')
    plt.title('Positive Mass Flow Rate at Port B vs. Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 将图表保存为 'time_vs_mass_flow_chart.png'
    plt.savefig('time_vs_mass_flow_chart.png')
    print("图表一已成功保存为 'time_vs_mass_flow_chart.png'")
    # plt.show() # 在这个环境中，我们只保存文件而不直接显示

    # --- 图二：电压 vs. 质量流率 (您要求的新增图表) ---
    print("\n正在生成图表二: Voltage vs. Mass Flow Rate...")
    
    # 1. 根据流量数据的点数，生成一个从5到10的线性电压序列
    num_points = len(mass_flow_data)
    voltage_data = np.linspace(5, 10, num_points)

    # 2. 创建图表
    plt.figure(figsize=(10, 6))
    plt.plot(voltage_data, mass_flow_data, label='Mass Flow Rate at Port B', color='crimson')

    # 3. 添加图表的详细信息 (全英文)
    plt.xlabel('Voltage (V)')
    plt.ylabel('Mass Flow Rate (g/s)')
    plt.title('Positive Mass Flow Rate at Port B vs. Voltage (5V-10V)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 4. 保存图表为图片文件
    plt.savefig('voltage_vs_mass_flow_chart.png')
    print("图表二已成功保存为 'voltage_vs_mass_flow_chart.png'")
    # plt.show()
    
    print("\n所有图表已成功生成！")

# --- 运行主函数 ---
if __name__ == "__main__":
    main()

# --- 代码结束 ---
