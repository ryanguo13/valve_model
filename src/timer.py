# coding=utf-8
import ctypes
import os
import time

class Timer:
    """使用Linux内核时钟的精确定时器类"""
    CLOCK_MONOTONIC = 1
    CLOCK_MONOTONIC_RAW = 4

    class Timespec(ctypes.Structure):
        _fields_ = [
            ('tv_sec', ctypes.c_long),
            ('tv_nsec', ctypes.c_long)
        ]

    def __init__(self):
        # 尝试加载不同的库名以提高兼容性
        try:
            self.librt = ctypes.CDLL('librt.so.1', use_errno=True)
        except OSError:
            try:
                self.librt = ctypes.CDLL('librt.so', use_errno=True)
            except OSError:
                self.librt = ctypes.CDLL('libc.so.6', use_errno=True)
                print("Using libc.so.6 for timer functions")
        
        # 设置函数参数和返回类型
        self.librt.clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(self.Timespec)]
        self.librt.clock_gettime.restype = ctypes.c_int
        
        # 初始化timespec结构体
        self.ts = self.Timespec()
        self._start_time = self.get_raw_time()
        
    def get_raw_time(self):
        """获取原始时间"""
        if self.librt.clock_gettime(self.CLOCK_MONOTONIC_RAW, ctypes.byref(self.ts)) != 0:
            errno = ctypes.get_errno()
            raise OSError(errno, os.strerror(errno))
        return self.ts.tv_sec + self.ts.tv_nsec * 1e-9
        
    def get_time(self):
        """获取相对于开始时间的时间差（秒）"""
        return self.get_raw_time() - self._start_time
        
    def busy_wait(self, target_time):
        """忙等待直到目标时间"""
        target_absolute = self._start_time + target_time
        while self.get_raw_time() < target_absolute:
            pass 