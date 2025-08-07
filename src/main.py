# coding=utf-8
import atexit
import signal
import sys
from threading import Thread
from .camera_controller import CameraController
from .experiment_runner import ExperimentRunner
from .data_processor import DataProcessor
from .frame_storage import FrameStorage
from .pressure_sensor import PressureSensor

def signal_handler(signum, frame):
    """信号处理函数"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    """主程序入口"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建各个组件
    camera_controller = CameraController()
    experiment_runner = ExperimentRunner()
    data_processor = DataProcessor()
    
    # 初始化帧存储器
    save_path = "/home/pi/Downloads/Xiaohui/Test_py/Xiaohui_camera_test/7_1_Dynamic_PID/6.4_test"
    try:
        frame_storage = FrameStorage(
            save_path=save_path,
            max_frames=8400  # 84秒 × 100fps (10ms一帧)
        )
        print("帧存储器初始化成功，准备记录84秒实验视频")
    except Exception as e:
        print(f"帧存储器初始化失败: {e}")
        frame_storage = None
    
    # 初始化压力传感器
    try:
        pressure_sensor = PressureSensor(channels=[0, 1, 2])
        print("压力传感器初始化成功")
    except Exception as e:
        print(f"压力传感器初始化失败: {e}")
        pressure_sensor = None
    
    # 注册程序退出时的回调函数，确保保存数据
    atexit.register(data_processor.save_data_and_plot, experiment_runner)
    
    # 初始化相机
    if not camera_controller.initialize_camera():
        print("相机初始化失败，程序退出")
        return
    
    capture_thread = None
    control_thread = None
    
    try:
        # 启动相机采集线程
        capture_thread = Thread(
            target=camera_controller.capture_frames, 
            args=(frame_storage, lambda: experiment_runner.experiment_running)
        )
        capture_thread.daemon = False  # 改为非守护线程，确保完成执行
        capture_thread.start()
        
        # 等待用户启动控制实验
        input("按Enter键开始84秒控制实验（将生成8400帧视频）...")
        
        # 启动控制实验线程
        control_thread = Thread(
            target=experiment_runner.run_control_experiment,
            args=(camera_controller, frame_storage, pressure_sensor)
        )
        control_thread.daemon = False  # 改为非守护线程，确保完成执行
        control_thread.start()

        # 等待控制实验完成
        print("等待84秒控制实验完成...")
        if control_thread:
            control_thread.join()  # 等待控制线程完成
            print("控制实验线程已完成")
        
        # 等待采集线程完成
        if capture_thread:
            capture_thread.join(timeout=10.0)  # 给采集线程10秒时间完成
            print("采集线程已完成")
        
        # 确保数据已保存
        if not experiment_runner.data_already_saved:
            print("开始保存实验数据...")
            data_processor.save_data_and_plot(experiment_runner)
        
        # 停止帧存储并创建视频
        if frame_storage:
            print("开始创建实验视频...")
            frame_storage.stop_recording()
            # 在主线程中创建视频，确保不被中断
            frame_storage.create_video(experiment_duration=84.0)
            print("视频创建完成！")
            
    except KeyboardInterrupt:
        print("Program interrupted by user")
        experiment_runner.experiment_running = False  # 停止实验
        
    except Exception as e:
        print(f"Program error: {e}")
        experiment_runner.experiment_running = False
        
    finally:
        print("开始清理资源...")
        
        # 标记实验结束
        experiment_runner.experiment_running = False
        
        # 等待线程安全结束
        if capture_thread and capture_thread.is_alive():
            print("等待采集线程结束...")
            capture_thread.join(timeout=5.0)
            
        if control_thread and control_thread.is_alive():
            print("等待控制线程结束...")
            control_thread.join(timeout=5.0)
            
        # 清理相机资源
        camera_controller.release_camera()

if __name__ == '__main__':
    main() 