"""
首页总览页面 - 现代简约 B 端风格 (Light Mode)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGroupBox, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect, QFormLayout, QListWidget, QListWidgetItem,
    QComboBox, QTextBrowser, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QRect
import os
import random
import glob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils.global_state import global_state


class ModernCard(QFrame):
    """现代简约 B 端卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QFrame#card_frame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        # 添加轻微投影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class KPICard(ModernCard):
    """现代 KPI 指标卡片"""
    clicked = pyqtSignal()
    
    def __init__(self, title, value, unit, icon_text, color="#3b82f6"):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 左侧图标区域
        icon_label = QLabel(icon_text)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {color}20;
            color: {color};
            font-size: 24px;
            border-radius: 24px;
        """)
        
        # 右侧文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #6b7280; font-size: 14px; font-weight: 500;")
        
        val_layout = QHBoxLayout()
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: #111827; font-size: 24px; font-weight: bold; font-family: 'Segoe UI', 'Arial';")
        
        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("color: #9ca3af; font-size: 13px; margin-left: 4px; margin-bottom: 3px;")
        self.unit_label.setAlignment(Qt.AlignBottom)
        
        val_layout.addWidget(self.value_label)
        val_layout.addWidget(self.unit_label)
        val_layout.addStretch()
        
        text_layout.addWidget(self.title_label)
        text_layout.addLayout(val_layout)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_value(self, value):
        self.value_label.setText(value)


class ScanImageLabel(QLabel):
    """带扫描线效果的图片展示 (浅色模式适配)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_pos = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_scan)
        self.timer.start(50)
        
    def _update_scan(self):
        self.scan_pos += 4
        if self.scan_pos > self.height():
            self.scan_pos = 0
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 绘制扫描线 (淡蓝色)
            pen = QPen(QColor(59, 130, 246, 100))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, self.scan_pos, self.width(), self.scan_pos)
            
            # 绘制四角边框
            pen.setColor(QColor(59, 130, 246, 180))
            pen.setWidth(3)
            painter.setPen(pen)
            length = 20
            # 左上
            painter.drawLine(0, 0, length, 0)
            painter.drawLine(0, 0, 0, length)
            # 右上
            painter.drawLine(self.width(), 0, self.width() - length, 0)
            painter.drawLine(self.width(), 0, self.width(), length)
            # 左下
            painter.drawLine(0, self.height(), length, self.height())
            painter.drawLine(0, self.height(), 0, self.height() - length)
            # 右下
            painter.drawLine(self.width(), self.height(), self.width() - length, self.height())
            painter.drawLine(self.width(), self.height(), self.width(), self.height() - length)


