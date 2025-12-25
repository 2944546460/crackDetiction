#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成线程

用于在后台线程中生成 PDF 报告，避免阻塞 UI
"""

import os
import time
from datetime import datetime
from PyQt5.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from utils.logger import logger
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFExportThread(BaseThread):
    """PDF 导出线程"""
    
    def __init__(self, data):
        """初始化导出线程
        
        Args:
            data: 包含报告数据的字典 (score, crack_penalty, traffic_penalty, diagnosis_text)
        """
        super().__init__()
        self.data = data
        
        # 注册中文字体 (如果存在)
        try:
            # 尝试查找系统字体
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf", # 黑体
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf" # Linux fallback
            ]
            self.font_name = "Helvetica" # 默认
            for path in font_paths:
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont('SourceHanSans', path))
                    self.font_name = 'SourceHanSans'
                    break
        except Exception as e:
            logger.error(f"注册字体失败: {e}")
            self.font_name = "Helvetica"

    def _run(self):
        """执行导出任务"""
        try:
            # 模拟耗时操作，让进度条更明显
            self._update_progress(10)
            time.sleep(0.5)
            
            # 创建保存目录
            output_dir = "reports"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Bridge_Report_{timestamp}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            self._update_progress(30)
            
            # 开始绘制 PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # 标题
            c.setFont(self.font_name, 24)
            c.drawCentredString(width/2, height - 100, "桥梁健康检测评估报告")
            
            # 基本信息
            c.setFont(self.font_name, 12)
            c.drawString(100, height - 150, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, height - 170, f"健康评分: {self.data.get('score', 0)}")
            
            self._update_progress(60)
            time.sleep(0.5)
            
            # 扣分项
            c.drawString(100, height - 210, "评估详情:")
            c.drawString(120, height - 230, f"- 裂缝检测扣分: {self.data.get('crack_penalty', 0)}")
            c.drawString(120, height - 250, f"- 交通荷载扣分: {self.data.get('traffic_penalty', 0)}")
            
            # 诊断建议 (简单处理 HTML 标签)
            diag_text = self.data.get('diagnosis_text', '').replace('<b>', '').replace('</b>', '').replace('<br>', '\n').replace("<font color='#2ecc71'>", "").replace("<font color='#3498db'>", "").replace("<font color='#f1c40f'>", "").replace("<font color='#e74c3c'>", "").replace("</font>", "")
            
            c.drawString(100, height - 300, "诊断建议:")
            y = height - 320
            for line in diag_text.split('\n'):
                if line.strip():
                    c.drawString(120, y, line.strip())
                    y -= 20
            
            self._update_progress(90)
            
            c.showPage()
            c.save()
            
            time.sleep(0.3)
            self._update_progress(100)
            
            self.result_signal.emit({"success": True, "filepath": filepath})
            
        except Exception as e:
            logger.exception("导出 PDF 失败")
            self.result_signal.emit({"success": False, "error": str(e)})
