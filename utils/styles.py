#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局样式定义

提供QSS样式表，用于美化整个应用界面
"""

GLOBAL_STYLE = """/* 全局样式 */
* {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

QMainWindow {
    background-color: #f4f6f9;
}

/* 左侧导航栏样式 */
QFrame#nav_frame {
    background-color: #2c3e50;
    border-right: 1px solid #34495e;
}

QPushButton#home_btn,
QPushButton#detection_btn,
QPushButton#traffic_btn,
QPushButton#report_btn,
QPushButton#history_btn,
QPushButton#settings_btn {
    background-color: #2c3e50;
    color: white;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 15px 20px;
    font-size: 14px;
    font-weight: bold;
    border-left: 3px solid transparent;
    letter-spacing: 0.5px;
}

QPushButton#home_btn:hover,
QPushButton#detection_btn:hover,
QPushButton#traffic_btn:hover,
QPushButton#report_btn:hover,
QPushButton#history_btn:hover,
QPushButton#settings_btn:hover {
    background-color: #34495e;
    border-color: #34495e;
}

QPushButton#home_btn:checked,
QPushButton#detection_btn:checked,
QPushButton#traffic_btn:checked,
QPushButton#report_btn:checked,
QPushButton#history_btn:checked,
QPushButton#settings_btn:checked {
    background-color: #34495e;
    border-left: 4px solid #3498db; /* 左侧亮条加粗一点 */
    color: #ffffff;
}

/* 内容卡片样式 */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    margin: 5px;
}

QLabel {
    color: #333333;
}

/* 按钮样式 */
/* 主操作按钮 */
QPushButton#start_btn,
QPushButton#start_monitoring_btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}

QPushButton#start_btn:hover,
QPushButton#start_monitoring_btn:hover {
    background-color: #2980b9;
}

QPushButton#start_btn:pressed,
QPushButton#start_monitoring_btn:pressed {
    background-color: #1f618d;
}

/* 危险按钮 */
QPushButton#stop_btn,
QPushButton#stop_monitoring_btn {
    background-color: #e74c3c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}

QPushButton#stop_btn:hover,
QPushButton#stop_monitoring_btn:hover {
    background-color: #c0392b;
}

QPushButton#stop_btn:pressed,
QPushButton#stop_monitoring_btn:pressed {
    background-color: #a93226;
}

/* 普通按钮 */
QPushButton {
    background-color: white;
    color: #333333;
    border: 1px solid #d0d0d0;
    padding: 10px 20px;
    border-radius: 6px;
}

QPushButton:hover {
    border: 1px solid #3498db;
    color: #3498db;
}

QPushButton:pressed {
    background-color: #f0f8ff;
}

/* 进度条样式 */
QProgressBar {
    background-color: #f0f0f0;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: #333333;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 6px;
}

/* 文本编辑框样式 */
QTextEdit {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 10px;
    color: #333333;
}

/* 标签样式 */
QLabel {
    color: #333333;
    padding: 5px;
}

/* 图像和视频显示标签 */
QLabel#image_display_label,
QLabel#video_display_label {
    background-color: #000000;
    border: 2px solid #34495e;
    border-radius: 8px;
    min-height: 400px;
    color: white;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
}

/* 分隔线样式 */
QSplitter::handle {
    background-color: #e0e0e0;
}

QSplitter::handle:hover {
    background-color: #bdc3c7;
}

/* 弹窗样式 */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #333333;
}

QMessageBox QPushButton {
    color: #000000; /* 确保文字是黑色 */
    background-color: #f0f0f0;
    border: 1px solid #dcdcdc;
    border-radius: 4px;
    padding: 6px 15px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #e0e0e0;
}
"""