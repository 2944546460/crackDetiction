#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智桥卫士 - 主窗口界面

采用PyQt5实现的主窗口界面，包含左侧导航栏和右侧多页面容器。
左侧导航栏包含4个按钮，用于切换右侧不同的功能页面。
右侧使用QStackedWidget实现多页面切换功能。
"""

import sys
import os
import cv2

# 添加项目根目录到Python路径，确保能够正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QWidget, QSplitter, QLabel, QTextEdit,
    QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# 尝试不同的导入方式，确保无论是直接运行还是作为模块导入都能正常工作
try:
    from views.detection_page import DetectionPage
    from views.dashboard_page import DashboardPage
    from views.report_page import ReportPage
    from views.traffic_page import TrafficPage
    from views.history_page import HistoryPage
except ImportError:
    from detection_page import DetectionPage
    from dashboard_page import DashboardPage
    from report_page import ReportPage
    from traffic_page import TrafficPage
    from history_page import HistoryPage

# 导入YOLO视频检测线程
try:
    from threads.video_threads import YOLOThread
except ImportError:
    try:
        from video_threads import YOLOThread
    except ImportError:
        print("无法导入YOLOThread类")
        YOLOThread = None


class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        # 设置窗口标题和大小
        self.setWindowTitle("智桥卫士 (Bridge Monitor)")
        self.resize(1200, 800)
        
        # 初始化UI组件
        self.init_ui()
        
        # 连接信号与槽
        self.connect_signals()
        
        # 初始化状态栏
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("就绪")
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距，最大化可用空间
        main_layout.setSpacing(0)  # 移除间距
        
        # 创建左侧导航栏
        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("nav_frame")
        self.nav_frame.setFixedWidth(200)
        
        # 创建导航栏布局（垂直布局）
        nav_layout = QVBoxLayout(self.nav_frame)
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(20, 30, 20, 20)
        
        # 创建Logo区域
        logo_label = QLabel("智桥卫士 v1.0")
        logo_label.setObjectName("logo_label")
        logo_label.setStyleSheet("QLabel#logo_label { font-size: 18px; font-weight: bold; color: white; text-align: center; margin-bottom: 20px; padding: 10px 0; border-bottom: 1px solid #34495e; }")
        nav_layout.addWidget(logo_label)
        
        # 创建导航按钮
        self.home_btn = QPushButton("🏠 首页总览")
        self.detection_btn = QPushButton("📷 裂缝检测")
        self.traffic_btn = QPushButton("🚛 交通荷载")
        self.report_btn = QPushButton("📋 评估报告")
        self.history_btn = QPushButton("📊 历史记录")
        # 将按钮放入一个列表，方便批量处理
        self.nav_btns = [self.home_btn, self.detection_btn, self.traffic_btn, self.report_btn, self.history_btn]
        
        for btn in self.nav_btns:
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            
            # --- 新增：设置为可选中模式 ---
            btn.setCheckable(True)       # 允许按钮处于“按下”状态
            btn.setAutoExclusive(True)   # 自动互斥（点亮一个，其他的自动熄灭）
            
            nav_layout.addWidget(btn)
            
        # 默认选中第一个
        self.home_btn.setChecked(True)
        # 设置按钮对象名称
        self.home_btn.setObjectName("home_btn")
        self.detection_btn.setObjectName("detection_btn")
        self.traffic_btn.setObjectName("traffic_btn")
        self.report_btn.setObjectName("report_btn")
        self.history_btn.setObjectName("history_btn")
        
        for btn in [self.home_btn, self.detection_btn, self.traffic_btn, self.report_btn, self.history_btn]:
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            nav_layout.addWidget(btn)
        
        # 添加伸缩空间，使按钮靠上排列
        nav_layout.addStretch()
        
        # 创建右侧多页面容器
        self.stacked_widget = QStackedWidget()
        
        # 创建5个页面
        self.home_page = DashboardPage()
        
        # 使用DetectionPage作为裂缝检测页面
        self.detection_page = DetectionPage()
        
        # 创建交通荷载页面
        self.traffic_page = TrafficPage()
        
        self.report_page = ReportPage()
        
        # 创建历史记录页面
        self.history_page = HistoryPage()
        
        # 将页面添加到多页面容器
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.detection_page)
        self.stacked_widget.addWidget(self.traffic_page)
        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.history_page)
        
        # 将左侧导航栏和右侧多页面容器添加到主布局
        main_layout.addWidget(self.nav_frame)
        main_layout.addWidget(self.stacked_widget, 1)  # 设置伸缩因子，使右侧占据剩余空间
        
        # 设置中央部件的布局策略，使其能在垂直方向上伸缩
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def connect_signals(self):
        """连接信号与槽"""
        # 连接导航按钮与页面切换槽函数
        self.home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.detection_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.traffic_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.report_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.history_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
    
    def initialize(self):
        """初始化主窗口"""
        # 可以在这里添加额外的初始化代码
        pass
    
    def _init_traffic_page(self):
        """初始化交通荷载页面"""
        # 创建页面布局（垂直布局）
        page_layout = QVBoxLayout(self.traffic_page)
        page_layout.setSpacing(20)
        page_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建视频显示区域
        self.video_label = QLabel("视频显示区")
        self.video_label.setObjectName("video_display_label")
        self.video_label.setAlignment(Qt.AlignCenter)
        page_layout.addWidget(self.video_label)
        
        # 创建控制按钮区域（水平布局）
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.start_btn = QPushButton("开始监测")
        self.start_btn.setObjectName("start_monitoring_btn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        
        self.stop_btn = QPushButton("停止监测")
        self.stop_btn.setObjectName("stop_monitoring_btn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)  # 初始禁用停止按钮
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()  # 添加伸缩空间，将按钮靠左对齐
        
        page_layout.addLayout(control_layout)
        
        # 创建日志文本框
        self.log_textedit = QTextEdit()
        self.log_textedit.setReadOnly(True)  # 设置为只读
        self.log_textedit.append("日志信息：")
        self.log_textedit.append("交通荷载监测系统已就绪")
        page_layout.addWidget(self.log_textedit, 1)  # 设置伸缩因子，使日志框占据剩余空间
        
        # 初始化YOLO视频检测线程
        self.yolo_thread = None
        
        # 连接控制按钮信号
        self.start_btn.clicked.connect(self._on_start_monitoring)
        self.stop_btn.clicked.connect(self._on_stop_monitoring)
    
    def _on_start_monitoring(self):
        """开始监测按钮点击事件"""
        if not self.yolo_thread:
            # 实例化VideoDetectionThread视频检测线程（默认使用摄像头0）
            from threads.video_detection_thread import VideoDetectionThread
            self.yolo_thread = VideoDetectionThread(video_path=0)
            
            # 连接线程信号
            self.yolo_thread.frame_processed_signal.connect(self._update_video_label_from_frame)
            self.yolo_thread.frame_processed_signal.connect(self._update_stats_from_result)
            self.yolo_thread.finished_signal.connect(self._on_thread_finished)
            
            # 启动线程
            self.yolo_thread.start()
            
            # 更新按钮状态
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # 添加日志信息
            self.log_textedit.append("[INFO] 开始交通荷载监测")
        else:
            self.log_textedit.append("[ERROR] 监测已经在运行中或YOLOThread未正确导入")
    
    def _on_stop_monitoring(self):
        """停止监测按钮点击事件"""
        if self.yolo_thread and self.yolo_thread.is_running:
            # 停止线程
            self.yolo_thread.stop()
            
            # 更新按钮状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # 添加日志信息
            self.log_textedit.append("[INFO] 停止交通荷载监测")
    
    def _update_video_label(self, q_image):
        """更新视频显示标签
        
        Args:
            q_image: 要显示的QImage对象
        """
        # 将QImage转换为QPixmap，然后缩放以适应标签大小
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
        
    def _update_video_label_from_frame(self, frame, result):
        """从视频帧更新视频显示标签
        
        Args:
            frame: 处理后的视频帧（numpy数组，BGR格式）
            result: 检测结果
        """
        # 将OpenCV的BGR格式转换为Qt的RGB格式
        import cv2
        from PyQt5.QtGui import QPixmap, QImage
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 将QImage转换为QPixmap，然后缩放以适应标签大小
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
    
    def _update_stats(self, stats):
        """更新检测统计信息
        
        Args:
            stats: 包含检测统计数据的字典
        """
        if stats:
            log_msg = f"[STATS] {stats}"
            self.log_textedit.append(log_msg)
    
    def _update_stats_from_result(self, frame, result):
        """从检测结果更新统计信息
        
        Args:
            frame: 处理后的视频帧（numpy数组，BGR格式）
            result: 检测结果数据
        """
        # 获取检测统计信息
        stats = result.get("stats", {})
        
        # 根据用户需求，实时打印"当前车流：Car=X, Truck=Y"
        # 这里假设stats中包含car和truck的计数信息
        car_count = stats.get("car", 0)
        truck_count = stats.get("truck", 0)
        
        # 更新日志文本框
        self.log_textedit.append(f"当前车流：Car={car_count}, Truck={truck_count}")
    
    def _on_thread_finished(self):
        """线程结束事件"""
        # 更新按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 添加日志信息
        self.log_textedit.append("[INFO] 交通荷载监测线程已结束")
        
        # 重置线程对象
        self.yolo_thread = None
    
    def _update_video_label_from_frame(self, frame, result):
        """从视频帧更新视频显示标签
        
        Args:
            frame: 处理后的视频帧（numpy数组，BGR格式）
            result: 检测结果
        """
        # 将OpenCV的BGR格式转换为Qt的RGB格式
        import cv2
        from PyQt5.QtGui import QPixmap, QImage
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 将QImage转换为QPixmap，然后缩放以适应标签大小
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    """主程序入口"""
    # 设置Qt平台插件环境变量
    if hasattr(sys, 'frozen'):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(sys.executable), 'PyQt5', 'Qt', 'plugins', 'platforms')
    else:
        try:
            from PyQt5.QtCore import QCoreApplication
            qt_plugins_path = os.path.join(os.path.dirname(QCoreApplication.__file__), 'Qt', 'plugins', 'platforms')
            if os.path.exists(qt_plugins_path):
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path
        except Exception as e:
            print(f"无法设置Qt平台插件路径: {e}")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # --- 新增：确保加载全局样式 ---
    try:
        from utils.styles import GLOBAL_STYLE
        app.setStyleSheet(GLOBAL_STYLE) # 这一句至关重要！
    except ImportError:
        print("警告：未找到样式文件")
    
    # 设置应用程序样式
    app.setStyle("Fusion")  # 使用Fusion样式，提供更现代的界面
    
    # 创建主窗口实例
    window = MainWindow()
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())
