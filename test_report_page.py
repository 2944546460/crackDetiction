#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评估报告页面UI
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from views.report_page import ReportPage


def test_report_page():
    """测试报告页面UI"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("评估报告页面测试")
    main_window.resize(800, 600)
    
    # 创建中心部件
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    
    # 创建报告页面
    report_page = ReportPage()
    main_layout.addWidget(report_page)
    
    # 设置中心部件
    main_window.setCentralWidget(central_widget)
    
    # 显示窗口
    main_window.show()
    
    # 运行应用
    return app.exec_()


if __name__ == "__main__":
    sys.exit(test_report_page())
