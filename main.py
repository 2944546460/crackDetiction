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
    # 修复 libiomp5md.dll 冲突
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    
    try:
        # 设置Qt平台插件环境变量
        if hasattr(sys, 'frozen'):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(sys.executable), 'PyQt5', 'Qt', 'plugins', 'platforms')
        else:
            try:
                import PyQt5
                qt_plugins_path = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'plugins', 'platforms')
                if os.path.exists(qt_plugins_path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path
            except Exception as e:
                from utils.logger import logger
                logger.warning(f"无法设置Qt平台插件路径: {e}")
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 导入样式和组件
        from utils.styles import GLOBAL_STYLE
        from views.splash_screen import SplashScreen
        from views.login_dialog import LoginDialog
        from threads.loading_thread import LoadingThread
        from utils.logger import logger
        
        app.setStyleSheet(GLOBAL_STYLE)
        
        # 1. 显示启动页
        splash = SplashScreen()
        splash.show()
        
        # 定义加载完成后的回调
        controller = None
        
        def on_load_finished(models):
            nonlocal controller
            try:
                # 2. 关闭启动页
                splash.close()
                
                # 3. 显示登录对话框
                login = LoginDialog()
                if login.exec_() == LoginDialog.Accepted:
                    # 4. 登录成功，创建并初始化主控制器 (使用加载好的模型)
                    controller = MainController()
                    controller.initialize(models)
                    
                    # 5. 显示主窗口
                    controller.show_main_window()
                    logger.info("系统启动完成")
                else:
                    # 登录取消或失败，退出程序
                    logger.info("用户取消登录，程序退出")
                    sys.exit(0)
            except Exception as e:
                logger.exception("界面初始化失败")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(None, "启动错误", f"界面初始化失败: {str(e)}")
                sys.exit(1)

        def on_load_error(error_msg):
            logger.error(f"加载失败: {error_msg}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "启动错误", error_msg)
            sys.exit(1)
        
        # 4. 启动加载线程
        loader = LoadingThread()
        loader.loading_status_signal.connect(splash.update_progress)
        loader.result_signal.connect(on_load_finished)
        loader.error_signal.connect(on_load_error)
        loader.start()
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        from utils.logger import logger
        logger.exception(f"应用程序启动失败: {e}")
        return 1


if __name__ == "__main__":
    """程序入口点"""
    sys.exit(main())
