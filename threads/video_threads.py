#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO视频检测线程

实现基于QThread的视频检测线程，支持实时视频流处理和YOLO目标检测
"""

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage
from threads.base_thread import BaseThread
from models.yolo_detection import YoloModel


class YOLOThread(BaseThread):
    """YOLO视频检测线程类"""
    
    # 自定义信号定义
    change_pixmap_signal = pyqtSignal(QImage)  # 发送处理好的图像给UI显示
    stats_signal = pyqtSignal(dict)  # 发送检测到的统计数据
    
    def __init__(self, video_path=0, model_path='best.pt'):
        """初始化YOLO视频检测线程
        
        Args:
            video_path: 视频文件路径或摄像头ID（默认0）
            model_path: YOLO模型文件路径（默认使用best.pt）
        """
        super().__init__()
        self._video_path = video_path
        self._model_path = model_path
        self._yolo_model = None
        self._cap = None
        self._frame_count = 0
        self._detection_stats = {}
    
    def _run(self):
        """执行YOLO视频检测任务"""
        try:
            # 初始化YoloModel
            try:
                self._yolo_model = YoloModel(self._model_path)
                self._yolo_model.initialize()
                if not self._yolo_model.is_initialized:
                    error_msg = "YOLO检测模型初始化失败"
                    self.stats_signal.emit({"error": error_msg})
                    return
            except FileNotFoundError:
                # 模型文件不存在时发送错误信号
                error_msg = f"YOLO检测模型初始化失败: [Errno 2] No such file or directory: '{self._model_path}'"
                self.stats_signal.emit({"error": error_msg})
                return
            except Exception as e:
                # 其他模型加载错误
                error_msg = f"YOLO检测模型初始化失败: {str(e)}"
                self.stats_signal.emit({"error": error_msg})
                return
            
            # 打开视频文件或摄像头
            self._cap = cv2.VideoCapture(self._video_path)
            if not self._cap.isOpened():
                error_msg = f"无法打开视频源: {self._video_path}"
                self.stats_signal.emit({"error": error_msg})
                return
            
            # 处理视频帧
            self._process_video_frames()
            
        finally:
            # 释放资源
            if self._cap is not None:
                self._cap.release()
            if self._yolo_model is not None:
                self._yolo_model.release()
    
    def _process_video_frames(self):
        """处理视频帧并进行YOLO检测"""
        while self._is_running:
            # 检查是否暂停
            self._wait_for_resume()
            
            # 读取视频帧
            ret, frame = self._cap.read()
            if not ret:
                break  # 视频处理完毕
            
            self._frame_count += 1
            
            # 使用YoloModel进行推理
            annotated_frame, result = self._yolo_model.process_image(frame)
            
            # 更新检测统计数据
            self._update_detection_stats(result)
            
            # 将OpenCV的BGR格式转换为Qt的RGB格式
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            
            # 创建QImage对象
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 缩放图像以适应UI显示（保持宽高比）
            scaled_q_image = q_image.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 发送信号
            self.change_pixmap_signal.emit(scaled_q_image)
            self.stats_signal.emit(self._detection_stats.copy())
            
            # 更新进度
            progress = min(int((self._frame_count / 1000) * 100), 100)  # 模拟进度，实际可以根据视频总帧数计算
            self._update_progress(progress)
    
    def _update_detection_stats(self, result):
        """更新检测统计数据
        
        Args:
            result: YoloModel检测结果
        """
        # 初始化统计字典
        self._detection_stats = {}
        
        # 统计各类别目标数量
        detected_cracks = result.get("detected_cracks", [])
        class_name = "crack"
        self._detection_stats[class_name] = len(detected_cracks)
        
        # 添加总目标数量
        self._detection_stats['total'] = len(detected_cracks)
        
        # 添加当前帧号
        self._detection_stats['frame'] = self._frame_count
        
        # 添加其他统计信息
        stats = result.get("stats", {})
        for key, value in stats.items():
            self._detection_stats[key] = value
