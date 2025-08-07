#!/usr/bin/env python3
# coding=utf-8
"""
阀门控制系统实验启动脚本
Valve Control System Experiment Launcher

使用方法:
python run_experiment.py

或者:
python -m src.main
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """启动实验"""
    try:
        # 导入并运行主程序
        from src.main import main as run_main
        run_main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖包已安装")
        print("依赖包包括: mvsdk, numpy, opencv-python, matplotlib, psutil, rpi_hardware_pwm, Adafruit_ADS1x15")
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 