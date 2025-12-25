#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程基类

提供后台任务线程的通用功能和接口定义
"""

from PyQt5.QtCore import QThread, pyqtSignal
import traceback
import time
from utils.logger import logger

class BaseThread(QThread):
    """后台任务线程基类"""
    
    # 信号定义
    started_signal = pyqtSignal()  # 线程开始信号
    finished_signal = pyqtSignal()  # 线程完成信号
    progress_signal = pyqtSignal(int)  # 进度更新信号 (0-100)
    result_signal = pyqtSignal(object)  # 结果返回信号
    error_signal = pyqtSignal(str)  # 错误信息信号
    frame_processed_signal = pyqtSignal(object, object)  # 视频帧处理完成信号 (frame, result)
    
    def __init__(self):
        """初始化后台任务线程"""
        super().__init__()
        self._is_running = False
        self._is_paused = False
        self._progress = 0
    
    def run(self):
        """线程执行的主方法"""
        self._is_running = True
        self._is_paused = False
        self._progress = 0
        
        try:
            self.started_signal.emit()
            self._run()  # 调用子类实现的具体任务方法
        except Exception as e:
            # 捕获异常并发送错误信号
            error_msg = f"线程执行出错: {str(e)}\n{traceback.format_exc()}"
            logger.exception("线程执行出错")
            self.error_signal.emit(error_msg)
        finally:
            self._is_running = False
            self.finished_signal.emit()
    
    def _run(self):
        """具体任务实现方法，由子类重写"""
        raise NotImplementedError("子类必须实现_run方法")
    
    def start(self):
        """启动线程"""
        if not self._is_running:
            super().start()
    
    def pause(self):
        """暂停线程"""
        if self._is_running and not self._is_paused:
            self._is_paused = True
    
    def resume(self):
        """恢复线程"""
        if self._is_running and self._is_paused:
            self._is_paused = False
    
    def stop(self):
        """停止线程"""
        if self._is_running:
            self._is_running = False
            # 等待线程结束
            self.wait()
    
    def _update_progress(self, progress):
        """更新进度
        
        Args:
            progress: 进度值 (0-100)
        """
        self._progress = max(0, min(100, int(progress)))
        self.progress_signal.emit(self._progress)
    
    def _wait_for_resume(self):
        """等待线程恢复运行"""
        while self._is_paused and self._is_running:
            time.sleep(0.1)  # 短暂休眠，避免CPU占用过高
    
    @property
    def is_running(self):
        """检查线程是否正在运行"""
        return self._is_running
    
    @property
    def is_paused(self):
        """检查线程是否已暂停"""
        return self._is_paused
    
    @property
    def progress(self):
        """获取当前进度"""
        return self._progress
