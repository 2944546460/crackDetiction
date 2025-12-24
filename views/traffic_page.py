#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通荷载页面

展示实时车流变化的图表和日志信息
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGroupBox, QTextEdit, QSplitter
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import os
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
        
        # 初始化车辆计数
        self.vehicle_count = 0
        
        self._init_ui()
        self._init_chart()
        self._init_timer()
    
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
        
        # 创建视频显示区
        self.video_label = QLabel("视频播放区")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("QLabel { background-color: #000000; color: white; border-radius: 8px; font-family: 'Microsoft YaHei'; font-size: 16px; }")
        self.video_label.setMinimumSize(320, 240)  # 降低最小尺寸，提高灵活性
        
        # 左侧：视频显示区
        video_group = QGroupBox("视频监控")
        video_layout = QVBoxLayout(video_group)
        video_layout.addWidget(self.video_label)
        
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
        self.log_text.setMinimumHeight(100)  # 设置最小高度，移除最大高度限制
        
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
        content_splitter.setSizes([640, 600])  # 设置初始大小比例
        
        content_layout.addWidget(content_splitter)
        
        main_layout.addWidget(content_section)
    

    
    def _init_chart(self):
        """初始化图表"""
        # 创建图表布局
        chart_layout = QVBoxLayout(self.chart_container)
        
        # 创建Figure对象
        self.figure = Figure(figsize=(8, 6), dpi=100)
        
        # 设置图表背景为透明
        self.figure.patch.set_alpha(0)
        
        # 创建画布
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        
        # 添加画布到布局
        chart_layout.addWidget(self.canvas)
        
        # 创建图表
        self.ax = self.figure.add_subplot(111)
        
        # 设置图表背景为透明
        self.ax.set_facecolor('none')
        
        # 设置图表样式
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#bdc3c7')
        self.ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.ax.set_xlabel('时间', fontsize=12, color='#34495e')
        self.ax.set_ylabel('车辆数', fontsize=12, color='#34495e')
        
        # 初始化数据
        self.x_data = []  # 存储时间字符串用于标签
        self.y_data = []
        
        # 创建折线图
        self.line, = self.ax.plot(self.x_data, self.y_data, 
                                 color='#3498db', linewidth=2, 
                                 marker='o', markersize=4, 
                                 markerfacecolor='#3498db', 
                                 alpha=0.8)
        
        # 设置Y轴范围
        self.ax.set_ylim(0, 50)
        
        # 设置网格线
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    def _init_timer(self):
        """初始化定时器"""
        # 创建定时器，每秒更新一次数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_data)
        self.timer.start(1000)  # 1秒间隔
    
    def _update_data(self):
        """更新交通数据和图表"""
        # 模拟车辆数（5-30之间的随机数）
        self.vehicle_count = random.randint(5, 30)
        
        # 模拟平均车速（20-80之间的随机数）
        average_speed = random.randint(20, 80)
        
        # 计算车道占用率（基于车辆数）
        lane_occupation = int(self.vehicle_count / 30 * 100)
        
        # 更新状态卡片
        self._update_status_card(self.vehicle_count_card, str(self.vehicle_count))
        self._update_status_card(self.average_speed_card, f"{average_speed} km/h")
        self._update_status_card(self.lane_occupation_card, f"{lane_occupation}%")
        
        # 获取当前时间
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # 更新图表数据
        self.x_data.append(current_time)
        self.y_data.append(self.vehicle_count)
        
        # 只保留最近10个数据点
        if len(self.x_data) > 10:
            self.x_data.pop(0)
            self.y_data.pop(0)
        
        # 使用数值索引作为X轴数据
        x_values = range(len(self.y_data))
        
        # 更新图表
        self.line.set_data(x_values, self.y_data)
        
        # 自动调整X轴范围
        self.ax.set_xlim(-0.5, len(self.y_data) - 0.5)
        self.ax.set_xticks(range(len(self.y_data)))
        
        # 如果数据点足够，显示时间标签
        if len(self.y_data) > 0:
            # 只保留最近的时间标签
            time_labels = ["" for _ in range(len(self.y_data))]
            time_labels[-1] = current_time  # 只显示最新的时间
            if len(self.y_data) > 5:
                time_labels[-5] = self.x_data[-5] if self.x_data else ""  # 显示5个点前的时间
            self.ax.set_xticklabels(time_labels, rotation=45, ha='right', fontsize=10)
        
        self.ax.tick_params(axis='y', labelsize=10)
        
        # 刷新图表
        self.figure.tight_layout()
        self.canvas.draw()
        
        # 记录日志
        self._add_log(f"{current_time} - 车辆数: {self.vehicle_count}, 平均车速: {average_speed} km/h, 车道占用率: {lane_occupation}%")
    
    def _update_status_card(self, card, value):
        """更新状态卡片的值
        
        Args:
            card: 状态卡片
            value: 新的值
        """
        # 获取值标签
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def _add_log(self, message):
        """添加日志信息
        
        Args:
            message: 日志消息
        """
        # 添加日志到文本框
        self.log_text.append(message)
        
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def _create_status_card(self, title, value, color):
        """创建状态卡片
        
        Args:
            title: 卡片标题
            value: 卡片值
            color: 值的颜色
            
        Returns:
            QFrame: 状态卡片
        """
        card = QFrame()
        card.setObjectName("status_card")
        card.setStyleSheet("""
            QFrame#status_card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                min-width: 150px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # 创建标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                margin-bottom: 10px;
                font-family: 'Microsoft YaHei';
                text-align: center;
            }
        """)
        layout.addWidget(title_label)
        
        # 创建值标签
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet("""
            QLabel#value_label {
                font-size: 24px;
                font-weight: bold;
                color: %s;
                font-family: 'Microsoft YaHei';
                text-align: center;
            }
        """ % color)
        layout.addWidget(value_label)
        
        return card
    
    def stop_monitoring(self):
        """停止监测并更新全局状态"""
        if self.timer.isActive():
            self.timer.stop()
            # 更新全局状态
            from utils.global_state import global_state
            global_state.update_vehicle_count(self.vehicle_count)
            self._add_log(f"监测已停止，总车辆数已更新到全局状态: {self.vehicle_count}")
    
    def closeEvent(self, event):
        """页面关闭时停止监测"""
        self.stop_monitoring()
        super().closeEvent(event)
