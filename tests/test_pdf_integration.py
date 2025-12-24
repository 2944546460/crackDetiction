#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试PDF导出功能
"""

import sys
import os
import time
from datetime import datetime
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import cv2

# 模拟MainWindow和DetectionPage类
class MockDetectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.result_label = QLabel("检测结果")
        self.result_label.setAlignment(0x0084)  # Qt.AlignCenter
        self.result_label.setMinimumSize(640, 480)
        
        # 创建一个测试图像
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "测试裂缝图像", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # 转换为QPixmap并显示
        height, width, channel = test_image.shape
        bytesPerLine = 3 * width
        qimg = QImage(test_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.result_label.setPixmap(pixmap)
        
        layout.addWidget(self.result_label)

class MockMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("模拟主窗口")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建检测页面
        self.detection_page = MockDetectionPage()
        self.setCentralWidget(self.detection_page)

# 模拟GlobalState类
class MockGlobalState:
    def __init__(self):
        self.crack_count = 3
        self.vehicle_count = 100
        self.max_crack_width = 0.5

global_state = MockGlobalState()

# 保存原始的global_state引用
original_global_state = None

# 测试PDF导出
def test_pdf_integration():
    """集成测试PDF导出功能"""
    try:
        # 导入原始的global_state
        from utils import global_state as original_global_state
        
        # 保存原始的全局状态数据
        original_crack_count = original_global_state.crack_count
        original_vehicle_count = original_global_state.vehicle_count
        original_max_crack_width = original_global_state.max_crack_width
        
        # 临时修改全局状态数据
        original_global_state.crack_count = 3
        original_global_state.vehicle_count = 100
        original_global_state.max_crack_width = 0.5
        
        print("✅ 全局状态数据已修改")
        print(f"   裂缝数量: {original_global_state.crack_count}")
        print(f"   车辆数量: {original_global_state.vehicle_count}")
        print(f"   最大裂缝宽度: {original_global_state.max_crack_width}")
        
        # 创建应用程序实例
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建模拟主窗口
        main_window = MockMainWindow()
        
        # 导入ReportPage并测试PDF导出
        from views.report_page import ReportPage
        
        # 创建报告页面
        report_page = ReportPage()
        
        # 模拟生成报告
        report_page._generate_report()
        print("✅ 报告生成完成")
        
        # 模拟导出PDF
        print("\n正在导出PDF...")
        report_page._export_pdf()
        print("✅ PDF导出完成")
        
        # 恢复原始的全局状态数据
        original_global_state.crack_count = original_crack_count
        original_global_state.vehicle_count = original_vehicle_count
        original_global_state.max_crack_width = original_max_crack_width
        
        print("\n🎉 集成测试成功完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 确保恢复原始的全局状态数据
        if original_global_state:
            original_global_state.crack_count = original_crack_count
            original_global_state.vehicle_count = original_vehicle_count
            original_global_state.max_crack_width = original_max_crack_width
        
        return False

if __name__ == "__main__":
    print("开始PDF导出集成测试...")
    success = test_pdf_integration()
    if success:
        print("\n✅ PDF导出功能测试通过！")
        print("请检查生成的PDF文件，确认文字显示正常，没有黑块问题。")
    else:
        print("\n❌ PDF导出功能测试失败！")
