#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通荷载页面

展示实时车流变化的图表和日志信息（真实数据驱动版）
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGroupBox, QTextEdit, QSplitter, QPushButton
)
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt
import sys
import random
from datetime import datetime

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
                # 尝试导入视频线程
                from threads.video_detection_thread import VideoDetectionThread
                self.yolo_thread = VideoDetectionThread(video_path=0) # 0 代表摄像头，或传入视频路径
                
                # 连接信号：frame_processed_signal 携带 (frame, result)
                self.yolo_thread.frame_processed_signal.connect(self._update_video_label_from_frame)
                self.yolo_thread.finished_signal.connect(self._on_thread_finished)
                
                self.yolo_thread.start()
                
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self._add_log("[INFO] 监测系统启动，正在连接视频流...")
            except Exception as e:
                self._add_log(f"[ERROR] 启动失败: {str(e)}")

    def _on_stop_monitoring(self):
        """停止监测"""
        if self.yolo_thread and self.yolo_thread.is_running:
            self.yolo_thread.stop()
            self._add_log("[INFO] 正在停止监测...")
            
            # 按钮状态将在线程结束信号中更新
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # 保存数据到数据库
            self._save_traffic_data()
            
            # 重置界面显示为0
            self._reset_display_to_zero()
            
        else:
            self._reset_display_to_zero()

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
        total_vehicles = car_count + truck_count + bus_count
        
        self.vehicle_count = total_vehicles # 更新成员变量
        
        # 3. 更新全局状态 (用于报告页)
        from utils.global_state import global_state
        global_state.update_traffic_stats(total_vehicles, truck_count, car_count, bus_count)
        
        # 4. 更新界面卡片
        self._update_status_card(self.vehicle_count_card, str(total_vehicles))
        
        # 模拟计算逻辑：车越多，速度越慢；车越多，占用率越高
        # 假设最大容量50辆
        lane_occupation = min(100, int((total_vehicles / 50.0) * 100))
        # 假设空载速度80，满载速度20
        fake_speed = max(20, int(80 - (total_vehicles * 1.2)))
        
        self._update_status_card(self.average_speed_card, f"{fake_speed} km/h")
        self._update_status_card(self.lane_occupation_card, f"{lane_occupation}%")
        
        # 5. 更新图表 (Real-time Chart)
        current_time = datetime.now().strftime('%H:%M:%S')
        self.x_data.append(current_time)
        self.y_data.append(total_vehicles)
        
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
        """线程结束清理"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._add_log("[INFO] 监测线程已结束")
        self.yolo_thread = None

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