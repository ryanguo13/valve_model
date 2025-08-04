import pandas as pd
import matplotlib.pyplot as plt

# --- 代码开始 ---

# 1. 读取您保存的CSV文件
# 请确保文件名 'positive_mass_flow_data.csv' 和您的文件名一致
try:
    df = pd.read_csv('positive_mass_flow_data.csv')
except FileNotFoundError:
    print("Error: 'positive_mass_flow_data.csv' not found.")
    print("Please make sure the filename is correct and it is in the same folder as your Python script.")
    exit()

# 2. 提取需要绘图的数据列
time_data = df['Time (s)']
mass_flow_data = df['Positive mass flow rate at port B (g/s)']

# 3. 创建图表
plt.figure(figsize=(10, 6))
plt.plot(time_data, mass_flow_data, label='Mass Flow Rate at Port B')

# 4. 添加图表的详细信息 (全英文)
plt.xlabel('Time (s)')
plt.ylabel('Mass Flow Rate (g/s)')
plt.title('Positive Mass Flow Rate at Port B vs. Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# 5. 保存图表为图片文件
# 这行新代码会将图表保存为名为 'mass_flow_rate_chart.png' 的文件
# 您也可以更改文件名或格式，例如 'my_chart.jpg' 或 'my_chart.pdf'
plt.savefig('mass_flow_rate_chart.png')

# 6. 显示图表
plt.show()

# --- 代码结束 ---