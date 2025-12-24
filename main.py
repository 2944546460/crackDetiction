#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智桥卫士 - 主程序入口

这是程序的入口点，负责初始化应用程序和主控制器。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


def main():
    """主函数"""
    try:
        # 设置Qt平台插件环境变量（解决Qt平台插件加载问题）
        if hasattr(sys, 'frozen'):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(sys.executable), 'PyQt5', 'Qt', 'plugins', 'platforms')
        else:
            try:
                import PyQt5
                qt_plugins_path = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'plugins', 'platforms')
                if os.path.exists(qt_plugins_path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path
            except Exception as e:
                print(f"无法设置Qt平台插件路径: {e}")
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序样式
        app.setStyle("Fusion")  # 使用Fusion样式，提供更现代的界面
        
        # 导入并应用全局样式表
        from utils.styles import GLOBAL_STYLE
        app.setStyleSheet(GLOBAL_STYLE)
        
        # 创建主控制器实例
        controller = MainController()
        
        # 初始化控制器
        controller.initialize()
        
        # 显示主窗口
        controller.show_main_window()
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    """程序入口点"""
    sys.exit(main())
