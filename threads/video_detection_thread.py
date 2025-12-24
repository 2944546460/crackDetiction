#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频检测线程

用于处理视频文件的裂缝检测任务，支持暂停、恢复和停止操作
"""

from threads.base_thread import BaseThread
from models.yolo_detection import YoloModel
from models.base_model import VideoProcessingModel
import cv2
import time


class VideoDetectionThread(BaseThread):
    """视频检测线程类"""
    
    def __init__(self, video_path, model_path=None):
        """初始化视频检测线程
        
        Args:
            video_path: 视频文件路径
            model_path: YOLO模型文件路径
        """
        super().__init__()
        self._video_path = video_path
        self._model_path = model_path
        self._detection_model = None
        self._video_model = None
        self._frame_count = 0
        self._total_frames = 0
    
    def _run(self):
        """执行视频检测任务"""
        try:
            # 初始化YOLO检测模型
            self._detection_model = YoloModel(self._model_path)
            self._detection_model.initialize()
            
            # 初始化视频处理模型
            self._video_model = VideoProcessingModel()
            if not self._video_model.open_video(self._video_path):
                raise Exception(f"无法打开视频文件: {self._video_path}")
            
            self._total_frames = self._video_model.total_frames
            
            # 处理视频帧
            self._process_video_frames()
            
        finally:
            # 释放资源
            if self._detection_model:
                self._detection_model.release()
            if self._video_model:
                self._video_model.close_video()
    
    def _process_video_frames(self):
        """处理视频帧"""
        frame_interval = 1  # 处理间隔（每隔几帧处理一次）
        processed_frames = 0
        start_time = time.time()
        
        while self._is_running:
            # 检查是否暂停
            self._wait_for_resume()
            
            # 获取下一帧
            frame = self._video_model.get_frame()
            if frame is None:
                break  # 视频处理完毕
            
            self._frame_count += 1
            
            # 每隔指定间隔处理一帧
            if self._frame_count % frame_interval == 0:
                # 进行裂缝检测
                processed_frame, result = self._detection_model.process_video_frame(frame)
                
                # 发送处理结果信号
                self.frame_processed_signal.emit(processed_frame, result)
                
                processed_frames += 1
                
                # 更新进度
                progress = int((self._frame_count / self._total_frames) * 100)
                self._update_progress(progress)
                
                # 计算并显示FPS
                if processed_frames % 10 == 0:  # 每处理10帧显示一次FPS
                    elapsed_time = time.time() - start_time
                    fps = processed_frames / elapsed_time if elapsed_time > 0 else 0
                    print(f"视频检测FPS: {fps:.2f}")
        
        # 视频处理完成，发送最终结果
        final_result = {
            "video_path": self._video_path,
            "total_frames": self._total_frames,
            "processed_frames": processed_frames,
            "processing_time": time.time() - start_time
        }
        self.result_signal.emit(final_result)


class ImageDetectionThread(BaseThread):
    """图像检测线程类，用于处理单张图像的裂缝检测"""
    
    def __init__(self, image_path, model_path=None):
        """初始化图像检测线程
        
        Args:
            image_path: 图像文件路径或numpy数组
            model_path: YOLO模型文件路径
        """
        super().__init__()
        self._image_path = image_path
        self._model_path = model_path
        self._detection_model = None
    
    def _run(self):
        """执行图像检测任务"""
        try:
            # 初始化YOLO检测模型
            self._detection_model = YoloModel(self._model_path)
            self._detection_model.initialize()
            
            # 处理图像
            processed_image, result = self._detection_model.process_image(self._image_path)
            
            # 发送处理结果信号
            final_result = {
                "original_image": self._image_path,
                "processed_image": processed_image,
                "detection_result": result
            }
            self.result_signal.emit(final_result)
            
        finally:
            # 释放资源
            if self._detection_model:
                self._detection_model.release()


class CrackAnalysisThread(BaseThread):
    """裂缝分析线程类，用于对检测结果进行进一步分析"""
    
    def __init__(self, detection_result):
        """初始化裂缝分析线程
        
        Args:
            detection_result: 裂缝检测结果
        """
        super().__init__()
        self._detection_result = detection_result
    
    def _run(self):
        """执行裂缝分析任务"""
        from models.yolo_detection import CrackAnalysisModel
        
        try:
            # 初始化裂缝分析模型
            analysis_model = CrackAnalysisModel()
            analysis_model.initialize()
            
            # 进行裂缝分析
            analysis_result = analysis_model.analyze_cracks(self._detection_result)
            
            # 发送分析结果信号
            final_result = {
                "detection_result": self._detection_result,
                "analysis_result": analysis_result
            }
            self.result_signal.emit(final_result)
            
        finally:
            # 释放资源
            if 'analysis_model' in locals():
                analysis_model.release()
