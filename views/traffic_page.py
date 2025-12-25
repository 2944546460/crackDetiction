#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通荷载页面

展示实时车流变化的图表和日志信息（真实数据驱动版）
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGroupBox, QTextEdit, QSplitter, QPushButton, QRadioButton,
    QButtonGroup, QLineEdit, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt
import sys
import os
import random
import cv2
from datetime import datetime
from utils.logger import logger

# 导入Matplotlib相关模块
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams


class TrafficPage(QWidget):
    """交通荷载页面类"""
    
    def __init__(self):
        """初始化交通荷载页面"""
        super().__init__()
        
        # 设置中文字体
        rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']
        
        # 初始化数据
        self.vehicle_count = 0
        self.x_data = []  # 存储时间轴
        self.y_data = []  # 存储车辆数
        
        # 信号源相关变量
        self.video_source = 0  # 默认为摄像头ID 0
        self.source_type = 'camera'  # 'camera' 或 'file'
        
        self._init_ui()
        self._init_chart()
        # 注意：这里不再初始化定时器，完全由视频线程驱动
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("交通荷载")
        title_label.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; margin-bottom: 10px; font-family: 'Microsoft YaHei'; }")
        main_layout.addWidget(title_label)
        
        # --- 新增：信号源选择栏 ---
        source_group = QGroupBox("信号源选择")
        source_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        source_layout = QHBoxLayout(source_group)
        source_layout.setSpacing(15)
        
        # 单选按钮组
        self.camera_radio = QRadioButton("实时摄像头")
        self.file_radio = QRadioButton("视频文件")
        self.camera_radio.setChecked(True)
        
        self.source_group_btns = QButtonGroup(self)
        self.source_group_btns.addButton(self.camera_radio, 0)
        self.source_group_btns.addButton(self.file_radio, 1)
        self.source_group_btns.buttonClicked.connect(self._on_source_type_changed)
        
        source_layout.addWidget(self.camera_radio)
        source_layout.addWidget(self.file_radio)
        
        # 路径显示
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("未选择视频文件")
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f7fa; color: #909399;")
        source_layout.addWidget(self.path_edit, 1)
        
        # 选择文件按钮
        self.select_file_btn = QPushButton("📂 选择文件")
        self.select_file_btn.setEnabled(False) # 初始禁用
        self.select_file_btn.setCursor(Qt.PointingHandCursor)
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover { border-color: #3498db; color: #3498db; }
            QPushButton:disabled { background-color: #f5f7fa; color: #c0c4cc; }
        """)
        self.select_file_btn.clicked.connect(self._on_select_file)
        source_layout.addWidget(self.select_file_btn)
        
        main_layout.addWidget(source_group)
        
        # 创建内容区域
        content_section = QGroupBox()
        content_layout = QVBoxLayout(content_section)
        content_layout.setSpacing(20)
        
        # 创建交通荷载状态卡片
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setSpacing(15)
        
        # 车辆数卡片
        self.vehicle_count_card = self._create_status_card("当前车辆数", "0", "#3498db")
        status_layout.addWidget(self.vehicle_count_card)
        
        # 平均车速卡片
        self.average_speed_card = self._create_status_card("平均车速", "0 km/h", "#2ecc71")
        status_layout.addWidget(self.average_speed_card)
        
        # 车道占用率卡片
        self.lane_occupation_card = self._create_status_card("车道占用率", "0%", "#e74c3c")
        status_layout.addWidget(self.lane_occupation_card)
        
        content_layout.addWidget(status_frame)
        
        # 创建主内容区的左右布局（左视频-右图表）
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：视频显示区
        video_group = QGroupBox("视频监控")
        video_layout = QVBoxLayout(video_group)
        
        self.video_label = QLabel("视频播放区")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("QLabel { background-color: #000000; color: white; border-radius: 8px; font-family: 'Microsoft YaHei'; font-size: 16px; }")
        self.video_label.setMinimumSize(320, 240)
        video_layout.addWidget(self.video_label)
        
        # 添加控制按钮栏
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(10, 10, 10, 0)
        
        # 创建开始监测按钮（绿色）
        self.start_btn = QPushButton("▶ 开始监测")
        self.start_btn.setObjectName("start_monitoring_btn") # 配合QSS
        self.start_btn.setCursor(Qt.PointingHandCursor)
        
        # 创建停止监测按钮（红色）
        self.stop_btn = QPushButton("⏹ 停止监测")
        self.stop_btn.setObjectName("stop_monitoring_btn") # 配合QSS
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        
        video_layout.addLayout(control_layout)
        
        # 初始化YOLO视频检测线程变量
        self.yolo_thread = None
        
        # 连接按钮信号
        self.start_btn.clicked.connect(self._on_start_monitoring)
        self.stop_btn.clicked.connect(self._on_stop_monitoring)
        
        # 右侧：日志和图表区域
        right_group = QGroupBox("数据统计")
        right_layout = QVBoxLayout(right_group)
        right_layout.setSpacing(20)
        
        # 创建日志框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                color: #333333;
            }
        """)
        self.log_text.setMinimumHeight(100)
        
        # 创建图表容器
        self.chart_container = QFrame()
        self.chart_container.setStyleSheet("""
            QFrame {
                background-color: #f4f6f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        
        right_layout.addWidget(self.log_text)
        right_layout.addWidget(self.chart_container)
        
        # 将左右两部分添加到分割器
        content_splitter.addWidget(video_group)
        content_splitter.addWidget(right_group)
        content_splitter.setSizes([640, 600])
        
        content_layout.addWidget(content_splitter)
        
        main_layout.addWidget(content_section, 1)
    
    def _init_chart(self):
        """初始化图表"""
        chart_layout = QVBoxLayout(self.chart_container)
        
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_alpha(0) # 透明背景
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        chart_layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('none')
        
        # 样式设置
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#bdc3c7')
        self.ax.spines['bottom'].set_color('#bdc3c7')
        self.ax.set_xlabel('时间', fontsize=12, color='#34495e')
        self.ax.set_ylabel('车辆数', fontsize=12, color='#34495e')
        
        # 初始空线条
        self.line, = self.ax.plot([], [], 
                                 color='#3498db', linewidth=2, 
                                 marker='o', markersize=4, 
                                 markerfacecolor='#3498db', 
                                 alpha=0.8)
        
        self.ax.set_ylim(0, 50)
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    def _create_status_card(self, title, value, color):
        """创建状态卡片辅助函数"""
        card = QFrame()
        card.setObjectName("status_card")
        # 样式已在全局 styles.py 中定义，这里可以补充局部样式
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666; font-family: 'Microsoft YaHei';")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color}; font-family: 'Microsoft YaHei';")
        layout.addWidget(value_label, alignment=Qt.AlignCenter)
        
        return card

    def _update_status_card(self, card, value):
        """更新状态卡片"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)

    def _add_log(self, message):
        """添加日志"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _on_start_monitoring(self):
        """开始监测"""
        if not self.yolo_thread:
            try:
                # 确定信号源
                if self.source_type == 'camera':
                    from utils.config_manager import ConfigManager
                    config = ConfigManager()
                    source = config.get("Camera", "camera_id")
                    # 尝试转为整数（如果是摄像头索引）
                    try:
                        source = int(source)
                    except (ValueError, TypeError):
                        pass
                else:
                    source = self.video_source
                    if not source or not os.path.exists(str(source)):
                        QMessageBox.warning(self, "错误", "请先选择有效的视频文件！")
                        return

                # 尝试导入视频线程
                    from threads.video_detection_thread import VideoDetectionThread
                    
                    # 显式指定使用 yolo11n.pt 车辆检测模型
                    self.yolo_thread = VideoDetectionThread(video_path=source, model_path="yolo11n.pt")
                    
                    # 连接信号
                self.yolo_thread.frame_processed_signal.connect(self._update_video_label_from_frame)
                self.yolo_thread.finished_signal.connect(self._on_thread_finished)
                
                # 检查视频源是否能打开
                cap = cv2.VideoCapture(source)
                if not cap.isOpened():
                    QMessageBox.critical(self, "连接失败", f"无法打开视频源: {source}\n请检查摄像头连接或视频文件路径。")
                    self.yolo_thread = None
                    return
                cap.release()

                self.yolo_thread.start()
                
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.camera_radio.setEnabled(False)
                self.file_radio.setEnabled(False)
                self.select_file_btn.setEnabled(False)
                
                self._add_log(f"[INFO] 监测系统启动，源: {source}")
            except Exception as e:
                import traceback
                logger.error(f"启动交通监测失败: {e}\n{traceback.format_exc()}")
                QMessageBox.critical(self, "错误", f"启动监测失败: {str(e)}")
                self.yolo_thread = None

    def _on_stop_monitoring(self):
        """停止监测"""
        if self.yolo_thread:
            self.yolo_thread.stop()
            self.yolo_thread.wait() # 等待线程完全退出
            self.yolo_thread = None
            
            self._add_log("[INFO] 监测已停止")
            
            # 按钮状态恢复
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.camera_radio.setEnabled(True)
            self.file_radio.setEnabled(True)
            if self.source_type == 'file':
                self.select_file_btn.setEnabled(True)
            
            # 1. 清空画面 (显示黑色背景)
            black_pixmap = QPixmap(self.video_label.size())
            black_pixmap.fill(Qt.black)
            self.video_label.setPixmap(black_pixmap)
            
            # 2. 重置数据和图表
            self._reset_data()
            
            # 3. 保存数据到数据库
            self._save_traffic_data()

    def _on_source_type_changed(self, button):
        """信号源类型切换事件"""
        if button == self.camera_radio:
            self.source_type = 'camera'
            self.select_file_btn.setEnabled(False)
            self.path_edit.setText("")
        else:
            self.source_type = 'file'
            self.select_file_btn.setEnabled(True)
            if hasattr(self, 'video_source') and isinstance(self.video_source, str):
                self.path_edit.setText(self.video_source)

    def _on_select_file(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
        )
        if file_path:
            self.video_source = file_path
            self.path_edit.setText(file_path)
            self.file_radio.setChecked(True)
            self.source_type = 'file'

    def _reset_data(self):
        """重置所有统计数据和图表"""
        self.vehicle_count = 0
        self.x_data = []
        self.y_data = []
        
        # 更新卡片显示
        self._reset_display_to_zero()
        
        # 重置图表
        self.line.set_data([], [])
        self.ax.set_xlim(0, 10)
        self.canvas.draw()
        
        self._add_log("[INFO] 统计数据已重置")

    def closeEvent(self, event):
        """窗口关闭事件：确保线程退出"""
        if self.yolo_thread and self.yolo_thread.isRunning():
            self.yolo_thread.stop()
            self.yolo_thread.wait()
        super().closeEvent(event)

    def _update_video_label_from_frame(self, frame, result):
        """
        核心方法：处理视频帧并利用真实检测结果更新图表
        """
        # 1. 显示视频画面
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        q_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 2. 解析真实数据
        stats = result.get("stats", {})
        car_count = stats.get("car", 0)
        truck_count = stats.get("truck", 0)
        bus_count = stats.get("bus", 0)
        current_vehicles = stats.get("current_frame_vehicles", 0)
        total_flow = stats.get("total_vehicles", 0)
        avg_speed = stats.get("avg_speed", 0)
        
        self.vehicle_count = current_vehicles # 更新当前帧车辆数
        
        # 3. 更新全局状态 (用于报告页)
        from utils.global_state import global_state
        global_state.update_traffic_stats(total_flow, truck_count, car_count, bus_count)
        
        # 4. 更新界面卡片
        # 将车辆数卡片显示为：当前: X / 累计: Y
        self._update_status_card(self.vehicle_count_card, f"{current_vehicles} (累计: {total_flow})")
        
        # 计算逻辑优化：
        # 1. 车速：使用检测线程计算出的真实位移速度
        display_speed = int(avg_speed) if avg_speed > 0 else 0
        
        # 2. 车道占用率：根据当前画面车辆密度计算
        # 假设单画面超过 15 辆车即为 100% 拥堵
        lane_occupation = min(100, int((current_vehicles / 15.0) * 100))
        
        self._update_status_card(self.average_speed_card, f"{display_speed} km/h")
        self._update_status_card(self.lane_occupation_card, f"{lane_occupation}%")
        
        # 5. 更新图表 (Real-time Chart) - 绘制当前车辆数变化
        current_time = datetime.now().strftime('%H:%M:%S')
        self.x_data.append(current_time)
        self.y_data.append(current_vehicles)
        
        # 保持图表窗口大小 (最近10个点)
        if len(self.x_data) > 10:
            self.x_data.pop(0)
            self.y_data.pop(0)
            
        # 重绘
        x_values = range(len(self.y_data))
        self.line.set_data(x_values, self.y_data)
        self.ax.set_xlim(-0.5, max(9.5, len(self.y_data) - 0.5)) # 固定显示范围或随数据动
        self.ax.set_xticks(range(len(self.y_data)))
        self.ax.set_xticklabels(self.x_data, rotation=45, ha='right', fontsize=8)
        
        self.canvas.draw()
        
        # 6. 更新日志 (可选：防止刷屏，可以加条件限制)
        # self._add_log(f"[{current_time}] 车辆: {total_vehicles} (重车: {truck_count})")

    def _on_thread_finished(self):
        """线程结束时的处理"""
        # 仅仅恢复按钮状态，不要直接重置数据，让用户能看到最后的结果
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.camera_radio.setEnabled(True)
        self.file_radio.setEnabled(True)
        if self.source_type == 'file':
            self.select_file_btn.setEnabled(True)
        
        self.yolo_thread = None
        self._add_log("[INFO] 视频处理完成。")

    def _save_traffic_data(self):
        """保存数据到数据库"""
        from utils.global_state import global_state
        vehicle_stats = global_state.get_traffic_stats()
        try:
            from utils.db_manager import DBManager
            db = DBManager()
            db.add_traffic_record(
                project_id=global_state.get_current_project_id() or 1,
                score=0, 
                total=vehicle_stats["total"],
                truck=vehicle_stats["truck"],
                car=vehicle_stats["car"],
                bus=vehicle_stats["bus"]
            )
            self._add_log(f"[DB] 数据已保存: {vehicle_stats}")
        except Exception as e:
            self._add_log(f"[ERROR] 数据库写入失败: {e}")

    def _reset_display_to_zero(self):
        """重置显示为0"""
        self._update_status_card(self.vehicle_count_card, "0")
        self._update_status_card(self.average_speed_card, "0 km/h")
        self._update_status_card(self.lane_occupation_card, "0%")
        
        # 清空图表
        self.x_data = []
        self.y_data = []
        self.line.set_data([], [])
        self.ax.set_xticklabels([])
        self.canvas.draw()

    def closeEvent(self, event):
        self._on_stop_monitoring()
        super().closeEvent(event)