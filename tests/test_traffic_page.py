#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试交通荷载页面

专门测试TrafficPage类的实时折线图功能
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from views.traffic_page import TrafficPage


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("交通荷载页面测试")
    window.resize(1000, 600)
    
    # 创建中心部件
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # 添加TrafficPage
    traffic_page = TrafficPage()
    layout.addWidget(traffic_page)
    
    # 设置中心部件
    window.setCentralWidget(central_widget)
    
    # 显示窗口
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()