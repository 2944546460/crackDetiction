#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试QMessageBox样式
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from utils.styles import GLOBAL_STYLE


def test_qmessagebox():
    """测试QMessageBox样式"""
    app = QApplication(sys.argv)
    
    # 应用全局样式表
    app.setStyleSheet(GLOBAL_STYLE)
    
    # 显示信息框
    msg_box = QMessageBox()
    msg_box.setWindowTitle("信息测试")
    msg_box.setText("这是一个信息提示框，用于测试样式是否正确应用。")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.addButton("确定", QMessageBox.AcceptRole)
    msg_box.addButton("取消", QMessageBox.RejectRole)
    
    # 显示警告框
    msg_box2 = QMessageBox()
    msg_box2.setWindowTitle("警告测试")
    msg_box2.setText("这是一个警告提示框，用于测试样式是否正确应用。")
    msg_box2.setIcon(QMessageBox.Warning)
    msg_box2.addButton("确定", QMessageBox.AcceptRole)
    
    # 显示信息框
    msg_box.exec_()
    
    # 显示警告框
    msg_box2.exec_()
    
    return 0


if __name__ == "__main__":
    sys.exit(test_qmessagebox())
