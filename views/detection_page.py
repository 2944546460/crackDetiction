#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
裂缝检测页面

实现裂缝检测的具体功能界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QGroupBox, QTextEdit, QSplitter
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2


class DetectionPage(QWidget):
    """裂缝检测页面"""
    
    def __init__(self):
        """初始化裂缝检测页面"""
        super().__init__()
        
        # 初始化状态变量
        self.current_file_path = None  # 当前选择的文件路径
        self.detection_mode = None  # 当前检测模式: 'image', 'video', 'camera'
        self.is_detecting = False  # 是否正在检测中
        self.detection_thread = None  # 检测线程
        self.original_image = None  # 原始图像数据
        
        self._init_ui()
        self._connect_signals()
    
    def _connect_signals(self):
        """连接按钮信号与槽函数"""
        self.image_btn.clicked.connect(self._on_image_clicked)
        self.video_btn.clicked.connect(self._on_video_clicked)
        self.camera_btn.clicked.connect(self._on_camera_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("裂缝检测")
        title_label.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; margin-bottom: 10px; }")
        main_layout.addWidget(title_label)
        
        # 创建文件选择区域
        file_section = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_section)
        
        self.image_btn = QPushButton("选择图像")
        self.video_btn = QPushButton("选择视频")
        self.camera_btn = QPushButton("摄像头检测")
        self.clear_btn = QPushButton("清除")
        
        # 设置按钮对象名称
        self.image_btn.setObjectName("image_btn")
        self.video_btn.setObjectName("video_btn")
        self.camera_btn.setObjectName("camera_btn")
        self.clear_btn.setObjectName("clear_btn")
        
        for btn in [self.image_btn, self.video_btn, self.camera_btn, self.clear_btn]:
            btn.setMinimumHeight(40)
            file_layout.addWidget(btn)
        
        main_layout.addWidget(file_section)
        
        # 创建显示区域
        display_splitter = QSplitter(Qt.Horizontal)
        
        # 原始图像显示区域
        original_group = QGroupBox("原始图像")
        original_layout = QVBoxLayout(original_group)
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setObjectName("image_display_label")
        self.original_label.setMinimumHeight(200)  # 降低最小高度，提高灵活性
        original_layout.addWidget(self.original_label)
        
        # 结果图像显示区域
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setObjectName("image_display_label")
        self.result_label.setMinimumHeight(200)  # 降低最小高度，提高灵活性
        result_layout.addWidget(self.result_label)
        
        display_splitter.addWidget(original_group)
        display_splitter.addWidget(result_group)
        display_splitter.setSizes([400, 400])
        
        main_layout.addWidget(display_splitter)
        
        # 创建控制区域
        control_section = QGroupBox("控制")
        control_layout = QHBoxLayout(control_section)
        
        self.start_btn = QPushButton("开始检测")
        self.pause_btn = QPushButton("暂停")
        self.stop_btn = QPushButton("停止")
        
        # 设置按钮对象名称
        self.start_btn.setObjectName("start_btn")
        self.pause_btn.setObjectName("pause_btn")
        self.stop_btn.setObjectName("stop_btn")
        
        for btn in [self.start_btn, self.pause_btn, self.stop_btn]:
            btn.setMinimumHeight(40)
            control_layout.addWidget(btn)
        
        main_layout.addWidget(control_section)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # 创建结果信息区域
        info_section = QGroupBox("检测信息")
        info_layout = QVBoxLayout(info_section)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)  # 设置为只读
        self.info_text.setMinimumHeight(100)  # 降低最小高度，提高灵活性
        info_layout.addWidget(self.info_text, 1)  # 设置伸缩因子，使信息框可以随窗口垂直伸缩
        
        main_layout.addWidget(info_section)
        
        # 移除硬编码样式，使用全局样式表
    
    def display_image(self, image, is_original=True):
        """显示图像
        
        Args:
            image: 要显示的图像（numpy数组，BGR格式）
            is_original: 是否为原始图像
        """
        try:
            if image is None:
                return
            
            # 将BGR格式转换为RGB格式
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 创建QImage对象
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 创建QPixmap对象并缩放以适应标签大小
            pixmap = QPixmap.fromImage(q_image)
            
            if is_original:
                label = self.original_label
            else:
                label = self.result_label
            
            # 计算缩放后的尺寸
            label_width = label.width()
            label_height = label.height()
            scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 在标签上显示图像
            label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"显示图像失败: {e}")
    
    def update_progress(self, progress):
        """更新进度条
        
        Args:
            progress: 进度值 (0-100)
        """
        self.progress_bar.setValue(progress)
    
    def update_info(self, info):
        """更新检测信息
        
        Args:
            info: 检测信息文本
        """
        self.info_text.append(info)
    
    def clear_all(self):
        """清除所有显示内容"""
        self.original_label.clear()
        self.result_label.clear()
        self.progress_bar.setValue(0)
        self.info_text.clear()
    
    def get_file_path(self, file_type="image"):
        """获取文件路径
        
        Args:
            file_type: 文件类型，"image"或"video"
            
        Returns:
            file_path: 选择的文件路径，如果未选择返回None
        """
        if file_type == "image":
            file_filter = "图像文件 (*.jpg *.jpeg *.png *.bmp *.tif)"
            caption = "选择图像文件"
        else:
            file_filter = "视频文件 (*.mp4 *.avi *.mov *.mkv)"
            caption = "选择视频文件"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, caption, "", file_filter
        )
        
        if file_path:
            return file_path
        return None
    
    def show_message(self, title, message):
        """显示消息框
        
        Args:
            title: 消息框标题
            message: 消息内容
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)
    
    def show_error(self, title, message):
        """显示错误消息框
        
        Args:
            title: 消息框标题
            message: 错误消息内容
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)
    
    def _on_image_clicked(self):
        """选择图像按钮点击事件"""
        # 打开文件选择对话框
        file_path = self.get_file_path("image")
        if file_path:
            try:
                # 读取图像
                image = cv2.imread(file_path)
                if image is not None:
                    # 显示原始图像
                    self.display_image(image, is_original=True)
                    
                    # 保存当前状态
                    self.current_file_path = file_path
                    self.detection_mode = "image"
                    self.original_image = image.copy()
                    
                    # 清除之前的检测结果
                    self.result_label.clear()
                    self.update_info(f"已选择图像文件: {file_path}")
                else:
                    self.show_error("错误", "无法读取图像文件")
            except Exception as e:
                self.show_error("错误", f"选择图像失败: {str(e)}")
    
    def _on_video_clicked(self):
        """选择视频按钮点击事件"""
        # 打开文件选择对话框
        file_path = self.get_file_path("video")
        if file_path:
            try:
                # 保存当前状态
                self.current_file_path = file_path
                self.detection_mode = "video"
                
                # 清除之前的图像显示
                self.original_label.clear()
                self.result_label.clear()
                
                # 更新信息
                self.update_info(f"已选择视频文件: {file_path}")
                
            except Exception as e:
                self.show_error("错误", f"选择视频失败: {str(e)}")
    
    def _on_camera_clicked(self):
        """摄像头检测按钮点击事件"""
        try:
            # 保存当前状态
            self.current_file_path = None
            self.detection_mode = "camera"
            
            # 清除之前的图像显示
            self.original_label.clear()
            self.result_label.clear()
            
            # 更新信息
            self.update_info("已选择摄像头检测模式")
            
        except Exception as e:
            self.show_error("错误", f"摄像头检测设置失败: {str(e)}")
    
    def _on_clear_clicked(self):
        """清除按钮点击事件"""
        try:
            # 停止当前检测线程
            if self.detection_thread and self.detection_thread.isRunning():
                self.detection_thread.stop()
                self.detection_thread.wait()
                self.detection_thread = None
            
            # 重置状态变量
            self.current_file_path = None
            self.detection_mode = None
            self.is_detecting = False
            self.original_image = None
            
            # 清除显示内容
            self.clear_all()
            
            # 更新信息
            self.update_info("已清除所有检测状态和结果")
            
        except Exception as e:
            self.show_error("错误", f"清除失败: {str(e)}")
    
    def _on_start_clicked(self):
        """开始检测按钮点击事件"""
        try:
            # 检查是否已选择检测模式
            if not self.detection_mode:
                self.show_error("错误", "请先选择检测模式（图像、视频或摄像头）")
                return
            
            # 检查是否正在检测中
            if self.is_detecting:
                self.show_error("错误", "检测已在进行中")
                return
            
            # 根据检测模式创建相应的线程
            from threads.video_detection_thread import ImageDetectionThread, VideoDetectionThread
            
            if self.detection_mode == "image":
                # 图像检测
                if not self.current_file_path:
                    self.show_error("错误", "请先选择图像文件")
                    return
                
                self.detection_thread = ImageDetectionThread(self.original_image)
                self.detection_thread.result_signal.connect(self._on_image_detection_finished)
                
            elif self.detection_mode == "video":
                # 视频检测
                if not self.current_file_path:
                    self.show_error("错误", "请先选择视频文件")
                    return
                
                self.detection_thread = VideoDetectionThread(self.current_file_path)
                self.detection_thread.frame_processed_signal.connect(self._on_video_frame_processed)
                self.detection_thread.result_signal.connect(self._on_video_detection_finished)
                
            elif self.detection_mode == "camera":
                # 摄像头检测
                self.detection_thread = VideoDetectionThread(0)  # 0表示默认摄像头
                self.detection_thread.frame_processed_signal.connect(self._on_video_frame_processed)
                self.detection_thread.result_signal.connect(self._on_video_detection_finished)
            
            # 连接进度信号
            self.detection_thread.progress_signal.connect(self.update_progress)
            
            # 设置检测状态
            self.is_detecting = True
            
            # 启动线程
            self.detection_thread.start()
            
            # 更新信息
            self.update_info(f"开始{self.detection_mode}检测...")
            
        except Exception as e:
            self.show_error("错误", f"开始检测失败: {str(e)}")
    
    def _on_image_detection_finished(self, result):
        """图像检测完成信号处理"""
        try:
            # 获取检测结果
            processed_image = result.get("processed_image")
            detection_result = result.get("detection_result", {})
            
            if processed_image is not None:
                # 显示检测结果图像
                self.display_image(processed_image, is_original=False)
            
            # 显示检测统计信息
            stats = detection_result.get("stats", {})
            total = stats.get("total", 0)
            max_width = stats.get("max_width", 0)
            
            self.update_info(f"图像检测完成")
            self.update_info(f"裂缝数量: {total}")
            self.update_info(f"最大裂缝宽度: {max_width:.2f} 像素")
            
            # 更新全局状态
            from utils.global_state import global_state
            global_state.update_crack_data(total, max_width)
            
            # 重置检测状态
            self.is_detecting = False
            
        except Exception as e:
            self.show_error("错误", f"处理检测结果失败: {str(e)}")
    
    def _on_video_frame_processed(self, frame, result):
        """视频帧处理完成信号处理"""
        try:
            if frame is not None:
                # 显示处理后的帧
                self.display_image(frame, is_original=False)
            
            # 显示检测统计信息
            stats = result.get("stats", {})
            total = stats.get("total", 0)
            
            self.update_info(f"当前帧裂缝数量: {total}")
            
        except Exception as e:
            print(f"处理视频帧失败: {e}")
    
    def _on_video_detection_finished(self, result):
        """视频检测完成信号处理"""
        try:
            self.update_info("视频检测完成")
            
            # 重置检测状态
            self.is_detecting = False
            
        except Exception as e:
            self.show_error("错误", f"处理视频检测结果失败: {str(e)}")
    
    def _on_pause_clicked(self):
        """暂停按钮点击事件"""
        try:
            # 检查是否正在检测中
            if not self.is_detecting:
                self.show_error("错误", "当前没有正在进行的检测")
                return
            
            # 检查检测模式是否支持暂停
            if self.detection_mode == "image":
                self.show_error("提示", "图像检测不支持暂停操作")
                return
            
            # 检查检测线程是否存在
            if not self.detection_thread or not self.detection_thread.isRunning():
                self.show_error("错误", "检测线程不存在或未运行")
                return
            
            # 调用线程的暂停方法
            self.detection_thread.pause()
            
            # 更新信息
            self.update_info("检测已暂停")
            
        except Exception as e:
            self.show_error("错误", f"暂停检测失败: {str(e)}")
    
    def _on_stop_clicked(self):
        """停止按钮点击事件"""
        try:
            # 检查是否正在检测中
            if not self.is_detecting:
                self.show_error("错误", "当前没有正在进行的检测")
                return
            
            # 检查检测线程是否存在
            if not self.detection_thread:
                self.show_error("错误", "检测线程不存在")
                return
            
            # 停止线程
            if self.detection_thread.isRunning():
                self.detection_thread.stop()
                self.detection_thread.wait()
            
            # 重置线程引用
            self.detection_thread = None
            
            # 重置检测状态
            self.is_detecting = False
            
            # 更新信息
            self.update_info("检测已停止")
            
        except Exception as e:
            self.show_error("错误", f"停止检测失败: {str(e)}")
