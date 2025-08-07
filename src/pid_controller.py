# coding=utf-8
import time
import numpy as np

class PIDController:
    """基础PID控制器"""
    def __init__(self, kp=1.0, ki=0.0, kd=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0
        self.last_time = time.time()
    
    def compute(self, setpoint, measured_value):
        current_time = time.time()
        dt = current_time - self.last_time
        
        # 防止dt过小导致计算异常
        if dt < 0.001:
            dt = 0.001
            
        error = setpoint - measured_value
        
        # 计算积分项
        self.integral += error * dt
        
        # 计算微分项
        derivative = (error - self.previous_error) / dt
        
        # 计算PID各项
        p_term = self.kp * error
        i_term = self.ki * self.integral
        d_term = self.kd * derivative
        
        # 总输出
        output = p_term + i_term + d_term
        
        # 保存当前误差和时间供下次计算使用
        self.previous_error = error
        self.last_time = current_time
        
        return output, error, p_term, i_term, d_term
    
    def reset(self):
        self.previous_error = 0
        self.integral = 0
        self.last_time = time.time()

class FuzzyPID:
    """模糊PID控制器"""
    def __init__(self, kp_base=0.11, ki_base=0.1, kd_base=0.05):
        self.kp_base = kp_base
        self.ki_base = ki_base  # 使用非零积分增益
        self.kd_base = kd_base
        
        # Base PID controller
        self.pid = PIDController(kp=kp_base, ki=ki_base, kd=kd_base)
        
        # 前一个值用于计算变化率
        self.prev_error = 0
        self.prev_time = time.time()
        self.current_phase = "init"  # 阶段标记
        
        # 积分限幅以防积分饱和
        self.integral_cap = 15.0
        
    def fuzzy_inference(self, error, error_rate):
        """改进的模糊推理以调整PID参数"""
        # 将误差和误差变化率标准化到[-1,1]范围
        norm_error = max(-1, min(1, error / 50.0))
        norm_error_rate = max(-1, min(1, error_rate / 20.0))
        
        # 分段计算隶属度函数
        
        # 误差大小隶属度: 小(S)、中(M)、大(L)
        error_S = max(0, min(1, 1 - abs(norm_error) * 2.5)) 
        error_M = max(0, min(1, 1 - abs(abs(norm_error) - 0.5) * 2.5))
        error_L = max(0, min(1, (abs(norm_error) - 0.4) * 2.5))
        
        # 误差变化率隶属度: 慢(S)、中(M)、快(F)
        rate_S = max(0, min(1, 1 - abs(norm_error_rate) * 2.5))
        rate_M = max(0, min(1, 1 - abs(abs(norm_error_rate) - 0.5) * 2.5))
        rate_F = max(0, min(1, (abs(norm_error_rate) - 0.4) * 2.5))
        
        # 模糊规则:
        
        # Kp调整规则:
        # 1. 误差大 -> 增大Kp
        # 2. 误差小且变化率慢 -> 减小Kp
        # 3. 误差中等且变化率中等 -> 保持Kp
        kp_dec = error_S * rate_S
        kp_keep = error_M * rate_M
        kp_inc = error_L
        
        # Ki调整规则:
        # 1. 误差小且变化率慢 -> 增大Ki (消除稳态误差)
        # 2. 误差大或变化率快 -> 减小Ki (防止积分饱和)
        # 3. 误差中等 -> 保持Ki
        ki_dec = error_L + rate_F
        ki_keep = error_M
        ki_inc = error_S * rate_S
        
        # Kd调整规则:
        # 1. 误差变化率快 -> 增大Kd (抑制超调)
        # 2. 误差变化率慢且误差小 -> 减小Kd (减少高频噪声影响)
        # 3. 误差中等且变化率中等 -> 保持Kd
        kd_dec = error_S * rate_S
        kd_keep = error_M * rate_M
        kd_inc = rate_F
        
        # 解模糊化 - 采用加权平均法
        # 设定各规则的权重: 减小(0.7)、保持(1.0)、增大(1.3)
        kp_factor = (0.7 * kp_dec + 1.0 * kp_keep + 1.3 * kp_inc) / (kp_dec + kp_keep + kp_inc + 0.001)
        ki_factor = (0.7 * ki_dec + 1.0 * ki_keep + 1.3 * ki_inc) / (ki_dec + ki_keep + ki_inc + 0.001)
        kd_factor = (0.7 * kd_dec + 1.0 * kd_keep + 1.3 * kd_inc) / (kd_dec + kd_keep + kd_inc + 0.001)
        
        # 限制调整范围，防止过度调整
        kp_factor = max(0.7, min(1.5, kp_factor))
        ki_factor = max(0.5, min(2.0, ki_factor))
        kd_factor = max(0.8, min(1.5, kd_factor))
        
        # 应用于基础PID参数
        self.pid.kp = self.kp_base * kp_factor
        self.pid.ki = self.ki_base * ki_factor
        self.pid.kd = self.kd_base * kd_factor
        
        # 限制积分项，防止积分饱和
        self.pid.integral = max(-self.integral_cap, min(self.integral_cap, self.pid.integral))
        
        return self.pid.kp, self.pid.ki, self.pid.kd
        
    def compute(self, setpoint, measured_value):
        current_time = time.time()
        dt = current_time - self.prev_time
        dt = max(0.001, dt)  # 防止除零
        
        error = setpoint - measured_value
        error_rate = (error - self.prev_error) / dt
        
        # 确定当前阶段
        if setpoint > self.prev_error + 1:
            self.current_phase = "rising"
        elif setpoint < self.prev_error - 1:
            self.current_phase = "falling"
        else:
            self.current_phase = "holding"
        
        # 应用模糊推理
        kp, ki, kd = self.fuzzy_inference(error, error_rate)
        
        # 计算控制输出（包含各项分量）
        output, error, p_term, i_term, d_term = self.pid.compute(setpoint, measured_value)
        
        # 更新前一个值
        self.prev_error = error
        self.prev_time = current_time
        
        return output, error, kp, ki, kd, self.current_phase, p_term, i_term, d_term 