# 阀门控制系统 (Valve Control System)

一个基于Python的实时阀门控制系统，用于精确控制球阀位置，包含压力传感器数据采集和视频记录功能。

## 项目结构

```
valve_model/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── timer.py                 # 高精度定时器模块
│   ├── pressure_sensor.py       # 压力传感器模块
│   ├── frame_storage.py         # 帧数据存储模块
│   ├── pid_controller.py        # PID控制器模块
│   ├── camera_controller.py     # 相机控制器模块
│   ├── experiment_runner.py     # 实验运行器模块
│   ├── data_processor.py        # 数据处理模块
│   └── main.py                  # 主程序入口
├── run_experiment.py            # 实验启动脚本
├── requirements.txt             # 依赖包列表
└── README.md                   # 项目文档
```

## 功能特性

### 核心功能
- **实时位置控制**: 使用模糊PID控制器精确控制球阀位置
- **高精度定时**: 基于Linux内核时钟的微秒级定时器
- **压力监测**: 集成3通道压力传感器数据采集
- **视频记录**: 自动记录84秒实验视频（8400帧）
- **数据可视化**: 自动生成10种不同的数据图表

### 技术特点
- **模块化设计**: 代码分为8个独立模块，易于维护和扩展
- **实时性能**: 10ms控制周期，支持实时优先级调度
- **多线程架构**: 相机采集和控制计算并行执行
- **数据完整性**: 自动保存CSV数据和生成图表

## 安装依赖

### 1. 安装Python依赖包

```bash
pip install -r requirements.txt
```

### 2. 安装相机SDK

请从官方渠道获取并安装相机SDK (mvsdk)。

### 3. 硬件连接

确保以下硬件正确连接：
- 工业相机 (支持mvsdk)
- 压力传感器 (ADS1015 ADC)
- PWM输出设备
- 树莓派或其他Linux系统

## 使用方法

### 快速启动

```bash
python run_experiment.py
```

### 模块化运行

```bash
python -m src.main
```

### 实验流程

1. **启动程序**: 运行启动脚本
2. **相机初始化**: 程序自动检测和初始化相机
3. **等待开始**: 按Enter键开始84秒实验
4. **自动执行**: 程序自动执行控制实验
5. **数据保存**: 实验完成后自动保存数据和图表
6. **视频生成**: 自动生成实验视频文件

## 输出文件

实验完成后会在指定目录生成以下文件：

### 数据文件
- `control_data_YYYYMMDD_HHMMSS.csv` - 主要实验数据
- `phase_data_YYYYMMDD_HHMMSS.txt` - 控制阶段数据

### 图表文件
1. `1_position_tracking_*.png` - 位置跟踪图
2. `2_error_*.png` - 误差图
3. `3_control_output_*.png` - 控制输出图
4. `4_P_term_*.png` - 比例项输出图
5. `5_I_term_*.png` - 积分项输出图
6. `6_D_term_*.png` - 微分项输出图
7. `7_A0_pressure_calibrated_*.png` - A0压力传感器图
8. `8_A1_pressure_calibrated_*.png` - A1压力传感器图
9. `9_A2_pressure_calibrated_*.png` - A2压力传感器图
10. `10_timing_jitter_*.png` - 时间抖动图

### 视频文件
- `control_experiment_YYYYMMDD_HHMMSS.mp4` - 实验视频

## 模块说明

### Timer (timer.py)
高精度定时器，基于Linux内核时钟实现微秒级定时。

### PressureSensor (pressure_sensor.py)
压力传感器控制模块，支持3通道ADC读取和校准。

### FrameStorage (frame_storage.py)
帧数据存储模块，支持实时压缩存储和视频生成。

### PIDController (pid_controller.py)
PID控制器模块，包含基础PID和模糊PID两种实现。

### CameraController (camera_controller.py)
相机控制模块，负责图像采集和球位置检测。

### ExperimentRunner (experiment_runner.py)
实验运行器，协调各个模块执行控制实验。

### DataProcessor (data_processor.py)
数据处理模块，负责数据保存和图表生成。

## 配置参数

### 实验参数
- 实验时长: 84秒
- 控制周期: 10ms
- 轨迹周期: 28秒
- 预期数据点: 8400个

### 控制参数
- 基础Kp: 0.11
- 基础Ki: 0.1
- 基础Kd: 0.05
- 积分限幅: ±15.0

### 硬件参数
- PWM频率: 3000Hz
- 相机分辨率: 640×480
- 压力传感器范围: 0-10 Bar

## 故障排除

### 常见问题

1. **相机初始化失败**
   - 检查相机连接
   - 确认mvsdk已正确安装
   - 检查相机权限

2. **压力传感器读取错误**
   - 检查I2C连接
   - 确认ADS1015地址设置
   - 检查电源供应

3. **PWM输出异常**
   - 检查树莓派硬件PWM支持
   - 确认GPIO引脚配置
   - 检查权限设置

4. **内存不足**
   - 减少最大帧数设置
   - 降低图像质量
   - 增加系统内存

### 性能优化

1. **实时性能**
   - 使用CPU亲和性绑定
   - 启用FIFO调度
   - 锁定内存防止交换

2. **数据存储**
   - 使用压缩存储帧数据
   - 预分配数组减少内存分配
   - 禁用垃圾回收

## 开发说明

### 添加新功能

1. 在相应模块中添加新类或方法
2. 在`src/__init__.py`中导出新组件
3. 在`main.py`中集成新功能
4. 更新文档和测试

### 代码规范

- 使用UTF-8编码
- 遵循PEP 8代码风格
- 添加详细的文档字符串
- 使用类型提示（可选）

## 许可证

本项目仅供学术研究使用。

## 联系方式

如有问题或建议，请联系项目维护者。
