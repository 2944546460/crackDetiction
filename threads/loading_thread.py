#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加载线程

用于程序启动时在后台加载模型和配置，更新启动页进度
"""

import time
from PyQt5.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from utils.logger import logger

class LoadingThread(BaseThread):
    """程序启动加载线程"""
    
    # 进度更新信号 (进度百分比, 提示消息)
    loading_status_signal = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.models = {}
        
    def _run(self):
        """执行加载任务"""
        try:
            # 1. 加载配置文件
            self.loading_status_signal.emit(10, "正在读取配置文件...")
            from utils.config_manager import ConfigManager
            config = ConfigManager()
            time.sleep(0.5) # 模拟加载感
            
            # 2. 检查数据库连接
            self.loading_status_signal.emit(30, "正在连接数据库...")
            from utils.db_manager import DBManager
            db = DBManager()
            # 简单检查连接
            db.get_all_projects()
            time.sleep(0.5)
            
            # 3. 加载 YOLO 模型
            self.loading_status_signal.emit(50, "正在初始化 AI 视觉引擎 (YOLO)...")
            from models.yolo_detection import YoloModel
            detection_model = YoloModel()
            detection_model.initialize()
            self.models['detection'] = detection_model
            
            # 4. 加载裂缝分析模型
            self.loading_status_signal.emit(80, "正在加载专家评估系统...")
            from models.yolo_detection import CrackAnalysisModel
            analysis_model = CrackAnalysisModel()
            analysis_model.initialize()
            self.models['analysis'] = analysis_model
            
            # 5. 完成
            self.loading_status_signal.emit(100, "系统就绪，正在启动界面...")
            time.sleep(0.5)
            
            # 发送结果信号，包含加载的模型
            self.result_signal.emit(self.models)
            
        except Exception as e:
            logger.exception("启动加载失败")
            self.error_signal.emit(f"启动加载失败: {str(e)}")
