#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控制器

连接模型和视图，处理用户交互
"""

from controllers.base_controller import BaseController
from views.main_window import MainWindow
from models.yolo_detection import YoloModel, CrackAnalysisModel
from threads.video_detection_thread import VideoDetectionThread, ImageDetectionThread, CrackAnalysisThread
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2


class MainController(BaseController):
    """主控制器类"""
    
    def __init__(self):
        """初始化主控制器"""
        super().__init__()
        self._main_window = None
        self._current_thread = None
        self._detection_model = None
        self._analysis_model = None
    
    def initialize(self):
        """初始化控制器"""
        # 创建并初始化视图
        self._main_window = MainWindow()
        self._main_window.initialize()
        
        # 创建并初始化模型
        self._detection_model = YoloModel()
        self._detection_model.initialize()
        
        self._analysis_model = CrackAnalysisModel()
        self._analysis_model.initialize()
        
        # 连接信号与槽
        self._connect_signals()
        
        print("主控制器初始化完成")
    
    def _connect_signals(self):
        """连接视图信号与控制器槽函数"""
        # 连接导航按钮信号
        self._main_window.home_btn.clicked.connect(self._on_home_btn_clicked)
        self._main_window.detection_btn.clicked.connect(self._on_detection_btn_clicked)
        self._main_window.traffic_btn.clicked.connect(self._on_traffic_btn_clicked)
        self._main_window.report_btn.clicked.connect(self._on_report_btn_clicked)
        
        # 连接裂缝检测页面的信号
        # 注意：需要在裂缝检测页面创建后再连接
        
    def _on_home_btn_clicked(self):
        """首页总览按钮点击事件"""
        self._main_window.stacked_widget.setCurrentIndex(0)
        print("切换到首页总览")
    
    def _on_detection_btn_clicked(self):
        """裂缝检测按钮点击事件"""
        self._main_window.stacked_widget.setCurrentIndex(1)
        print("切换到裂缝检测")
        
        # 如果裂缝检测页面尚未初始化，进行初始化
        if not hasattr(self._main_window, 'detection_page') or not self._main_window.detection_page:
            self._initialize_detection_page()
    
    def _on_traffic_btn_clicked(self):
        """交通荷载按钮点击事件"""
        self._main_window.stacked_widget.setCurrentIndex(2)
        print("切换到交通荷载")
    
    def _on_report_btn_clicked(self):
        """评估报告按钮点击事件"""
        self._main_window.stacked_widget.setCurrentIndex(3)
        print("切换到评估报告")
    
    def _initialize_detection_page(self):
        """初始化裂缝检测页面"""
        try:
            # 从主窗口获取裂缝检测页面
            detection_page = self._main_window.stacked_widget.widget(1)
            
            # 添加裂缝检测页面的UI组件和功能
            # 注意：这里需要根据实际的裂缝检测页面设计进行实现
            
            # 示例：添加视频播放和控制组件
            print("裂缝检测页面初始化完成")
            
        except Exception as e:
            print(f"裂缝检测页面初始化失败: {e}")
    
    def start_video_detection(self, video_path):
        """开始视频检测
        
        Args:
            video_path: 视频文件路径
        """
        # 停止当前正在运行的线程
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.stop()
            self._current_thread.wait()
        
        # 创建新的视频检测线程
        self._current_thread = VideoDetectionThread(video_path)
        
        # 连接线程信号与槽
        self._current_thread.started_signal.connect(self._on_video_detection_started)
        self._current_thread.finished_signal.connect(self._on_video_detection_finished)
        self._current_thread.progress_signal.connect(self._on_video_detection_progress)
        self._current_thread.result_signal.connect(self._on_video_detection_result)
        self._current_thread.error_signal.connect(self._on_video_detection_error)
        self._current_thread.frame_processed_signal.connect(self._on_video_frame_processed)
        
        # 启动线程
        self._current_thread.start()
    
    def start_image_detection(self, image_path):
        """开始图像检测
        
        Args:
            image_path: 图像文件路径
        """
        # 停止当前正在运行的线程
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.stop()
            self._current_thread.wait()
        
        # 创建新的图像检测线程
        self._current_thread = ImageDetectionThread(image_path)
        
        # 连接线程信号与槽
        self._current_thread.started_signal.connect(self._on_image_detection_started)
        self._current_thread.finished_signal.connect(self._on_image_detection_finished)
        self._current_thread.result_signal.connect(self._on_image_detection_result)
        self._current_thread.error_signal.connect(self._on_image_detection_error)
        
        # 启动线程
        self._current_thread.start()
    
    def start_crack_analysis(self, detection_result):
        """开始裂缝分析
        
        Args:
            detection_result: 裂缝检测结果
        """
        # 停止当前正在运行的线程
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.stop()
            self._current_thread.wait()
        
        # 创建新的裂缝分析线程
        self._current_thread = CrackAnalysisThread(detection_result)
        
        # 连接线程信号与槽
        self._current_thread.started_signal.connect(self._on_crack_analysis_started)
        self._current_thread.finished_signal.connect(self._on_crack_analysis_finished)
        self._current_thread.result_signal.connect(self._on_crack_analysis_result)
        self._current_thread.error_signal.connect(self._on_crack_analysis_error)
        
        # 启动线程
        self._current_thread.start()
    
    def pause_current_task(self):
        """暂停当前任务"""
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.pause()
    
    def resume_current_task(self):
        """恢复当前任务"""
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.resume()
    
    def stop_current_task(self):
        """停止当前任务"""
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.stop()
    
    def _on_video_detection_started(self):
        """视频检测开始事件"""
        print("视频检测开始")
        # 更新UI状态
        # self._main_window.set_detection_status("检测中")
    
    def _on_video_detection_finished(self):
        """视频检测完成事件"""
        print("视频检测完成")
        # 更新UI状态
        # self._main_window.set_detection_status("检测完成")
    
    def _on_video_detection_progress(self, progress):
        """视频检测进度更新事件"""
        print(f"视频检测进度: {progress}%")
        # 更新UI进度条
        # self._main_window.set_progress(progress)
    
    def _on_video_detection_result(self, result):
        """视频检测结果事件"""
        print(f"视频检测结果: {result}")
        # 显示检测结果
        # self._main_window.display_detection_result(result)
    
    def _on_video_detection_error(self, error_msg):
        """视频检测错误事件"""
        print(f"视频检测错误: {error_msg}")
        # 显示错误信息
        # self._main_window.show_error_message("检测错误", error_msg)
    
    def _on_video_frame_processed(self, frame, result):
        """视频帧处理完成事件"""
        # 更新视频显示
        # self._main_window.update_video_display(frame)
        pass
    
    def _on_image_detection_started(self):
        """图像检测开始事件"""
        print("图像检测开始")
    
    def _on_image_detection_finished(self):
        """图像检测完成事件"""
        print("图像检测完成")
    
    def _on_image_detection_result(self, result):
        """图像检测结果事件"""
        print(f"图像检测结果: {result}")
        # 显示检测结果图像
        if result and "processed_image" in result:
            processed_image = result["processed_image"]
            self._display_image(processed_image, self._main_window.detection_page.result_label)
    
    def _on_image_detection_error(self, error_msg):
        """图像检测错误事件"""
        print(f"图像检测错误: {error_msg}")
    
    def _on_crack_analysis_started(self):
        """裂缝分析开始事件"""
        print("裂缝分析开始")
    
    def _on_crack_analysis_finished(self):
        """裂缝分析完成事件"""
        print("裂缝分析完成")
    
    def _on_crack_analysis_result(self, result):
        """裂缝分析结果事件"""
        print(f"裂缝分析结果: {result}")
        # 显示分析结果
        # self._main_window.display_analysis_result(result)
    
    def _on_crack_analysis_error(self, error_msg):
        """裂缝分析错误事件"""
        print(f"裂缝分析错误: {error_msg}")
    
    def _display_image(self, image, label):
        """在标签上显示图像
        
        Args:
            image: 要显示的图像（numpy数组，BGR格式）
            label: PyQt5标签组件
        """
        try:
            # 将BGR格式转换为RGB格式
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 创建QImage对象
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 创建QPixmap对象并缩放以适应标签大小
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 在标签上显示图像
            label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"显示图像失败: {e}")
    
    def show_main_window(self):
        """显示主窗口"""
        if self._main_window:
            self._main_window.show()
    
    def release(self):
        """释放资源"""
        # 停止当前线程
        if self._current_thread and self._current_thread.is_running:
            self._current_thread.stop()
            self._current_thread.wait()
        
        # 释放模型资源
        if self._detection_model:
            self._detection_model.release()
        
        if self._analysis_model:
            self._analysis_model.release()
        
        print("主控制器资源已释放")