class DashboardPage(QWidget):
    """首页总览页面类 - 现代简约 B 端风格"""
    switch_tab_signal = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("dashboard_page")
        self.setStyleSheet("QWidget#dashboard_page { background-color: #f5f7fa; }")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. 顶部导航/信息栏
        self._setup_header()
        
        # 2. 内容区域 (三栏布局)
        content_wrapper = QWidget()
        self.content_layout = QGridLayout(content_wrapper)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(24)
        
        self._setup_left_panel()
        self._setup_center_panel()
        self._setup_right_panel()
        
        # 设置比例 (左:中:右 = 1:2:1 策略)
        self.content_layout.setColumnStretch(0, 1) # Left (H2 + H1)
        self.content_layout.setColumnStretch(1, 2) # Center (H4 + H3)
        self.content_layout.setColumnStretch(2, 1) # Right (H5 + H6 + H7)
        
        self.main_layout.addWidget(content_wrapper)
        
        # --- 定时器初始化 ---
        # 1. 时钟定时器
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        
        # 2. 模拟日志定时器
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self._add_mock_log)
        self.log_timer.start(3000)
        
        # 3. 数据更新定时器 (KPI 卡片 & 监测图)
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_dashboard_data)
        self.data_timer.start(1000)
        
        # 4. 系统状态心跳定时器 (左下角状态卡片)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(lambda: self.update_system_status('normal'))
        self.status_timer.start(1000)
        
        # 初始加载
        self._load_latest_image()

    def _setup_header(self):
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_frame.setFixedHeight(70)
        header_frame.setStyleSheet("""
            QFrame#header_frame {
                background-color: #ffffff;
                border-bottom: 1px solid #e5e7eb;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # 标题
        title_label = QLabel("智桥卫士 · 桥梁健康监测系统")
        title_label.setStyleSheet("color: #111827; font-size: 20px; font-weight: bold;")
        
        # 项目切换
        self.project_combo = QComboBox()
        self.project_combo.addItems(["八一大桥 (南昌)", "大桥二号", "大桥三号"])
        self.project_combo.setFixedWidth(200)
        self.project_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                color: #333333;
            }
        """)
        
        # --- 模拟终端 (隐藏在 Header 之后供日志写入，或者由于没有设计终端 UI，我们直接注释掉定时器或添加隐藏容器) ---
        # 修复 AttributeError: 'DashboardPage' object has no attribute 'log_terminal'
        self.log_terminal = QTextBrowser()
        self.log_terminal.hide() # 暂时隐藏，因为 UI 布局中没有为它预留位置
        
        # 时钟
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #6b7280; font-size: 15px; font-family: 'Segoe UI';")
        self._update_clock()
        
        layout.addWidget(title_label)
        layout.addSpacing(40)
        layout.addWidget(self.project_combo)
        layout.addStretch()
        layout.addWidget(self.clock_label)
        
        self.main_layout.addWidget(header_frame)

    def _setup_left_panel(self):
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # 桥梁基础信息 (H2 模块)
        bridge_info_card = self._create_bridge_info_card()
        
        # 系统状态总览 (H1 模块)
        status_card = self._create_system_status_card()
        
        layout.addWidget(bridge_info_card, 7) # 档案信息占大头
        layout.addWidget(status_card, 3)     # 状态监控占小头
        self.content_layout.addWidget(left_widget, 0, 0)

    def _create_bridge_info_card(self):
        """创建桥梁基础信息模块 (H2 规格)"""
        card = QFrame()
        card.setObjectName("bridge_info_card")
        card.setStyleSheet("""
            QFrame#bridge_info_card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        
        # 添加轻微投影
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 1. 标题栏
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        # 蓝色竖条装饰
        blue_bar = QFrame()
        blue_bar.setFixedSize(4, 16)
        blue_bar.setStyleSheet("background-color: #1890ff; border-radius: 2px;")
        
        title_label = QLabel("工程档案")
        title_label.setStyleSheet("color: #303133; font-size: 16px; font-weight: bold;")
        
        title_layout.addWidget(blue_bar)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 2. 内容布局 (Grid Layout)
        content_grid = QGridLayout()
        content_grid.setVerticalSpacing(12) # 行间距 12px
        content_grid.setHorizontalSpacing(15)
        
        # 定义字段数据
        fields = [
            ("🌉 桥梁名称:", "八一大桥", True), # 加粗, 16px
            ("🏗️ 结构类型:", "混凝土连续梁", False),
            ("📅 建成年份:", "1997年", False),
            ("📏 桥梁全长:", "500m (主跨 100m)", False),
            ("🚛 设计荷载:", "公路-I级", False),
            ("🏢 管养单位:", "xx市气象局", False)
        ]
        
        for i, (key, value, is_highlight) in enumerate(fields):
            key_label = QLabel(key)
            key_label.setStyleSheet("color: #909399; font-size: 13px;")
            
            val_label = QLabel(value)
            if is_highlight:
                val_label.setStyleSheet("color: #303133; font-size: 16px; font-weight: bold;")
            else:
                val_label.setStyleSheet("color: #303133; font-size: 14px; font-weight: 500;")
            
            content_grid.addWidget(key_label, i, 0)
            content_grid.addWidget(val_label, i, 1)
            content_grid.setColumnStretch(1, 1) # 让值列拉伸
            
        layout.addLayout(content_grid)
        layout.addStretch()
        
        return card

    def _create_system_status_card(self):
        """创建系统状态总览模块"""
        card = QFrame()
        card.setObjectName("status_card")
        card.setStyleSheet("""
            QFrame#status_card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        
        # 添加轻微投影
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 1. 顶部状态区
        status_top_layout = QHBoxLayout()
        status_top_layout.setSpacing(10)
        
        # 状态指示灯 (16x16 圆形)
        self.status_light = QLabel()
        self.status_light.setFixedSize(16, 16)
        self.status_light.setStyleSheet("""
            background-color: #52c41a;
            border-radius: 8px;
            border: 2px solid #f6ffed;
        """)
        
        # 状态文本
        self.status_title_label = QLabel("系统运行正常")
        self.status_title_label.setStyleSheet("color: #303133; font-size: 18px; font-weight: bold;")
        
        status_top_layout.addWidget(self.status_light)
        status_top_layout.addWidget(self.status_title_label)
        status_top_layout.addStretch()
        
        layout.addLayout(status_top_layout)
        
        # 2. 中部异常区 (默认隐藏)
        self.anomaly_container = QFrame()
        self.anomaly_container.setStyleSheet("""
            QFrame {
                background-color: #fef0f0;
                border-radius: 4px;
            }
        """)
        anomaly_layout = QHBoxLayout(self.anomaly_container)
        anomaly_layout.setContentsMargins(12, 10, 12, 10)
        
        warn_icon = QLabel("⚠️")
        warn_icon.setStyleSheet("font-size: 16px;")
        
        self.anomaly_msg_label = QLabel("异常原因说明")
        self.anomaly_msg_label.setWordWrap(True)
        self.anomaly_msg_label.setStyleSheet("color: #f56c6c; font-size: 13px;")
        
        anomaly_layout.addWidget(warn_icon)
        anomaly_layout.addWidget(self.anomaly_msg_label)
        
        self.anomaly_container.hide() # 初始隐藏
        layout.addWidget(self.anomaly_container)
        
        # 3. 底部信息区
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #f3f4f6; max-height: 1px;")
        layout.addWidget(line)
        
        self.status_refresh_label = QLabel("数据刷新: --:--:--")
        self.status_refresh_label.setStyleSheet("color: #909399; font-size: 12px;")
        layout.addWidget(self.status_refresh_label)
        
        return card

    def update_system_status(self, status='normal', message=""):
        """更新系统状态"""
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.status_refresh_label.setText(f"数据刷新: {current_time}")
        
        if status == 'normal':
            # 正常状态
            self.status_light.setStyleSheet("""
                background-color: #52c41a;
                border-radius: 8px;
                border: 2px solid #f6ffed;
            """)
            self.status_title_label.setText("系统运行正常")
            self.anomaly_container.hide()
            
        elif status == 'warning':
            # 警告状态
            self.status_light.setStyleSheet("""
                background-color: #faad14;
                border-radius: 8px;
                border: 2px solid #fffbe6;
            """)
            self.status_title_label.setText("系统维护中/警告")
            self.anomaly_msg_label.setText(message)
            self.anomaly_container.show()
            
        elif status == 'error':
            # 错误状态
            self.status_light.setStyleSheet("""
                background-color: #f5222d;
                border-radius: 8px;
                border: 2px solid #fff1f0;
            """)
            self.status_title_label.setText("系统异常")
            self.anomaly_msg_label.setText(message)
            self.anomaly_container.show()

    def _setup_center_panel(self):
        center_widget = QWidget()
        layout = QVBoxLayout(center_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # H4 | 裂缝信息可视化模块 (动态监测视窗)
        self.visual_card = self._create_visual_monitor_card()
        
        # H3 | 核心指标网格
        kpi_grid = self._create_kpi_grid()
        
        layout.addWidget(self.visual_card, 6) # 视觉重心占 60%
        layout.addWidget(kpi_grid, 4)        # KPI 区域占 40%
        self.content_layout.addWidget(center_widget, 0, 1)

    def _create_visual_monitor_card(self):
        """创建 H4 | 裂缝信息可视化模块 (动态监测视窗)"""
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 监测状态标题栏
        self.monitor_header = QFrame()
        self.monitor_header.setFixedHeight(40)
        self.monitor_header.setStyleSheet("background-color: #f9fafb; border-bottom: 1px solid #e5e7eb; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        h_layout = QHBoxLayout(self.monitor_header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        
        self.monitor_status_label = QLabel("⚪ 正在检测...")
        self.monitor_status_label.setStyleSheet("color: #6b7280; font-size: 13px; font-weight: 500;")
        h_layout.addWidget(self.monitor_status_label)
        h_layout.addStretch()
        
        layout.addWidget(self.monitor_header)

        # 2. 图片展示容器
        self.monitor_label = QLabel()
        self.monitor_label.setAlignment(Qt.AlignCenter)
        self.monitor_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.monitor_label.setMinimumSize(200, 150)
        self.monitor_label.setStyleSheet("background-color: #f3f4f6;")
        
        # 点击事件
        self.monitor_label.mousePressEvent = lambda e: self.switch_tab_signal.emit(1)
        
        # Overlay 叠加层布局
        monitor_layout = QVBoxLayout(self.monitor_label)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.addStretch()
        
        # 半透明信息条
        self.overlay_bar = QFrame()
        self.overlay_bar.setFixedHeight(45)
        self.overlay_bar.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
        """)
        
        overlay_content = QHBoxLayout(self.overlay_bar)
        overlay_content.setContentsMargins(20, 0, 20, 0)
        
        self.overlay_time_label = QLabel("🕒 最近检测: --:--")
        self.overlay_time_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 500;")
        
        self.overlay_crack_label = QLabel("⚠️ 当前裂缝: 0处")
        self.overlay_crack_label.setStyleSheet("color: #ffcc00; font-size: 14px; font-weight: bold;")
        
        overlay_content.addWidget(self.overlay_time_label)
        overlay_content.addStretch()
        overlay_content.addWidget(self.overlay_crack_label)
        
        monitor_layout.addWidget(self.overlay_bar)
        layout.addWidget(self.monitor_label)
        
        return card

    def _create_kpi_grid(self):
        """创建 H3 | 核心指标网格模块 (3列2行)"""
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)
        
        # 1. 桥梁健康指数
        self.health_card = KPICard("桥梁健康指数", "98", "分", "❤️", "#10b981")
        # 2. 当前裂缝数量
        self.crack_count_card = KPICard("当前裂缝数量", "0", "条", "📉", "#ef4444")
        # 3. 主要裂缝等级
        self.crack_level_card = KPICard("主要裂缝等级", "I 级", "级", "⚠️", "#f59e0b")
        # 4. 今日检测次数
        self.det_count_card = KPICard("今日检测次数", "0", "次", "🔍", "#3b82f6")
        # 5. 今日车流量
        self.traffic_count_card = KPICard("今日车流量", "0", "辆", "🚗", "#06b6d4")
        # 6. 重载车辆占比
        self.truck_ratio_card = KPICard("重载车辆占比", "0.0", "%", "🚛", "#8b5cf6")
        
        # 绑定点击跳转 (示例: 点击裂缝跳转到检测页, 点击车流跳转到交通页)
        self.crack_count_card.clicked.connect(lambda: self.switch_tab_signal.emit(1))
        self.crack_level_card.clicked.connect(lambda: self.switch_tab_signal.emit(1))
        self.traffic_count_card.clicked.connect(lambda: self.switch_tab_signal.emit(2))
        self.truck_ratio_card.clicked.connect(lambda: self.switch_tab_signal.emit(2))
        
        # 布局: 3列 2行
        grid_layout.addWidget(self.health_card, 0, 0)
        grid_layout.addWidget(self.crack_count_card, 0, 1)
        grid_layout.addWidget(self.crack_level_card, 0, 2)
        grid_layout.addWidget(self.det_count_card, 1, 0)
        grid_layout.addWidget(self.traffic_count_card, 1, 1)
        grid_layout.addWidget(self.truck_ratio_card, 1, 2)
        
        return grid_widget

    def update_detection_count(self):
        """同步刷新核心指标卡片数值 (Step 3)"""
        # 强制从单例获取最新状态 (解决某些情况下引用旧对象的问题)
        from utils.global_state import global_state
        
        # 1. 健康指数
        self.health_card.set_value(str(global_state._health_score))
        # 2. 裂缝数量
        self.crack_count_card.set_value(str(global_state.crack_count))
        # 3. 裂缝等级
        self.crack_level_card.set_value(global_state.get_crack_level())
        # 4. 检测次数
        self.det_count_card.set_value(str(global_state.get_detection_count()))
        # 5. 今日车流
        stats = global_state.get_traffic_stats()
        self.traffic_count_card.set_value(str(stats['total']))
        # 6. 重载占比
        self.truck_ratio_card.set_value(f"{global_state.get_truck_ratio():.1f}")

    def _setup_right_panel(self):
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15) # Requirement: Spacing = 15
        
        # H5 | 运行趋势统计模块
        trend_card = self._create_trend_card()
        
        # H6 | 风险与预警信息模块
        risk_card = self._create_risk_card()
        
        # H7 | 最近检测记录模块
        recent_records_card = self._create_recent_records_card()
        
        layout.addWidget(trend_card, 1)          # Requirement: Stretch=1
        layout.addWidget(risk_card, 1)           # Requirement: Stretch=1
        layout.addWidget(recent_records_card, 1)  # Requirement: Stretch=1
        
        self.content_layout.addWidget(right_widget, 0, 2)

    def _create_recent_records_card(self):
        """创建 H7｜最近检测记录模块"""
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. 标题栏
        header_layout = QHBoxLayout()
        title = QLabel("🕒 最近检测")
        title.setStyleSheet("color: #111827; font-size: 16px; font-weight: bold;")
        
        view_all_btn = QPushButton("查看全部 >")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setStyleSheet("""
            QPushButton {
                color: #3b82f6;
                font-size: 13px;
                border: none;
                background: transparent;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #2563eb;
                text-decoration: underline;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.switch_tab_signal.emit(4)) # 跳转到 HistoryPage

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(view_all_btn)
        layout.addLayout(header_layout)

        # 2. 列表内容 (QTableWidget)
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setRowCount(3)
        self.recent_table.setShowGrid(False)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.verticalHeader().hide()
        self.recent_table.horizontalHeader().hide()
        self.recent_table.setSelectionMode(QTableWidget.NoSelection)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setFrameShape(QFrame.NoFrame)
        
        # 列宽设置
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.recent_table.setColumnWidth(0, 80)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.recent_table.setColumnWidth(1, 80)
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                alternate-background-color: #f9fafb;
                border: none;
                font-size: 13px;
                color: #4b5563;
            }
            QTableWidget::item {
                padding: 8px 5px;
                border-bottom: 1px solid #f3f4f6;
            }
        """)

        # 插入模拟数据
        data = [
            ("12-28", "裂缝检测", "发现 2 处病害"),
            ("12-28", "交通监测", "通行 1500 辆"),
            ("12-27", "裂缝检测", "正常")
        ]
        
        for row, (time, type_str, result) in enumerate(data):
            time_item = QTableWidgetItem(time)
            type_item = QTableWidgetItem(type_str)
            result_item = QTableWidgetItem(result)
            
            # 设置样式
            type_item.setForeground(QColor("#3b82f6")) # 蓝色强调类型
            
            self.recent_table.setItem(row, 0, time_item)
            self.recent_table.setItem(row, 1, type_item)
            self.recent_table.setItem(row, 2, result_item)

        layout.addWidget(self.recent_table)
        return card

    def _create_risk_card(self):
        """创建 H6｜风险与预警信息模块"""
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. 标题
        title = QLabel("🔔 风险预警")
        title.setStyleSheet("color: #111827; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # 2. 列表容器 (QListWidget)
        self.risk_list = QListWidget()
        self.risk_list.setFrameShape(QFrame.NoFrame)
        self.risk_list.setSelectionMode(QListWidget.NoSelection)
        self.risk_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #f3f4f6;
                padding: 5px 0;
            }
            QListWidget::item:last {
                border-bottom: none;
            }
        """)
        layout.addWidget(self.risk_list)

        # 3. 空状态标签 (默认隐藏)
        self.risk_empty_label = QLabel("✅ 当前无异常风险")
        self.risk_empty_label.setAlignment(Qt.AlignCenter)
        self.risk_empty_label.setStyleSheet("color: #52c41a; font-size: 14px; font-weight: 500; margin: 30px 0;")
        self.risk_empty_label.hide()
        layout.addWidget(self.risk_empty_label)

        # 插入模拟数据
        self._add_risk_item("严重", "监测到主梁裂缝宽度超限", "10:30")
        self._add_risk_item("警告", "重载车辆占比过高", "09:15")

        return card

    def _add_risk_item(self, level, message, time_str):
        """添加风险项到列表"""
        item = QListWidgetItem(self.risk_list)
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 10, 5, 10)
        item_layout.setSpacing(12)

        # 1. 风险等级徽章
        level_label = QLabel(level)
        level_label.setFixedSize(45, 22)
        level_label.setAlignment(Qt.AlignCenter)
        
        # 颜色映射
        colors = {
            "严重": ("#f5222d", "#fff1f0"), # 红底
            "警告": ("#faad14", "#fffbe6"), # 橙底
            "提示": ("#1890ff", "#e6f7ff")  # 蓝底
        }
        text_color, bg_color = colors.get(level, ("#1890ff", "#e6f7ff"))
        level_label.setStyleSheet(f"""
            background-color: {text_color};
            color: white;
            font-size: 11px;
            font-weight: bold;
            border-radius: 4px;
        """)

        # 2. 描述与时间
        text_container = QVBoxLayout()
        text_container.setSpacing(2)
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True) # Bug Fix: 防止长文字被截断
        msg_label.setStyleSheet("color: #374151; font-size: 13px; font-weight: 500;")
        
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
        
        text_container.addWidget(msg_label)
        text_container.addWidget(time_label)

        # 3. 详情箭头
        arrow_label = QLabel(">")
        arrow_label.setStyleSheet("color: #d1d5db; font-size: 16px; font-weight: bold;")

        item_layout.addWidget(level_label)
        item_layout.addLayout(text_container, 1)
        item_layout.addWidget(arrow_label)

        # 设置 Item 尺寸
        item.setSizeHint(item_widget.sizeHint())
        self.risk_list.setItemWidget(item, item_widget)
        
        # 刷新空状态逻辑
        self._update_risk_visibility()

    def _update_risk_visibility(self):
        """根据数据量切换空状态显示"""
        has_data = self.risk_list.count() > 0
        self.risk_list.setVisible(has_data)
        self.risk_empty_label.setVisible(not has_data)

    def _create_trend_card(self):
        """创建 H5｜运行趋势统计模块"""
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. 头部 (Header)
        header_layout = QHBoxLayout()
        title = QLabel("📈 运行趋势")
        title.setStyleSheet("color: #111827; font-size: 16px; font-weight: bold;")
        
        self.trend_filter = QComboBox()
        self.trend_filter.addItems(["裂缝数量趋势", "交通流量趋势"])
        self.trend_filter.setFixedWidth(120)
        self.trend_filter.setStyleSheet("""
            QComboBox {
                background-color: #f9fafb;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 2px 10px;
                color: #606266;
            }
            QComboBox:hover {
                border-color: #409eff;
            }
        """)
        self.trend_filter.currentIndexChanged.connect(self._update_trend_chart)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.trend_filter)
        layout.addLayout(header_layout)

        # 2. 图表区
        self.trend_figure = Figure(figsize=(5, 4), facecolor='white')
        self.trend_canvas = FigureCanvas(self.trend_figure)
        self.trend_canvas.setMinimumSize(200, 200)
        layout.addWidget(self.trend_canvas)

        # 初始化图表
        self._update_trend_chart()
        
        return card

    def _update_trend_chart(self):
        """更新 H5 模块图表数据"""
        self.trend_figure.clear()
        ax = self.trend_figure.add_subplot(111)
        ax.set_facecolor('white')

        # 准备数据
        days = []
        now = QDateTime.currentDateTime()
        for i in range(6, -1, -1):
            days.append(now.addDays(-i).toString("MM-dd"))

        filter_text = self.trend_filter.currentText()
        if "裂缝数量" in filter_text:
            data = [2, 3, 2, 5, 4, 6, 5]
            color = "#ff4d4f" # 红色预警感
            ylabel = "裂缝条数"
        else:
            data = [1200, 1350, 1100, 1500, 1400, 1600, 1550]
            color = "#1890ff" # 科技蓝
            ylabel = "通行量 (辆)"

        # 绘制平滑曲线 (使用样条插值模拟平滑效果，或直接用简单折线加平滑处理)
        # 这里使用 plot 直接绘制，并设置样式
        ax.plot(days, data, color=color, linewidth=2.5, marker='o', 
                markersize=6, markerfacecolor='white', markeredgewidth=2)
        
        # 填充区域
        ax.fill_between(days, data, 0, color=color, alpha=0.1)

        # 样式优化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e5e7eb')
        ax.spines['bottom'].set_color('#e5e7eb')
        
        ax.tick_params(colors='#9ca3af', labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='#e5e7eb')
        
        # 布局紧凑
        try:
            self.trend_figure.tight_layout()
        except:
            pass
            
        self.trend_canvas.draw()

    def _update_clock(self):
        self.clock_label.setText(QDateTime.currentDateTime().toString("yyyy年MM月dd日 HH:mm:ss"))

    def _add_mock_log(self):
        logs = ["传感器 L3 状态正常", "环境湿度 65% (适宜)", "视觉模块心跳正常", "通行记录: 苏A·66666", "系统备份完成", "发现细微裂缝 (已标记)"]
        log = random.choice(logs)
        time_str = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_terminal.append(f"<span style='color: #9ca3af;'>[{time_str}]</span> <span style='color: #3b82f6;'>INFO</span> {log}")
        self.log_terminal.moveCursor(self.log_terminal.textCursor().End)

    def update_dashboard_data(self):
        """定时更新首页数据"""
        # 调用核心指标更新方法
        self.update_detection_count()
        
        # 刷新监测视窗图片及 Overlay
        self._load_latest_image()

    def _load_latest_image(self):
        """Bug Fix: 优先读取 outputs/*.jpg，否则读取参考底图"""
        import glob
        import os
        
        img_path = ""
        is_realtime = False
        
        # 1. 尝试读取 outputs 最新图
        outputs_dir = os.path.join(os.getcwd(), "outputs")
        if os.path.exists(outputs_dir):
            files = glob.glob(os.path.join(outputs_dir, "*.jpg"))
            if files:
                img_path = max(files, key=os.path.getmtime)
                is_realtime = True
        
        # 2. 如果没有，读取参考底图
        if not img_path:
            ref_path = os.path.join(os.getcwd(), "icons", "八一大桥.jpg")
            if os.path.exists(ref_path):
                img_path = ref_path
                is_realtime = False
        
        # 3. 更新 UI
        if img_path:
            # 只有当路径变化时才重新加载 Pixmap
            if not hasattr(self, '_current_image_path') or self._current_image_path != img_path:
                self._current_image_path = img_path
                self.original_pixmap = QPixmap(img_path)
                # 清除尺寸缓存，强制重新渲染新图片
                if hasattr(self, '_last_scaled_size'):
                    delattr(self, '_last_scaled_size')
                self._update_image()
            
            # 更新状态文字
            if is_realtime:
                self.monitor_status_label.setText("🟢 实时画面")
                self.monitor_status_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
            else:
                self.monitor_status_label.setText("⚪ 参考底图")
                self.monitor_status_label.setStyleSheet("color: #6b7280; font-size: 13px; font-weight: 500;")
            
            # 更新 Overlay 时间
            mtime = os.path.getmtime(img_path)
            from datetime import datetime
            time_str = datetime.fromtimestamp(mtime).strftime("%H:%M")
            self.overlay_time_label.setText(f"🕒 最近检测: {time_str}")
            
            # 更新 Overlay 裂缝数量
            from utils.global_state import global_state
            color = "#ff4d4f" if global_state.crack_count > 0 else "#ffcc00"
            self.overlay_crack_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            self.overlay_crack_label.setText(f"⚠️ 当前裂缝: {global_state.crack_count}处")
        else:
            self.monitor_label.setText("暂无画面数据")
            self.monitor_status_label.setText("🔴 离线")

    def _update_image(self):
        """确保图片采用 KeepAspectRatioByExpanding 模式，填满容器且不变形"""
        if hasattr(self, 'monitor_label') and hasattr(self, 'original_pixmap') and self.original_pixmap:
            # 关键修复：获取当前 Label 的几何尺寸，但不让 setPixmap 影响布局
            # 使用 contentsRect() 避开边距影响
            rect = self.monitor_label.contentsRect()
            w, h = rect.width(), rect.height()
            
            if w > 10 and h > 10:
                # 检查是否需要重新缩放（避免微小尺寸变动导致的反馈循环）
                if (hasattr(self, '_last_scaled_size') and 
                    abs(self._last_scaled_size.width() - w) < 2 and 
                    abs(self._last_scaled_size.height() - h) < 2):
                    return

                self._last_scaled_size = rect.size()
                
                # 修复：改为等比例显示，避免裁剪导致显示不全
                scaled_pixmap = self.original_pixmap.scaled(
                    rect.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                self.monitor_label.blockSignals(True)
                self.monitor_label.setPixmap(scaled_pixmap)
                self.monitor_label.blockSignals(False)

    def showEvent(self, event):
        """页面显示时强制刷新一次数据"""
        super().showEvent(event)
        self.update_dashboard_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image()
