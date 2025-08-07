# coding=utf-8
import Adafruit_ADS1x15

class PressureSensor:
    """压力传感器类"""
    def __init__(self, channels=[0, 1, 2]):
        # 初始化ADS1015 ADC
        self.adc = Adafruit_ADS1x15.ADS1015(
            address=0x48,  # 默认I2C地址
            busnum=1       # 树莓派I2C总线编号
        )
        # 设置增益 - 对应适当的电压范围
        self.GAIN = 4 
        
        # 要读取的通道列表（默认读A0、A1、A2）
        self.channels = channels
        self.channel_names = ['A0', 'A1', 'A2']
        
        # 定义电压和压力的转换参数
        self.MIN_ADC_VOLTAGE = 0.033  # 分压器输出的最小电压 (V)
        self.MAX_ADC_VOLTAGE = 3.3    # 分压器输出的最大电压 (V)
        self.MIN_SENSOR_VOLTAGE = 0.1 # 传感器输出的最小电压 (V)
        self.MAX_SENSOR_VOLTAGE = 10.0 # 传感器输出的最大电压 (V)
        self.MIN_PRESSURE = 0.0       # 最小压力 (Bar)
        self.MAX_PRESSURE = 10.0      # 最大压力 (Bar)
        
        # 校准参数 - 对应MATLAB代码中的校准公式
        # Sensor_1_P_calibrated = 1.011*Sensor_1_P_raw+0.02716; 
        # Sensor_2_P_calibrated = 1.007*Sensor_2_P_raw-0.007; 
        # Sensor_3_P_calibrated = 1.0048*Sensor_3_P_raw+0.0055;
        self.calibration_params = {
            0: {'slope': 1.011, 'offset': 0.02716},   # A0 对应 Sensor_1
            1: {'slope': 1.007, 'offset': -0.007},    # A1 对应 Sensor_2
            2: {'slope': 1.0048, 'offset': 0.0055}    # A2 对应 Sensor_3
        }

    def read_adc_voltage(self, channel):
        """读取指定通道的ADC电压值"""
        # 从指定通道读取电压值
        adc_value = self.adc.read_adc(channel, gain=self.GAIN, data_rate=3300)
        # ADS1015是12位ADC (0-4095)
        # 对于增益16，满量程为+/-0.256V，但我们实际使用的是0-0.256V的正电压部分
        # 因此，有效范围是0-2048
        voltage = adc_value * 1.024 / 2048
        return voltage

    def adc_to_sensor_voltage(self, adc_voltage):
        """将ADC读取的电压转换回传感器输出的原始电压"""
        # 使用线性映射将ADC电压(0.033-3.3V)映射回传感器电压(0.1-10V)
        sensor_voltage = ((adc_voltage - self.MIN_ADC_VOLTAGE) / 
                          (self.MAX_ADC_VOLTAGE - self.MIN_ADC_VOLTAGE) * 
                          (self.MAX_SENSOR_VOLTAGE - self.MIN_SENSOR_VOLTAGE) + 
                          self.MIN_SENSOR_VOLTAGE)
        return sensor_voltage

    def voltage_to_pressure(self, sensor_voltage):
        """将传感器电压转换为压力值"""
        # 线性映射：0.1-10V → 0-10 Bar
        pressure = ((sensor_voltage - self.MIN_SENSOR_VOLTAGE) / 
                    (self.MAX_SENSOR_VOLTAGE - self.MIN_SENSOR_VOLTAGE) * 
                    (self.MAX_PRESSURE - self.MIN_PRESSURE) + 
                    self.MIN_PRESSURE)
        return pressure

    def calibrate_pressure(self, raw_pressure, channel):
        """
        校准压力值
        raw_pressure: 原始压力值
        channel: 传感器通道 (0, 1, 2)
        返回校准后的压力值
        """
        if channel in self.calibration_params:
            slope = self.calibration_params[channel]['slope']
            offset = self.calibration_params[channel]['offset']
            calibrated_pressure = slope * raw_pressure + offset
            return calibrated_pressure
        else:
            # 如果没有校准参数，返回原始值
            return raw_pressure

    def read_all_channels(self):
        """读取所有配置的通道并转换数据"""
        result = []
        
        for channel in self.channels:
            adc_voltage = self.read_adc_voltage(channel)
            sensor_voltage = self.adc_to_sensor_voltage(adc_voltage)
            raw_pressure = self.voltage_to_pressure(sensor_voltage)
            calibrated_pressure = self.calibrate_pressure(raw_pressure, channel)
            result.append((adc_voltage, sensor_voltage, raw_pressure, calibrated_pressure))
        
        return result 