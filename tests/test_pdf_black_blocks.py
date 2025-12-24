#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出功能，检查文字是否显示为黑块
"""

import sys
import os
import tempfile
from datetime import datetime
import numpy as np
import cv2

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

# 导入测试需要的模块
from views.report_page import ReportPage
from utils.global_state import global_state

class MockDetectionPage(QWidget):
    """模拟检测页面，用于测试图像提取"""
    def __init__(self):
        super().__init__()
        
        # 创建一个简单的结果标签
        self.result_label = QLabel()
        
        # 创建一个测试图像
        # 创建一个红色矩形作为测试
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (255, 255, 255)  # 白色背景
        cv2.rectangle(img, (100, 100), (540, 380), (0, 0, 255), 2)
        cv2.putText(img, "测试裂缝图像", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 转换为QPixmap
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # 设置到标签
        self.result_label.setPixmap(pixmap)
        self.result_label.setAlignment(Qt.AlignCenter)

class MockMainWindow(QMainWindow):
    """模拟主窗口"""
    def __init__(self):
        super().__init__()
        
        # 创建中央部件
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # 创建模拟检测页面
        self.detection_page = MockDetectionPage()
        
        # 创建报告页面
        self.report_page = ReportPage()
        
        # 添加到布局
        layout.addWidget(self.detection_page)
        layout.addWidget(self.report_page)
        
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    # 初始化GlobalState
    global_state.crack_count = 3
    global_state.vehicle_count = 50
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建模拟主窗口
    window = MockMainWindow()
    window.show()
    
    # 先生成报告
    window.report_page._generate_report()
    
    # 然后导出PDF
    print("开始导出PDF...")
    window.report_page._export_pdf()
    
    print("测试完成!")
    sys.exit(app.exec_())