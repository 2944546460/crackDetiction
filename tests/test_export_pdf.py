#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出功能

用于验证导出检测报告功能是否正常工作
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from views.report_page import ReportPage
from views.main_window import MainWindow

def test_export_pdf():
    """测试PDF导出功能"""
    try:
        # 设置模拟数据
        from utils.global_state import global_state
        global_state.update_crack_data(2, 5.5)
        global_state.update_vehicle_count(150)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 创建报告页面
        report_page = ReportPage()
        
        # 测试生成报告
        report_page._generate_report()
        
        # 测试导出PDF
        report_page._export_pdf()
        
        print("PDF导出测试完成")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_export_pdf()
