#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告页面修复是否成功
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from views.report_page import ReportPage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局样式
    from utils.styles import GLOBAL_STYLE
    app.setStyleSheet(GLOBAL_STYLE)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("报告页面测试")
    main_window.resize(800, 600)
    
    # 创建中央部件和布局
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # 创建报告页面
    report_page = ReportPage()
    layout.addWidget(report_page)
    
    # 显示仪表盘和诊断区域用于测试
    report_page.dashboard_section.show()
    report_page.diagnosis_section.show()
    
    # 测试更新仪表盘
    report_page._update_gauge(85)  # 设置一个示例分数
    
    main_window.setCentralWidget(central_widget)
    main_window.show()
    
    sys.exit(app.exec_())
