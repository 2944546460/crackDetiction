#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动页 (Splash Screen)

在程序启动时显示，展示加载进度
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, 
    QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QColor, QFont

class SplashScreen(QWidget):
    """应用启动页类"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 设置无边框和背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 固定大小
        self.setFixedSize(600, 400)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 背景容器
        self.container = QFrame()
        self.container.setObjectName("SplashContainer")
        self.container.setStyleSheet("""
            #SplashContainer {
                background-color: white;
                border-radius: 20px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # 1. Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        # 尝试加载 logo，如果不存在则显示文字占位
        logo_path = "assets/logo.png"
        if False: # 暂时关闭 logo 加载逻辑，使用文字代替
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("🌉") # 桥梁图标
            self.logo_label.setStyleSheet("font-size: 80px;")
            
        container_layout.addWidget(self.logo_label)
        
        # 2. 软件名称
        self.title_label = QLabel("智桥卫士")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            font-family: 'Microsoft YaHei';
        """)
        container_layout.addWidget(self.title_label)
        
        # 3. 描述
        self.desc_label = QLabel("AI 驱动的桥梁裂缝智能化检测系统")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        container_layout.addWidget(self.desc_label)
        
        container_layout.addStretch()
        
        # 4. 进度信息
        self.status_label = QLabel("正在初始化系统...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #34495e; font-size: 13px;")
        container_layout.addWidget(self.status_label)
        
        # 5. 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ecf0f1;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3498db, stop:1 #2ecc71);
                border-radius: 4px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # 6. 版本号
        self.version_label = QLabel("Version 1.1.0")
        self.version_label.setAlignment(Qt.AlignRight)
        self.version_label.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        container_layout.addWidget(self.version_label)
        
        layout.addWidget(self.container)
        
        # 居中显示
        self._center()
        
    def _center(self):
        """将窗口居中显示"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def update_progress(self, value, message):
        """更新进度
        
        Args:
            value: 进度值 (0-100)
            message: 提示文本
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
