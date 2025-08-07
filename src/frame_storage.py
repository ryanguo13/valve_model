# coding=utf-8
import os
import time
import cv2
import numpy as np

class FrameStorage:
    def __init__(self, save_path, max_frames=8400):
        """
        初始化帧存储器
        save_path: 保存路径
        max_frames: 最大帧数
        """
        self.save_path = save_path
        self.max_frames = max_frames
        self.frames = []  # 存储帧数据
        self.timestamps = []  # 存储时间戳
        self.frame_count = 0
        self.recording = False
        
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)
        
        print(f"帧存储器初始化完成，最大帧数: {max_frames}")
    
    def start_recording(self):
        """开始录制"""
        self.recording = True
        self.frames.clear()
        self.timestamps.clear()
        self.frame_count = 0
        print("开始帧数据记录")
    
    def add_frame(self, frame, timestamp):
        """添加一帧数据"""
        if not self.recording or self.frame_count >= self.max_frames:
            return
            
        try:
            # 直接存储原始帧数据（灰度图）
            if frame.ndim == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 压缩帧以节省内存
            _, compressed_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            self.frames.append(compressed_frame)
            self.timestamps.append(timestamp)
            self.frame_count += 1
            
            # 每1000帧打印一次进度
            if self.frame_count % 1000 == 0:
                print(f"帧数据记录进度: {self.frame_count}/{self.max_frames} 帧, 时长: {timestamp:.1f}s")
                
        except Exception as e:
            print(f"保存帧数据时出错: {e}")
    
    def stop_recording(self):
        """停止录制"""
        if not self.recording:
            return
            
        self.recording = False
        print(f"帧数据记录完成！总共记录了 {self.frame_count} 帧")
    
    def create_video(self, experiment_duration=84.0):
        """后处理创建视频"""
        if self.frame_count == 0:
            print("没有帧数据，无法创建视频")
            return
            
        print("开始后处理创建视频...")
        
        try:
            # 生成视频文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            video_filename = os.path.join(self.save_path, f"control_experiment_{timestamp}.mp4")
            
            # 计算视频参数
            actual_duration = self.timestamps[-1] - self.timestamps[0] if len(self.timestamps) > 1 else experiment_duration
            target_fps = self.frame_count / experiment_duration  # 目标帧率，使视频时长为experiment_duration
            
            print(f"视频参数: {self.frame_count} 帧, 目标时长: {experiment_duration:.1f}s, 帧率: {target_fps:.2f}fps")
            
            # 解压第一帧以获取尺寸信息
            first_frame = cv2.imdecode(self.frames[0], cv2.IMREAD_GRAYSCALE)
            frame_height, frame_width = first_frame.shape
            
            # 创建VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                video_filename, 
                fourcc, 
                target_fps, 
                (frame_width, frame_height)
            )
            
            if not video_writer.isOpened():
                print("无法创建视频写入器")
                return
            
            # 处理每一帧
            for i, (compressed_frame, timestamp) in enumerate(zip(self.frames, self.timestamps)):
                try:
                    # 解压帧
                    frame = cv2.imdecode(compressed_frame, cv2.IMREAD_GRAYSCALE)
                    
                    # 转换为彩色以便添加文字信息
                    frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    
                    # 添加时间戳信息
                    cv2.putText(frame_color, f"Time: {timestamp:.2f}s", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # 添加进度信息
                    progress = (i / self.frame_count) * 100
                    cv2.putText(frame_color, f"Progress: {progress:.1f}%", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # 写入视频
                    video_writer.write(frame_color)
                    
                    # 每100帧显示进度
                    if (i + 1) % 100 == 0:
                        video_progress = ((i + 1) / self.frame_count) * 100
                        print(f"视频处理进度: {video_progress:.1f}% ({i + 1}/{self.frame_count})")
                        
                except Exception as e:
                    print(f"处理第 {i} 帧时出错: {e}")
                    continue
            
            # 释放VideoWriter
            video_writer.release()
            
            print(f"视频创建完成！")
            print(f"视频已保存到: {video_filename}")
            
            # 验证视频文件
            if os.path.exists(video_filename):
                file_size = os.path.getsize(video_filename)
                print(f"视频文件大小: {file_size / 1024 / 1024:.1f} MB")
            
            # 清理内存中的帧数据
            self.frames.clear()
            self.timestamps.clear()
            print("已清理内存中的帧数据")
                
        except Exception as e:
            print(f"创建视频时出错: {e}") 