# coding=utf-8
import time
import gc
import os
import psutil
import numpy as np
from threading import Thread
from rpi_hardware_pwm import HardwarePWM
from .timer import Timer
from .pressure_sensor import PressureSensor
from .pid_controller import FuzzyPID

class ExperimentRunner:
    """实验运行器类"""
    def __init__(self):
        self.experiment_running = False
        self.data_already_saved = False
        
        # 数据记录用变量
        self.time_data = []
        self.setpoint_data = []
        self.position_data = []
        self.error_data = []
        self.output_data = []
        self.jitter_data = []
        
        # PID参数记录
        self.kp_data = []
        self.ki_data = []
        self.kd_data = []
        self.phase_data = []
        
        # PID各项输出记录
        self.p_term_data = []
        self.i_term_data = []
        self.d_term_data = []
        
        # 压力传感器数据记录
        self.pressure_a0_data = []
        self.pressure_a1_data = []
        self.pressure_a2_data = []
        
        # 实验参数
        self.cycle_time = 28.0
        self.DT = 0.01  # 固定的时间步长，10ms
        self.experiment_duration = 84.0  # 实验时长84秒，刚好3个周期
        self.expected_points = int(self.experiment_duration / self.DT)  # 预期数据点数：8400
        
        # 轨迹参数
        self.x_min = 0.0  # 轨迹的最小位置，单位mm
        self.x_max = 156.75  # 轨迹的最大位置，单位mm
        
    def set_realtime_priority(self):
        """使用纯Python设置实时优先级"""
        try:
            # 设置CPU亲和性到核心3
            current_process = psutil.Process()
            current_process.cpu_affinity([3])
            print("Process pinned to CPU core 3")
            
            # 尝试设置实时调度策略
            try:
                os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(99))
                print("Process set to FIFO scheduling with priority 99")
            except Exception as e:
                print(f"Failed to set FIFO scheduling: {e}")
            
            # 尝试内存锁定功能
            try:
                import resource
                if hasattr(resource, 'mlockall'):
                    resource.mlockall(resource.MCL_CURRENT | resource.MCL_FUTURE)
                    print("Memory locked to prevent swapping")
                else:
                    print("Memory locking not supported on this platform")
            except Exception as e:
                print("Memory locking not supported on this platform")
                
        except Exception as e:
            print(f"Failed to set real-time priority: {e}")
    
    def generate_setpoint_curve(self, t):
        """
        生成理想位移曲线，支持无限循环
        t: 当前时间(秒)
        返回: 期望位置(mm)
        """
        # 计算在周期内的时间点
        t_cycle = t % self.cycle_time
        
        # 定义周期内各阶段时间
        delay_start = 2.0    # 初始保持阶段
        rise_time = 10.0     # 上升阶段
        hold_time = 4.0      # 高位保持阶段
        fall_time = 10.0     # 下降阶段
        delay_end = 2.0      # 末尾保持阶段
        
        # 确保所有阶段时间之和等于周期时间
        assert abs(delay_start + rise_time + hold_time + fall_time + delay_end - self.cycle_time) < 1e-6, "阶段时间总和应等于周期时间"
        
        # 目标位移值
        X_max = self.x_max  # 使用函数参数
        
        # 根据周期内时间点确定输出值
        if t_cycle < delay_start:
            return self.x_min  # 初始延迟
        elif t_cycle < delay_start + rise_time:
            # 上升阶段，使用三次多项式平滑过渡
            progress = (t_cycle - delay_start) / rise_time
            smooth_progress = 3 * progress**2 - 2 * progress**3
            return self.x_min + (X_max - self.x_min) * smooth_progress
        elif t_cycle < delay_start + rise_time + hold_time:
            return X_max  # 高位保持
        elif t_cycle < delay_start + rise_time + hold_time + fall_time:
            # 下降阶段，使用三次多项式平滑过渡
            progress = (t_cycle - (delay_start + rise_time + hold_time)) / fall_time
            smooth_progress = 3 * progress**2 - 2 * progress**3
            return X_max - (X_max - self.x_min) * smooth_progress
        else:
            return self.x_min  # 末尾延迟
    
    def clear_data(self):
        """清理上次实验数据"""
        self.time_data.clear()
        self.setpoint_data.clear()
        self.position_data.clear()
        self.error_data.clear()
        self.output_data.clear()
        self.jitter_data.clear()
        self.kp_data.clear()
        self.ki_data.clear()
        self.kd_data.clear()
        self.phase_data.clear()
        self.p_term_data.clear()
        self.i_term_data.clear()
        self.d_term_data.clear()
        self.pressure_a0_data.clear()
        self.pressure_a1_data.clear()
        self.pressure_a2_data.clear()
    
    def preallocate_arrays(self):
        """预分配数据数组"""
        self.time_data = np.zeros(self.expected_points)
        self.setpoint_data = np.zeros(self.expected_points)
        self.position_data = np.zeros(self.expected_points)
        self.error_data = np.zeros(self.expected_points)
        self.output_data = np.zeros(self.expected_points)
        self.jitter_data = np.zeros(self.expected_points)
        self.kp_data = np.zeros(self.expected_points)
        self.ki_data = np.zeros(self.expected_points)
        self.kd_data = np.zeros(self.expected_points)
        self.phase_data = np.empty(self.expected_points, dtype='U10')  # 使用字符串存储阶段名称
        self.p_term_data = np.zeros(self.expected_points)
        self.i_term_data = np.zeros(self.expected_points)
        self.d_term_data = np.zeros(self.expected_points)
        self.pressure_a0_data = np.zeros(self.expected_points)
        self.pressure_a1_data = np.zeros(self.expected_points)
        self.pressure_a2_data = np.zeros(self.expected_points)
    
    def run_control_experiment(self, camera_controller, frame_storage=None, pressure_sensor=None):
        """进行控制实验的主要函数"""
        # 标记实验已开始
        self.experiment_running = True
        
        # 启动帧数据记录
        if frame_storage:
            frame_storage.start_recording()
        
        # 清理上次实验数据
        self.clear_data()
        
        # 禁用垃圾回收
        gc.disable()
        
        # 设置优先级
        self.set_realtime_priority()
        
        # 创建高精度定时器
        timer = Timer()
        
        # 初始化压力传感器
        if pressure_sensor is None:
            try:
                pressure_sensor = PressureSensor(channels=[0, 1, 2])
                print("压力传感器初始化成功")
            except Exception as e:
                print(f"压力传感器初始化失败: {e}")
                pressure_sensor = None
        
        # 预分配数据数组
        self.preallocate_arrays()
        
        # PWM设置
        pwm_channel = 2  # 从2_1_P_controller.py采用
        pwm_freq = 3000  # PWM频率Hz
        pwm = HardwarePWM(pwm_channel=pwm_channel, hz=pwm_freq, chip=2)
        pwm.start(0)  # 启动PWM，初始占空比为0
        print(f"PWM started on channel {pwm_channel}")
        
        # 创建实时动态PID控制器
        pid_controller = FuzzyPID(kp_base=0.11, ki_base=0.1, kd_base=0.05)
        
        try:
            # 实验开始时间
            print(f"Starting {self.experiment_duration}-second experiment with {self.expected_points} data points...")
            start_time = timer.get_time()
            prev_elapsed_time = 0
            
            # 控制循环 - 确保运行8400次（84秒）
            for i in range(self.expected_points):
                # 计算下一个采样时间点 - 这是关键部分，确保固定时间步长
                next_sample_time = start_time + (i * self.DT)
                
                # 以高精度等待到下一个采样时间
                timer.busy_wait(next_sample_time)
                
                # 获取当前时间
                current_time = timer.get_time()
                elapsed_time = current_time - start_time
                
                # 计算定时抖动
                actual_dt = elapsed_time - prev_elapsed_time if i > 0 else self.DT
                jitter_ms = (actual_dt - self.DT) * 1000  # 转换为毫秒
                prev_elapsed_time = elapsed_time
                
                # 获取当前小球位置
                current_position = camera_controller.get_ball_position()
                
                # 计算设定点 - 使用全局cycle_time变量
                setpoint = self.generate_setpoint_curve(elapsed_time)
                
                # 计算控制输出 - 使用FuzzyPID控制器，获取当前PID参数和各项分量
                output, error, current_kp, current_ki, current_kd, current_phase, p_term, i_term, d_term = pid_controller.compute(setpoint, current_position)
                
                # 限制输出电压在0-3.3V范围内
                output = max(0, min(output, 3.3))
                    
                # 将电压转换为PWM占空比 (0-3.3V -> 0-100%)
                duty_cycle = (output / 3.3) * 100
                
                # 设置PWM占空比
                pwm.change_duty_cycle(duty_cycle)
                
                # 读取压力传感器数据
                pressure_readings = [0.0, 0.0, 0.0]  # 默认值
                if pressure_sensor is not None:
                    try:
                        readings = pressure_sensor.read_all_channels()
                        # 提取校准后的压力值
                        pressure_readings = [reading[3] for reading in readings]  # reading[3]是校准后的压力值
                    except Exception as e:
                        if i % 100 == 0:  # 每100次循环打印一次错误，避免日志过多
                            print(f"压力传感器读取错误: {e}")
                
                # 记录数据
                self.time_data[i] = elapsed_time
                self.setpoint_data[i] = setpoint
                self.position_data[i] = current_position
                self.error_data[i] = error
                self.output_data[i] = output
                self.jitter_data[i] = jitter_ms
                self.kp_data[i] = current_kp
                self.ki_data[i] = current_ki
                self.kd_data[i] = current_kd
                self.phase_data[i] = current_phase
                self.p_term_data[i] = p_term
                self.i_term_data[i] = i_term
                self.d_term_data[i] = d_term
                self.pressure_a0_data[i] = pressure_readings[0]
                self.pressure_a1_data[i] = pressure_readings[1]
                self.pressure_a2_data[i] = pressure_readings[2]
                
                # 打印控制信息
                if i % 100 == 0:  # 每100个点打印一次
                    progress = (i / self.expected_points) * 100
                    cycles_completed = elapsed_time / self.cycle_time
                    print(f"Progress: {progress:.1f}% - Time: {elapsed_time:.2f}s ({cycles_completed:.2f} cycles), "
                          f"Phase: {current_phase}, Setpoint: {setpoint:.2f}mm, Position: {current_position:.2f}mm, "
                          f"Error: {error:.2f}mm, Kp: {current_kp:.2f}, Kd: {current_kd:.2f}, Output: {output:.2f}V")
                
        except KeyboardInterrupt:
            print("\nExperiment interrupted!")
        finally:
            # 停止PWM
            if 'pwm' in locals():
                pwm.stop()
                print("PWM stopped")
            
            # 重新启用垃圾回收
            gc.enable()
            
            # 标记实验结束
            self.experiment_running = False
            
            # 打印最终统计
            print(f"{self.experiment_duration}秒控制实验完成！总共运行了 {i+1} 次循环")
            cycles_completed = (i+1) * self.DT / self.cycle_time
            print(f"完成了 {cycles_completed:.2f} 个{self.cycle_time}秒周期") 