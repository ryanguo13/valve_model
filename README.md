# 阀门数据分析项目

这个项目包含了从实验表格中提取的阀门特性数据，以及用于分析的Python脚本。

## 文件说明

- `valve_data.csv`: 从实验表格中提取的阀门数据，包含以下列：
  - `Voltage (volt)`: 输入电压 (V)
  - `Spool Pos. (mm)`: 阀芯位置 (mm)
  - `Orifice Area (mm^2)`: 孔口面积 (mm²)
  - `Mass flow rate (g/sec)`: 质量流量 (g/s)
  - `Cal. Vol. flow rate (l/min)`: 计算体积流量 (l/min)
  - `Exp. Vol. flow rate (l/min)`: 实验体积流量 (l/min)

- `analyze_valve_data.py`: Python分析脚本，提供以下功能：
  - 数据加载和基本统计
  - 绘制各种关系图表
  - 模型精度分析
  - 线性区域识别

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行分析

```bash
python analyze_valve_data.py
```

## 分析功能

1. **数据概览**: 显示数据基本信息和统计摘要
2. **关系图表**: 生成4个子图显示不同参数间的关系
3. **精度分析**: 计算计算值与实验值的相对误差
4. **线性分析**: 识别线性工作区域并计算相关参数

## 输出文件

- `valve_analysis.png`: 包含4个子图的分析图表
- 控制台输出: 包含详细的分析结果和统计信息

## 数据特点

- 电压范围: 5.0V - 9.875V
- 阀芯位置范围: 0mm - 1.95mm
- 流量范围: 0 l/min - 100 l/min
- 数据点数量: 40个测量点

## 注意事项

- 数据在电压8.75V后达到饱和状态
- 计算流量与实验流量有良好的一致性
- 线性工作区域主要在电压5.0V-8.75V之间 