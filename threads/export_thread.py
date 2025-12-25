#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出线程

用于在后台线程中导出数据（Excel等），避免阻塞 UI
"""

import os
import time
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from utils.logger import logger

class ExcelExportThread(BaseThread):
    """Excel 导出线程"""
    
    def __init__(self, data, filename_prefix="Export"):
        """初始化导出线程
        
        Args:
            data: 要导出的数据列表（字典列表）
            filename_prefix: 文件名前缀
        """
        super().__init__()
        self.data = data
        self.filename_prefix = filename_prefix

    def _run(self):
        """执行导出任务"""
        try:
            if not self.data:
                self.result_signal.emit({"success": False, "error": "没有可导出的数据"})
                return

            self._update_progress(10)
            time.sleep(0.3)
            
            # 创建保存目录
            output_dir = "exports"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.filename_prefix}_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)
            
            self._update_progress(30)
            
            # 转换为 DataFrame
            df = pd.DataFrame(self.data)
            
            self._update_progress(60)
            time.sleep(0.5)
            
            # 导出到 Excel
            df.to_excel(filepath, index=False)
            
            self._update_progress(90)
            time.sleep(0.2)
            self._update_progress(100)
            
            self.result_signal.emit({"success": True, "filepath": filepath})
            
        except Exception as e:
            logger.exception("导出 Excel 失败")
            self.result_signal.emit({"success": False, "error": str(e)})
