# coding=utf-8
import os
import time
import numpy as np
import matplotlib.pyplot as plt

class DataProcessor:
    """数据处理类"""
    def __init__(self, save_path="/home/pi/Downloads/Xiaohui/Test_py/Xiaohui_camera_test/7_1_Dynamic_PID/6.4_test"):
        self.save_path = save_path
        self.data_already_saved = False
        
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)
    
    def save_data_and_plot(self, experiment_runner):
        """保存记录的数据到CSV文件并生成曲线图"""
        # 检查是否已经保存过
        if self.data_already_saved:
            print("Data already saved")
            return
        
        # 检查是否有数据需要保存
        if len(experiment_runner.time_data) == 0 or (isinstance(experiment_runner.time_data, list) and not experiment_runner.time_data):
            print("No data to save")
            return
        
        try:
            # 裁剪数据到有效长度 (如果数组是预分配的)
            if isinstance(experiment_runner.time_data, np.ndarray) and len(experiment_runner.time_data) > 0:
                # 找到最后一个非零时间索引
                valid_indices = np.where(experiment_runner.time_data > 0)[0]
                if len(valid_indices) > 0:
                    last_valid_idx = valid_indices[-1] + 1
                    time_data_trimmed = experiment_runner.time_data[:last_valid_idx]
                    setpoint_data_trimmed = experiment_runner.setpoint_data[:last_valid_idx]
                    position_data_trimmed = experiment_runner.position_data[:last_valid_idx]
                    error_data_trimmed = experiment_runner.error_data[:last_valid_idx]
                    output_data_trimmed = experiment_runner.output_data[:last_valid_idx]
                    jitter_data_trimmed = experiment_runner.jitter_data[:last_valid_idx]
                    
                    # 裁剪PID参数数据
                    kp_data_trimmed = experiment_runner.kp_data[:last_valid_idx]
                    ki_data_trimmed = experiment_runner.ki_data[:last_valid_idx]
                    kd_data_trimmed = experiment_runner.kd_data[:last_valid_idx]
                    phase_data_trimmed = experiment_runner.phase_data[:last_valid_idx]
                    
                    # 裁剪PID各项数据
                    p_term_data_trimmed = experiment_runner.p_term_data[:last_valid_idx]
                    i_term_data_trimmed = experiment_runner.i_term_data[:last_valid_idx]
                    d_term_data_trimmed = experiment_runner.d_term_data[:last_valid_idx]
                    
                    # 裁剪压力传感器数据
                    pressure_a0_data_trimmed = experiment_runner.pressure_a0_data[:last_valid_idx]
                    pressure_a1_data_trimmed = experiment_runner.pressure_a1_data[:last_valid_idx]
                    pressure_a2_data_trimmed = experiment_runner.pressure_a2_data[:last_valid_idx]
                    
                    print(f"保存了 {last_valid_idx} 个数据点，实际实验时长: {time_data_trimmed[-1]:.2f}s")
                else:
                    print("No valid data found")
                    return
            else:
                # 如果是列表或其他格式，直接使用
                time_data_trimmed = experiment_runner.time_data
                setpoint_data_trimmed = experiment_runner.setpoint_data
                position_data_trimmed = experiment_runner.position_data
                error_data_trimmed = experiment_runner.error_data
                output_data_trimmed = experiment_runner.output_data
                jitter_data_trimmed = experiment_runner.jitter_data
                kp_data_trimmed = experiment_runner.kp_data
                ki_data_trimmed = experiment_runner.ki_data
                kd_data_trimmed = experiment_runner.kd_data
                phase_data_trimmed = experiment_runner.phase_data
                p_term_data_trimmed = experiment_runner.p_term_data
                i_term_data_trimmed = experiment_runner.i_term_data
                d_term_data_trimmed = experiment_runner.d_term_data
                pressure_a0_data_trimmed = experiment_runner.pressure_a0_data
                pressure_a1_data_trimmed = experiment_runner.pressure_a1_data
                pressure_a2_data_trimmed = experiment_runner.pressure_a2_data
                
            # 创建数据数组 (不包含phase_data因为它是字符串，增加压力传感器数据)
            data = np.column_stack((
                time_data_trimmed,
                setpoint_data_trimmed,
                position_data_trimmed,
                error_data_trimmed,
                output_data_trimmed,
                jitter_data_trimmed,
                kp_data_trimmed,
                ki_data_trimmed,
                kd_data_trimmed,
                p_term_data_trimmed,
                i_term_data_trimmed,
                d_term_data_trimmed,
                pressure_a0_data_trimmed,  # 新增
                pressure_a1_data_trimmed,  # 新增
                pressure_a2_data_trimmed   # 新增
            ))
            
            # 保存到CSV文件
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_path, f"control_data_{timestamp}.csv")
            
            # 添加表头并保存（更新表头包含压力传感器数据）
            header = "Time(s),x_set(mm),x_meas(mm),e_x(mm),Output(V),Jitter(ms),Kp,Ki,Kd,P_term(V),I_term(V),D_term(V),Pressure_A0(Bar),Pressure_A1(Bar),Pressure_A2(Bar)"
            np.savetxt(filename, data, delimiter=',', header=header, comments='')
            
            # 单独保存phase数据（因为它是字符串）
            phase_filename = os.path.join(self.save_path, f"phase_data_{timestamp}.txt")
            with open(phase_filename, 'w') as f:
                for phase in phase_data_trimmed:
                    f.write(f"{phase}\n")
            
            print(f"Data saved to {filename}")
            print(f"Phase data saved to {phase_filename}")
            
            # 生成图表
            self._generate_plots(time_data_trimmed, setpoint_data_trimmed, position_data_trimmed,
                               error_data_trimmed, output_data_trimmed, jitter_data_trimmed,
                               p_term_data_trimmed, i_term_data_trimmed, d_term_data_trimmed,
                               pressure_a0_data_trimmed, pressure_a1_data_trimmed, pressure_a2_data_trimmed,
                               timestamp)
            
            # 标记数据已保存
            self.data_already_saved = True
            
        except Exception as e:
            print(f"Error saving data and plotting: {e}")
    
    def _generate_plots(self, time_data, setpoint_data, position_data, error_data, output_data, 
                       jitter_data, p_term_data, i_term_data, d_term_data,
                       pressure_a0_data, pressure_a1_data, pressure_a2_data, timestamp):
        """生成所有图表"""
        
        # 图1: 设定值和实际位置
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, setpoint_data, 'r-', linewidth=2, label='x_set (Setpoint)')
        plt.plot(time_data, position_data, 'b-', linewidth=1.5, label='x_meas (Measured Position)')
        plt.title('Ball Position: Setpoint vs Measured')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (mm)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        position_plot_filename = os.path.join(self.save_path, f"1_position_tracking_{timestamp}.png")
        plt.savefig(position_plot_filename)
        plt.close()
        print(f"Position tracking plot saved to {position_plot_filename}")
        
        # 图2: 误差 e_x = x_set - x_meas
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, error_data, 'g-', linewidth=1.5, label='e_x = x_set - x_meas')
        plt.title('Position Error')
        plt.xlabel('Time (s)')
        plt.ylabel('Error e_x (mm)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        error_plot_filename = os.path.join(self.save_path, f"2_error_{timestamp}.png")
        plt.savefig(error_plot_filename)
        plt.close()
        print(f"Error plot saved to {error_plot_filename}")
        
        # 图3: 控制输出 (转换为0-10V) - 只有这个图需要转换
        plt.figure(figsize=(12, 6))
        scaled_output = np.array(output_data) * (10.0 / 3.3)  # 将0-3.3V转换为0-10V
        plt.plot(time_data, scaled_output, 'k-', linewidth=1.5, label='Control Output (0-10V)')
        plt.title('Control Output Voltage')
        plt.xlabel('Time (s)')
        plt.ylabel('Output Voltage (V)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        output_plot_filename = os.path.join(self.save_path, f"3_control_output_{timestamp}.png")
        plt.savefig(output_plot_filename)
        plt.close()
        print(f"Control output plot saved to {output_plot_filename}")
        
        # 图4: P项 (e_x * kp) - 保持原始电压范围
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, p_term_data, 'r-', linewidth=1.5, label='P_term = e_x × Kp')
        plt.title('Proportional Term Output')
        plt.xlabel('Time (s)')
        plt.ylabel('P_term (V)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        p_term_plot_filename = os.path.join(self.save_path, f"4_P_term_{timestamp}.png")
        plt.savefig(p_term_plot_filename)
        plt.close()
        print(f"P term plot saved to {p_term_plot_filename}")
        
        # 图5: I项 (∫(e_x) * ki) - 保持原始电压范围
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, i_term_data, 'b-', linewidth=1.5, label='I_term = ∫(e_x) × Ki')
        plt.title('Integral Term Output')
        plt.xlabel('Time (s)')
        plt.ylabel('I_term (V)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        i_term_plot_filename = os.path.join(self.save_path, f"5_I_term_{timestamp}.png")
        plt.savefig(i_term_plot_filename)
        plt.close()
        print(f"I term plot saved to {i_term_plot_filename}")
        
        # 图6: D项 (de_x/dt * kd) - 保持原始电压范围
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, d_term_data, 'm-', linewidth=1.5, label='D_term = d(e_x)/dt × Kd')
        plt.title('Derivative Term Output')
        plt.xlabel('Time (s)')
        plt.ylabel('D_term (V)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        d_term_plot_filename = os.path.join(self.save_path, f"6_D_term_{timestamp}.png")
        plt.savefig(d_term_plot_filename)
        plt.close()
        print(f"D term plot saved to {d_term_plot_filename}")
        
        # 新增图7: A0压力传感器校准后数据
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, pressure_a0_data, 'c-', linewidth=1.5, label='A0 Pressure (Calibrated)')
        plt.title('A0 Pressure Sensor - Calibrated')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (Bar)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        pressure_a0_plot_filename = os.path.join(self.save_path, f"7_A0_pressure_calibrated_{timestamp}.png")
        plt.savefig(pressure_a0_plot_filename)
        plt.close()
        print(f"A0 pressure plot saved to {pressure_a0_plot_filename}")
        
        # 新增图8: A1压力传感器校准后数据
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, pressure_a1_data, 'orange', linewidth=1.5, label='A1 Pressure (Calibrated)')
        plt.title('A1 Pressure Sensor - Calibrated')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (Bar)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        pressure_a1_plot_filename = os.path.join(self.save_path, f"8_A1_pressure_calibrated_{timestamp}.png")
        plt.savefig(pressure_a1_plot_filename)
        plt.close()
        print(f"A1 pressure plot saved to {pressure_a1_plot_filename}")
        
        # 新增图9: A2压力传感器校准后数据
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, pressure_a2_data, 'purple', linewidth=1.5, label='A2 Pressure (Calibrated)')
        plt.title('A2 Pressure Sensor - Calibrated')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (Bar)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        pressure_a2_plot_filename = os.path.join(self.save_path, f"9_A2_pressure_calibrated_{timestamp}.png")
        plt.savefig(pressure_a2_plot_filename)
        plt.close()
        print(f"A2 pressure plot saved to {pressure_a2_plot_filename}")
        
        # 时间抖动图 (保留原有功能)
        plt.figure(figsize=(12, 6))
        plt.plot(time_data, jitter_data, 'orange', linewidth=1, label='Timing Jitter')
        if len(jitter_data) > 0:
            max_jitter = np.max(np.abs(jitter_data))
            avg_jitter = np.mean(np.abs(jitter_data))
            plt.title(f'Timing Jitter - Max: {max_jitter:.3f} ms, Avg: {avg_jitter:.3f} ms')
        else:
            plt.title('Timing Jitter')
        plt.xlabel('Time (s)')
        plt.ylabel('Jitter (ms)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        jitter_plot_filename = os.path.join(self.save_path, f"10_timing_jitter_{timestamp}.png")
        plt.savefig(jitter_plot_filename)
        plt.close()
        print(f"Timing jitter plot saved to {jitter_plot_filename}") 