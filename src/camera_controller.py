# coding=utf-8
import mvsdk
import cv2
import numpy as np
import math
import time
from threading import Lock

class CameraController:
    """相机控制器类"""
    def __init__(self):
        self.hCamera = None
        self.pFrameBuffer = None
        self.frame_buffer_size = None
        self.global_ball_position = 0.0
        self.position_lock = Lock()
        
    def ensure_camera_closed(self):
        """在程序启动时确保相机设备已经关闭"""
        try:
            # 尝试枚举所有相机设备
            DevList = mvsdk.CameraEnumerateDevice()
            if len(DevList) == 0:
                print("No camera found!")
                return
                
            # 获取第一个相机的信息
            DevInfo = DevList[0]
            
            # 检查相机设备是否已经打开 (通过简单的操作并捕获错误)
            try:
                # 尝试打开并立即关闭，如果打开成功说明之前没有打开
                hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
                if hCamera:
                    print("Successfully initialized camera, closing...")
                    mvsdk.CameraUnInit(hCamera)
            except mvsdk.CameraException as e:
                if e.error_code == -18:  # 设备已经打开
                    print("Camera is already open, attempting to close it...")
                    
                    # 这里需要更直接的方法来关闭相机，但SDK通常不提供
                    # 我们可以尝试通过系统命令关闭占用相机的进程
                    try:
                        import os
                        if os.name == 'posix':  # Linux
                            # 查找并终止所有可能占用相机的进程
                            os.system("pkill -f python.*320_Junhua.py")
                            print("Terminated potential camera-using processes")
                            time.sleep(2)  # 给系统时间释放资源
                        else:
                            print("Camera is in use and automatic release is only supported on Linux")
                    except Exception as e:
                        print(f"Failed to release camera: {e}")
        except Exception as e:
            print(f"Error checking camera state: {e}")
    
    def initialize_camera(self):
        """初始化相机"""
        # 确保相机设备已关闭
        self.ensure_camera_closed()
        
        # 枚举相机
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            return False
            
        for i, DevInfo in enumerate(DevList):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        i = 0 if nDev == 1 else int(input("Select camera: "))
        DevInfo = DevList[i]

        # 打开相机
        try:
            self.hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message))
            return False

        # 获取相机特性描述
        cap = mvsdk.CameraGetCapability(self.hCamera)

        # 设置ISP输出MONO8格式
        mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        
        # 相机模式切换成软触发模式
        mvsdk.CameraSetTriggerMode(self.hCamera, 1)  # 设置为软触发模式
        print("Camera set to software trigger mode")

        # 手动曝光设置
        mvsdk.CameraSetAeState(self.hCamera, 0)
        mvsdk.CameraSetExposureTime(self.hCamera, 4 * 1000)  # 曝光时间4ms
        mvsdk.CameraSetAnalogGain(self.hCamera, 100)          # 模拟增益
        mvsdk.CameraSetGamma(self.hCamera, 250)               # 伽马
        mvsdk.CameraSetContrast(self.hCamera, 200)            # 对比度

        # 设置分辨率
        resolution = mvsdk.CameraGetImageResolution(self.hCamera)
        resolution.iIndex = 0  # 使用索引0对应640*480分辨率
        mvsdk.CameraSetImageResolution(self.hCamera, resolution)

        # 设置高帧率模式
        mvsdk.CameraSetFrameSpeed(self.hCamera, 2)           # 2:高速模式

        # 让SDK内部取图线程开始工作
        mvsdk.CameraPlay(self.hCamera)

        # 计算buffer大小并申请buffer
        self.frame_buffer_size = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(self.frame_buffer_size, 16)
        
        return True
    
    def pixel_to_physical(self, pixel_x, zero_pixel_x, scale_factor):
        """
        将像素坐标转换为物理坐标
        pixel_x: 像素坐标_320*240
        zero_pixel_x: 0点对应的像素坐标_320*240
        scale_factor: 比例系数 (mm/pixel)
        """
        return (pixel_x - zero_pixel_x) * scale_factor
    
    def capture_frames(self, frame_storage=None, experiment_running=None):
        """相机采集线程 - 移除显示相关功能，专注于位置检测和视频录制"""
        # ROI参数
        roi_x = 7
        roi_y = 220
        roi_width = 570
        roi_height = 43
        zero_pixel_x = 19.7  # 修改为X方向的零点
        scale_factor = 165/572  # 24mm/167pixel
        
        # 等待实验开始
        while not experiment_running:
            time.sleep(0.001)
        
        # 实验开始后，与控制循环同步，每10ms采集一帧
        experiment_start_time = time.time()
        frame_interval = 0.01  # 10ms间隔，与控制循环同步
        next_frame_time = experiment_start_time
        
        while experiment_running:
            try:
                # 等待到下一个预定的采集时间
                current_time = time.time()
                if current_time < next_frame_time:
                    time.sleep(max(0, next_frame_time - current_time))
                
                # 计算实验经过时间
                elapsed_time = time.time() - experiment_start_time
                
                # 如果实验时间超过84秒，停止采集
                if elapsed_time > 84.0:
                    break
                
                # 执行软触发采集一帧图像
                mvsdk.CameraClearBuffer(self.hCamera)  # 清空相机内部已缓存的所有帧
                mvsdk.CameraSoftTrigger(self.hCamera)  # 执行一次软触发
                
                # 取一帧图像，添加200ms超时
                pRawData, FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 200)
                mvsdk.CameraImageProcess(self.hCamera, pRawData, self.pFrameBuffer, FrameHead)
                
                # 将图像数据转换成OpenCV格式
                frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.pFrameBuffer)
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = frame.reshape(FrameHead.iHeight, FrameHead.iWidth)
                
                # 保存原始帧到帧存储器 - 优先处理以减少实时计算负担
                if frame_storage and frame_storage.recording:
                    frame_storage.add_frame(frame, elapsed_time)
                
                # ROI裁剪用于球位置检测
                roi = frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
                
                # 反二值化
                _, binary = cv2.threshold(roi, 128, 255, cv2.THRESH_BINARY_INV)
                
                # 移除小于500像素的连通区域
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
                
                # 处理连通区域
                for i in range(1, num_labels):
                    if stats[i, cv2.CC_STAT_AREA] >= 500:
                        # 获取轮廓mask
                        contour_mask = (labels == i).astype(np.uint8) * 255
        
                        # 查找轮廓并计算最小包围圆
                        contours, _ = cv2.findContours(contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            # 计算最小包围圆
                            (x, y), radius = cv2.minEnclosingCircle(contours[0])
            
                            # 计算圆度过滤非圆形物体
                            perimeter = cv2.arcLength(contours[0], True)
                            if perimeter > 0:
                                circularity = 4 * math.pi * stats[i, cv2.CC_STAT_AREA] / (perimeter ** 2)
                                if 0.40 < circularity < 1.15:  # 圆度阈值范围
                                    # 找到小球，计算质心并更新位置
                                    centroid_x = centroids[i][0]
                                    pixel_x = centroid_x + roi_x  # 转换回原图坐标系
                                    physical_x = self.pixel_to_physical(pixel_x, zero_pixel_x, scale_factor)
                                    
                                    # 更新全局球位置
                                    with self.position_lock:
                                        self.global_ball_position = physical_x
            
                # 释放图像缓冲区
                mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)
                
                # 计算下一帧时间
                next_frame_time += frame_interval
                
            except mvsdk.CameraException as e:
                if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:  # 忽略超时错误
                    print("Camera error({}): {}".format(e.error_code, e.message))
                # 调整下一帧时间，避免因错误导致时间偏移
                next_frame_time = time.time() + frame_interval
            except Exception as e:
                print(f"Error in capture loop: {e}")
                next_frame_time = time.time() + frame_interval
    
    def get_ball_position(self):
        """获取当前球位置"""
        with self.position_lock:
            return self.global_ball_position
    
    def release_camera(self):
        """释放相机资源"""
        try:
            if self.hCamera:
                mvsdk.CameraStop(self.hCamera)
                mvsdk.CameraUnInit(self.hCamera)
            if self.pFrameBuffer:
                mvsdk.CameraAlignFree(self.pFrameBuffer)
            print("Camera resources released")
        except Exception as e:
            print(f"Error releasing camera resources: {e}") 