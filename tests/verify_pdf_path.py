#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证PDF导出路径是否正确的测试脚本
"""

import sys
import os
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import cv2

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
    print("开始验证PDF导出路径...")
    
    # 检查reports目录是否存在
    reports_dir = os.path.join(os.getcwd(), "reports")
    if not os.path.exists(reports_dir):
        print(f"创建reports目录: {reports_dir}")
        os.makedirs(reports_dir)
    else:
        print(f"reports目录已存在: {reports_dir}")
    
    # 初始化GlobalState
    global_state.crack_count = 2
    global_state.vehicle_count = 30
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建模拟主窗口
    window = MockMainWindow()
    
    # 显示窗口
    window.show()
    
    # 先生成报告
    print("生成评估报告...")
    window.report_page._generate_report()
    
    # 然后导出PDF
    print("导出PDF...")
    window.report_page._export_pdf()
    
    # 检查reports目录是否有新的PDF文件
    pdf_files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf') and '桥梁健康监测报告' in f]
    if pdf_files:
        latest_pdf = sorted(pdf_files)[-1]
        latest_pdf_path = os.path.join(reports_dir, latest_pdf)
        print(f"✓ PDF文件已成功导出到reports目录: {latest_pdf_path}")
    else:
        print("✗ 未在reports目录中找到新的PDF文件")
    
    print("测试完成!")
    sys.exit(0)