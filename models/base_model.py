#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础模型类

提供模型层的通用功能和接口定义
"""

import os
import cv2
import numpy as np
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """模型基类，定义了所有模型应实现的接口"""
    
    def __init__(self):
        """初始化基础模型"""
        self._is_initialized = False
    
    @abstractmethod
    def initialize(self):
        """初始化模型，加载必要的资源"""
        pass
    
    @abstractmethod
    def process(self, data):
        """处理数据的核心方法"""
        pass
    
    @abstractmethod
    def release(self):
        """释放资源"""
        pass
    
    @property
    def is_initialized(self):
        """检查模型是否已初始化"""
        return self._is_initialized
    
    def _set_initialized(self, value):
        """设置初始化状态"""
        self._is_initialized = value


class ImageProcessingModel(BaseModel):
    """图像处理模型基类"""
    
    def __init__(self):
        """初始化图像处理模型"""
        super().__init__()
    
    @abstractmethod
    def process_image(self, image):
        """处理单张图像
        
        Args:
            image: 输入图像，可以是numpy数组（BGR格式）或图像文件路径
            
        Returns:
            processed_image: 处理后的图像（numpy数组，BGR格式）
            result: 处理结果数据（如检测到的目标、裂缝信息等）
        """
        pass
    
    def read_image(self, image_input):
        """读取图像，支持文件路径或numpy数组
        
        Args:
            image_input: 图像输入，可以是文件路径或numpy数组
            
        Returns:
            image: 读取的图像（numpy数组，BGR格式）
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"图像文件不存在: {image_input}")
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"无法读取图像文件: {image_input}")
        elif isinstance(image_input, np.ndarray):
            image = image_input.copy()
        else:
            raise TypeError(f"不支持的图像输入类型: {type(image_input)}")
        
        return image
    
    def save_image(self, image, output_path):
        """保存图像到文件
        
        Args:
            image: 要保存的图像（numpy数组，BGR格式）
            output_path: 输出文件路径
            
        Returns:
            bool: 保存成功返回True，否则返回False
        """
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            return cv2.imwrite(output_path, image)
        except Exception as e:
            print(f"保存图像失败: {e}")
            return False


class VideoProcessingModel(BaseModel):
    """视频处理模型基类"""
    
    def __init__(self):
        """初始化视频处理模型"""
        super().__init__()
        self._cap = None
        self._fps = 0
        self._total_frames = 0
        self._width = 0
        self._height = 0
    
    @abstractmethod
    def process_frame(self, frame):
        """处理单帧视频
        
        Args:
            frame: 输入帧（numpy数组，BGR格式）
            
        Returns:
            processed_frame: 处理后的帧（numpy数组，BGR格式）
            result: 处理结果数据
        """
        pass
    
    def open_video(self, video_path):
        """打开视频文件
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            bool: 打开成功返回True，否则返回False
        """
        try:
            if self._cap is not None:
                self.close_video()
            
            self._cap = cv2.VideoCapture(video_path)
            if not self._cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            # 获取视频信息
            self._fps = self._cap.get(cv2.CAP_PROP_FPS)
            self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            return True
        except Exception as e:
            print(f"打开视频失败: {e}")
            self._cap = None
            return False
    
    def get_frame(self):
        """获取下一帧视频
        
        Returns:
            frame: 视频帧（numpy数组，BGR格式），如果没有更多帧返回None
        """
        if self._cap is None or not self._cap.isOpened():
            return None
        
        ret, frame = self._cap.read()
        if not ret:
            return None
        
        return frame
    
    def get_frame_at_position(self, position):
        """获取指定位置的视频帧
        
        Args:
            position: 帧位置（0到1之间的浮点数，表示视频进度）
            
        Returns:
            frame: 视频帧（numpy数组，BGR格式），如果失败返回None
        """
        if self._cap is None or not self._cap.isOpened():
            return None
        
        try:
            # 计算帧索引
            frame_index = int(position * self._total_frames)
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = self._cap.read()
            if not ret:
                return None
            return frame
        except Exception as e:
            print(f"获取指定位置帧失败: {e}")
            return None
    
    def close_video(self):
        """关闭视频文件"""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
    
    @property
    def fps(self):
        """获取视频帧率"""
        return self._fps
    
    @property
    def total_frames(self):
        """获取视频总帧数"""
        return self._total_frames
    
    @property
    def width(self):
        """获取视频宽度"""
        return self._width
    
    @property
    def height(self):
        """获取视频高度"""
        return self._height
