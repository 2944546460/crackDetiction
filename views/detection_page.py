#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
裂缝检测页面

实现裂缝检测的具体功能界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QGroupBox, QTextEdit, QSplitter,
    QInputDialog, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import cv2
import math
import os
from utils.global_state import global_state
from utils.logger import logger
from utils.config_manager import ConfigManager


class ClickableLabel(QLabel):
    """可点击并支持绘图的标签"""
    clicked = pyqtSignal(QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []
        self.is_calibration_mode = False
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        if self.is_calibration_mode and event.button() == Qt.LeftButton:
            self.clicked.emit(event.pos())
            if len(self.points) < 2:
                self.points.append(event.pos())
                self.update()
            else:
                self.points = [event.pos()]
                self.update()
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_calibration_mode and self.points:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
            
            # 画点
            for pt in self.points:
                painter.drawEllipse(pt, 3, 3)
            
            # 画线
            if len(self.points) == 2:
                painter.drawLine(self.points[0], self.points[1])
    
    def clear_calibration(self):
        self.points = []
        self.update()


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
        self.batch_btn.clicked.connect(self._on_batch_clicked)
        self.camera_btn.clicked.connect(self._on_camera_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        
        # 标定相关信号
        self.calib_btn.toggled.connect(self._on_calib_toggled)
        self.calib_reset_btn.clicked.connect(self._on_calib_reset_clicked)
        self.original_label.clicked.connect(self._on_label_clicked)
    
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
        self.batch_btn = QPushButton("批量处理")
        self.camera_btn = QPushButton("摄像头检测")
        self.clear_btn = QPushButton("清除")
        
        # 设置按钮对象名称
        self.image_btn.setObjectName("image_btn")
        self.video_btn.setObjectName("video_btn")
        self.batch_btn.setObjectName("batch_btn")
        self.camera_btn.setObjectName("camera_btn")
        self.clear_btn.setObjectName("clear_btn")
        
        for btn in [self.image_btn, self.video_btn, self.batch_btn, self.camera_btn, self.clear_btn]:
            btn.setMinimumHeight(40)
            file_layout.addWidget(btn)
        
        main_layout.addWidget(file_section)
        
        # 创建显示区域
        display_splitter = QSplitter(Qt.Horizontal)
        
        # 原始图像显示区域
        original_group = QGroupBox("原始图像")
        original_layout = QVBoxLayout(original_group)
        
        # 增加标定模式开关和操作按钮
        calibration_layout = QHBoxLayout()
        self.calib_btn = QPushButton("开启标定模式")
        self.calib_btn.setCheckable(True)
        self.calib_btn.setObjectName("calib_btn")
        self.calib_reset_btn = QPushButton("重置标定")
        self.calib_reset_btn.setObjectName("calib_reset_btn")
        self.calib_reset_btn.setEnabled(False)
        
        calibration_layout.addWidget(self.calib_btn)
        calibration_layout.addWidget(self.calib_reset_btn)
        original_layout.addLayout(calibration_layout)
        
        self.original_label = ClickableLabel()
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
        
        main_layout.addWidget(display_splitter, 1)  # 添加伸缩因子，使显示区域随窗口垂直伸缩
        
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
    
    def _on_calib_toggled(self, checked):
        """标定模式开关切换事件"""
        self.original_label.is_calibration_mode = checked
        self.calib_reset_btn.setEnabled(checked)
        if checked:
            self.calib_btn.setText("退出标定模式")
            self.update_info("进入标定模式：请在原图上点击两个点来定义参考长度")
        else:
            self.calib_btn.setText("开启标定模式")
            self.original_label.clear_calibration()
            self.update_info("已退出标定模式")

    def _on_calib_reset_clicked(self):
        """重置标定按钮点击事件"""
        self.original_label.clear_calibration()
        self.update_info("标定点已重置，请重新点击两个点")

    def _on_label_clicked(self, pos):
        """显示标签点击事件"""
        if not self.original_label.is_calibration_mode:
            return
            
        points = self.original_label.points
        if len(points) == 2:
            # 获取实际图像中的坐标
            img_pt1 = self._map_to_image_coords(points[0])
            img_pt2 = self._map_to_image_coords(points[1])
            
            if img_pt1 is None or img_pt2 is None:
                self.show_error("错误", "点击位置不在图像范围内")
                self.original_label.clear_calibration()
                return
                
            # 计算像素距离
            pixel_dist = math.sqrt((img_pt1[0] - img_pt2[0])**2 + (img_pt1[1] - img_pt2[1])**2)
            
            # 弹出对话框
            mm_val, ok = QInputDialog.getDouble(self, "像素标定", "这条线代表实际多少毫米？", 10.0, 0.1, 10000.0, 2)
            
            if ok:
                ratio = mm_val / pixel_dist
                config = ConfigManager()
                config.set("Detection", "pixel_ratio", ratio)
                config.save_config()
                
                self.show_message("标定完成", f"像素比例已更新: {ratio:.4f} mm/pixel\n像素距离: {pixel_dist:.2f} px")
                self.update_info(f"标定完成: {ratio:.4f} mm/pixel")
                
                # 退出标定模式
                self.calib_btn.setChecked(False)
            else:
                self.original_label.clear_calibration()

    def _map_to_image_coords(self, label_pos):
        """将标签坐标映射到原始图像坐标"""
        if self.original_image is None:
            return None
            
        label = self.original_label
        pixmap = label.pixmap()
        if not pixmap:
            return None
            
        # 标签尺寸
        lw, lh = label.width(), label.height()
        # 实际显示的图片尺寸 (scaled)
        pw, ph = pixmap.width(), pixmap.height()
        # 原始图片尺寸
        ih, iw = self.original_image.shape[:2]
        
        # 图片在标签中的偏移 (AlignCenter)
        ox = (lw - pw) / 2
        oy = (lh - ph) / 2
        
        # 点击位置相对于图片左上角的坐标
        rx = label_pos.x() - ox
        ry = label_pos.y() - oy
        
        # 检查是否在图片范围内
        if rx < 0 or rx > pw or ry < 0 or ry > ph:
            return None
            
        # 映射回原始坐标
        img_x = int(rx * iw / pw)
        img_y = int(ry * ih / ph)
        
        return (img_x, img_y)

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
            logger.error(f"显示图像失败: {e}")
    
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
        # 自动滚动到最后一行
        self.info_text.verticalScrollBar().setValue(self.info_text.verticalScrollBar().maximum())
    
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
            self.current_file_path = file_path
            self.detection_mode = "video"
            
            # 清除之前的图像显示
            self.original_label.clear()
            self.result_label.clear()
            
            # 更新信息
            self.update_info(f"已选择视频文件: {file_path}")

    def _on_batch_clicked(self):
        """批量处理按钮点击事件"""
        try:
            # 选择目录
            dir_path = QFileDialog.getExistingDirectory(self, "选择包含图像的目录", "")
            if not dir_path:
                return
            
            # 获取所有图片文件
            valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tif')
            image_paths = [
                os.path.join(dir_path, f) for f in os.listdir(dir_path) 
                if f.lower().endswith(valid_exts)
            ]
            
            if not image_paths:
                self.show_error("错误", "所选目录中没有有效的图像文件")
                return
            
            # 确认批量处理
            reply = QMessageBox.question(
                self, "确认批量处理", 
                f"发现 {len(image_paths)} 张图片，是否开始批量检测？\n这可能需要一些时间。",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            
            if reply == QMessageBox.No:
                return
                
            # 创建进度对话框
            self.batch_progress_dialog = QProgressDialog("正在进行批量检测...", "取消", 0, 100, self)
            self.batch_progress_dialog.setWindowTitle("请稍候")
            self.batch_progress_dialog.setWindowModality(Qt.WindowModal)
            self.batch_progress_dialog.setMinimumDuration(0)
            self.batch_progress_dialog.setAutoClose(True)
            
            # 创建并启动批量检测线程
            from threads.video_detection_thread import BatchDetectionThread
            self.batch_thread = BatchDetectionThread(image_paths)
            self.batch_thread.progress_signal.connect(self.batch_progress_dialog.setValue)
            self.batch_thread.result_signal.connect(self._on_batch_finished)
            
            # 连接取消按钮
            self.batch_progress_dialog.canceled.connect(self.batch_thread.stop)
            
            self.batch_thread.start()
            self.batch_progress_dialog.show()
            
        except Exception as e:
            self.show_error("错误", f"批量处理启动失败: {str(e)}")

    def _on_batch_finished(self, result):
        """批量处理完成事件"""
        if hasattr(self, 'batch_progress_dialog'):
            self.batch_progress_dialog.close()
            
        if result.get("success"):
            total = result.get("total", 0)
            processed = result.get("processed", 0)
            self.show_message("批量处理完成", f"共处理 {total} 张图片，成功 {processed} 张。\n结果已保存至数据库和输出目录。")
            self.update_info(f"批量处理完成: {processed}/{total}")
        else:
            self.show_error("错误", f"批量处理失败: {result.get('error')}")

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
            from utils.config_manager import ConfigManager
            config = ConfigManager()
            
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
                camera_id = config.get("Camera", "camera_id")
                self.detection_thread = VideoDetectionThread(camera_id)  # 使用配置的摄像头ID
                self.detection_thread.frame_processed_signal.connect(self._on_video_frame_processed)
                self.detection_thread.result_signal.connect(self._on_video_detection_finished)
            
            # 连接进度信号
            self.detection_thread.progress_signal.connect(self.update_progress)
            
            # 设置检测状态
            self.is_detecting = True
            
            # 启动线程
            self.detection_thread.start()
            
            # 增加检测次数
            global_state.increment_detection_count()
            
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
            from datetime import datetime
            current_time = datetime.now().strftime('%H:%M:%S')
            stats = detection_result.get("stats", {})
            total_cracks = stats.get("total_cracks", 0)
            max_width_mm = stats.get("max_width_mm", 0)
            
            # 优化日志格式：[时间] 检测完成 | 发现目标: 0 | 最大宽度: 0.00 mm | 状态: 正常
            self.update_info(f"[{current_time}] 检测完成 | 发现目标: {total_cracks} | 最大宽度: {max_width_mm:.2f} mm | 状态: 正常")
            
            # 更新全局状态
            from utils.global_state import global_state
            global_state.update_crack_data(total_cracks, max_width_mm)
            
            # 保存检测结果图片
            import os
            from datetime import datetime
            from utils.config_manager import ConfigManager
            
            # 创建outputs目录（如果不存在）
            config = ConfigManager()
            output_dir = config.get("System", "save_dir")
            if not output_dir:
                output_dir = "outputs"
                
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(output_dir, f"{timestamp}.jpg")
            
            # 保存处理后的图像
            cv2.imwrite(image_path, processed_image)
            
            # 将结果存入数据库
            # 将结果存入数据库
            try:
                from utils.db_manager import DBManager
                db = DBManager()
                db.add_crack_record(
                    project_id=global_state.get_current_project_id() or 1,  # 默认使用项目ID 1
                    score=detection_result.get("score", 0),
                    image_path=image_path,
                    width=max_width_mm,
                    count=total_cracks
                )
                
                # --- 修改开始 ---
                # 获取顶层窗口 (MainWindow) 来访问状态栏
                main_window = self.window()
                if hasattr(main_window, 'statusBar') and main_window.statusBar:
                    main_window.statusBar.showMessage(f"检测结果已归档 | 裂缝数: {total_cracks}", 3000)
                # --- 修改结束 ---
                
            except Exception as e:
                # 注意：如果这里的 e 是关于 statusBar 的错误，说明数据库其实已经保存成功了
                self.show_error("错误", f"保存检测结果到数据库失败: {str(e)}")
            
            # 重置检测状态
            self.is_detecting = False
            
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
            from datetime import datetime
            current_time = datetime.now().strftime('%H:%M:%S')
            stats = result.get("stats", {})
            total_cracks = stats.get("total_cracks", 0)
            max_width_mm = stats.get("max_width_mm", 0)
            
            # 优化日志格式：[时间] 检测完成 | 发现目标: 0 | 最大宽度: 0.00 mm | 状态: 正常
            self.update_info(f"[{current_time}] 检测完成 | 发现目标: {total_cracks} | 最大宽度: {max_width_mm:.2f} mm | 状态: 正常")
            
        except Exception as e:
            logger.error(f"处理视频帧失败: {e}")
    
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
