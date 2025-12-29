#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估报告页面

用于计算桥梁健康评分 (BCI) 并生成评估报告（精修版）
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QSpinBox,
    QPushButton, QLabel, QFrame, QHBoxLayout,
    QTextBrowser, QSizePolicy, QMessageBox, QProgressDialog
)
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ReportPage(QWidget):
    """评估报告页面类"""
    
    def __init__(self):
        super().__init__()
        # 设置中文字体
        rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']
        self._init_ui()
    
    def showEvent(self, event):
        """每次页面显示时，自动加载最新数据"""
        super().showEvent(event)
        self._load_global_state_data()

    def _init_ui(self):
        """初始化UI组件"""
        self.setStyleSheet("background-color: #f4f6f9;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 1. 标题
        title_label = QLabel("评估报告")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei'; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 2. 参数输入卡片 (Form Section)
        form_section = QFrame()
        form_section.setObjectName("form_card")
        form_section.setStyleSheet("""
            QFrame#form_card { 
                background-color: #ffffff; 
                border: 1px solid #e0e0e0; 
                border-radius: 10px; 
                padding: 20px; 
            }
        """)
        
        # 使用水平布局包裹内部内容
        form_container_layout = QHBoxLayout(form_section)
        form_container_layout.setSpacing(40)
        form_container_layout.setContentsMargins(40, 20, 40, 20)
        
        # 左侧：输入表单 (使用 Grid Layout 对齐)
        inputs_layout = QGridLayout()
        inputs_layout.setHorizontalSpacing(15)
        inputs_layout.setVerticalSpacing(15)
        
        # 裂缝扣分
        lb_crack = QLabel("裂缝检测扣分:")
        lb_crack.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        self.crack_spinbox = QSpinBox()
        self.crack_spinbox.setRange(0, 100)
        self.crack_spinbox.setSuffix(" 分") # 添加单位
        self.crack_spinbox.setFixedWidth(120)
        self.crack_spinbox.setFixedHeight(35)
        self.crack_spinbox.setStyleSheet("QSpinBox { border: 1px solid #ccc; border-radius: 4px; padding-left: 10px; font-size: 14px; }")
        
        inputs_layout.addWidget(lb_crack, 0, 0)
        inputs_layout.addWidget(self.crack_spinbox, 0, 1)
        
        # 交通荷载扣分
        lb_traffic = QLabel("交通荷载扣分:")
        lb_traffic.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        self.traffic_spinbox = QSpinBox()
        self.traffic_spinbox.setRange(0, 100)
        self.traffic_spinbox.setSuffix(" 分")
        self.traffic_spinbox.setFixedWidth(120)
        self.traffic_spinbox.setFixedHeight(35)
        self.traffic_spinbox.setStyleSheet("QSpinBox { border: 1px solid #ccc; border-radius: 4px; padding-left: 10px; font-size: 14px; }")
        
        inputs_layout.addWidget(lb_traffic, 1, 0)
        inputs_layout.addWidget(self.traffic_spinbox, 1, 1)
        
        # 右侧：生成按钮
        self.generate_btn = QPushButton("生成/刷新 报告")
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setMinimumWidth(150)
        self.generate_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border: none; 
                border-radius: 6px; 
                font-size: 15px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1f618d; }
        """)
        self.generate_btn.clicked.connect(self._generate_report)
        
        # 将输入布局和按钮添加到容器
        form_container_layout.addLayout(inputs_layout)
        form_container_layout.addStretch() # 中间弹簧
        form_container_layout.addWidget(self.generate_btn)
        
        main_layout.addWidget(form_section)
        
        # 3. 仪表盘区域 (Dashboard Section)
        self.dashboard_section = QFrame()
        self.dashboard_section.setObjectName("dashboard_card")
        self.dashboard_section.setStyleSheet("""
            QFrame#dashboard_card { 
                background-color: #ffffff; 
                border: 1px solid #e0e0e0; 
                border-radius: 10px; 
                padding: 20px; 
            }
        """)
        self.dashboard_layout = QVBoxLayout(self.dashboard_section)
        
        dash_title = QLabel("桥梁健康度仪表盘")
        dash_title.setAlignment(Qt.AlignCenter)
        dash_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self.dashboard_layout.addWidget(dash_title)
        
        # 初始化 Matplotlib 仪表盘
        self._init_gauge()
        
        main_layout.addWidget(self.dashboard_section, 2) # 权重设为2，占据更多空间
        
        # 4. 详细诊断建议 (Diagnosis Section)
        self.diagnosis_section = QFrame()
        self.diagnosis_section.setObjectName("diagnosis_card")
        self.diagnosis_section.setStyleSheet("""
            QFrame#diagnosis_card { 
                background-color: #ffffff; 
                border: 1px solid #e0e0e0; 
                border-radius: 10px; 
                padding: 20px; 
            }
        """)
        diag_layout = QVBoxLayout(self.diagnosis_section)
        
        diag_title = QLabel("详细诊断建议")
        diag_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        diag_layout.addWidget(diag_title)
        
        self.diagnosis_text = QTextBrowser()
        self.diagnosis_text.setReadOnly(True)
        self.diagnosis_text.setStyleSheet("border: none; background: transparent; font-size: 14px; line-height: 24px; color: #555;")
        self.diagnosis_text.setPlaceholderText("请点击生成报告查看详情...")
        diag_layout.addWidget(self.diagnosis_text)
        
        main_layout.addWidget(self.diagnosis_section, 1)
        
        # 5. 导出 PDF 按钮
        self.export_btn = QPushButton("导出 PDF 报告")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedSize(200, 45)
        self.export_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 22px; 
                font-size: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.export_btn.clicked.connect(self._export_pdf)
        self.export_btn.hide() # 初始隐藏
        
        main_layout.addWidget(self.export_btn, alignment=Qt.AlignCenter)

    def _init_gauge(self):
        """初始化仪表盘"""
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_alpha(0)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(200, 200)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.dashboard_layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal') # 有了 MinimumSize 保护，这里设置 aspect 是安全的
        self.ax.set_facecolor('none')
        
        # 绘制底部灰色半圆
        self.gauge_arc = self.ax.pie(
            [100], startangle=180, colors=['#f0f0f0'], radius=1.0, 
            wedgeprops={'width': 0.3, 'edgecolor': 'none'}
        )[0][0]
        
        # 绘制进度条（初始0）
        self.score_arc = self.ax.pie(
            [0, 100], startangle=180, colors=['#3498db', 'none'], radius=1.0, 
            wedgeprops={'width': 0.3, 'edgecolor': 'none'}
        )[0][0]
        
        # 中心文字 (修正：字体改小，防止溢出)
        self.score_text = self.ax.text(
            0, -0.1, '0', 
            ha='center', va='center', 
            fontsize=36,  # 字体从48减小到36
            fontweight='bold', 
            color='#3498db'
        )
        
        self.unit_text = self.ax.text(
            0, -0.4, '健康评分', 
            ha='center', va='center', 
            fontsize=14, color='#999'
        )
        
        self.ax.axis('off')
        try:
            self.figure.tight_layout()
        except:
            pass

    def _update_gauge(self, score):
        """更新仪表盘动画"""
        # 角度计算
        score = max(0, min(100, score))
        score_ratio = score / 100.0
        
        # 这里的逻辑是：Pie chart从180度开始逆时针画
        # 我们需要画一个扇形代表分数
        
        # 颜色分级
        if score >= 90: color = '#2ecc71' # 优
        elif score >= 75: color = '#3498db' # 良
        elif score >= 60: color = '#f1c40f' # 中
        else: color = '#e74c3c' # 差
        
        # 更新数据: [分数对应的份额, 剩余份额(透明)]
        # 注意：matplotlib pie chart 更新数据比较麻烦，这里简单重绘
        self.ax.clear()
        self.ax.axis('off')
        
        # 重绘底色
        self.ax.pie([100], startangle=180, colors=['#f0f0f0'], radius=1.0, 
                   wedgeprops={'width': 0.3, 'edgecolor': 'none'})
        
        # 重绘进度
        # 180度是半圆，所以数据要是 [score, 100-score] 但要在半圆内，
        # 所以总数应该是200，[score, 100-score, 100(下半圆透明)]
        self.ax.pie(
            [score, 100-score, 100], 
            startangle=180, 
            colors=[color, '#f0f0f0', 'none'], # 未完成部分用灰色，下半圆透明
            radius=1.0,
            wedgeprops={'width': 0.3, 'edgecolor': 'none'}
        )
        
        # 重绘文字
        self.ax.text(0, -0.1, str(int(score)), ha='center', va='center', 
                    fontsize=36, fontweight='bold', color=color)
        self.ax.text(0, -0.4, '健康评分', ha='center', va='center', 
                    fontsize=14, color='#999')
        
        self.canvas.draw()

    def _load_global_state_data(self):
        """从全局状态加载数据"""
        from utils.global_state import global_state
        
        # 读取数据
        c_count = global_state.crack_count
        v_count = global_state.vehicle_count
        
        # 简单的扣分逻辑演示
        c_penalty = min(50, c_count * 5)
        v_penalty = min(50, v_count * 0.5)
        
        self.crack_spinbox.setValue(int(c_penalty))
        self.traffic_spinbox.setValue(int(v_penalty))
        
        # 自动刷新报告
        self._generate_report()

    def _generate_report(self):
        """生成报告逻辑"""
        c_pen = self.crack_spinbox.value()
        t_pen = self.traffic_spinbox.value()
        
        score = 100 - c_pen - t_pen
        self._update_gauge(score)
        
        # 生成诊断文案
        text = "<b>诊断报告摘要：</b><br><br>"
        if score >= 90:
            text += "<font color='#2ecc71'>[A级] 结构状况优良。</font> 未发现明显病害，交通荷载在正常范围内。<br>"
        elif score >= 75:
            text += "<font color='#3498db'>[B级] 结构状况良好。</font> 存在轻微裂缝或交通量略大，建议保持常规巡查。<br>"
        elif score >= 60:
            text += "<font color='#f1c40f'>[C级] 结构状况合格。</font> 病害发展较为明显，需加强针对性监测。<br>"
        else:
            text += "<font color='#e74c3c'>[D级] 结构状况不合格！</font> 裂缝严重或超载严重，建议立即进行详细检测或限行。<br>"
            
        text += f"<br>详细数据：<br>- 裂缝扣分：{c_pen}<br>- 荷载扣分：{t_pen}"
        self.diagnosis_text.setHtml(text)
        
        self.export_btn.show()

    def _export_pdf(self):
        """导出PDF报告"""
        try:
            # 准备数据
            data = {
                "score": 100 - self.crack_spinbox.value() - self.traffic_spinbox.value(),
                "crack_penalty": self.crack_spinbox.value(),
                "traffic_penalty": self.traffic_spinbox.value(),
                "diagnosis_text": self.diagnosis_text.toHtml()
            }
            
            # 创建进度对话框
            self.progress_dialog = QProgressDialog("正在生成 PDF 报告...", "取消", 0, 100, self)
            self.progress_dialog.setWindowTitle("导出中")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setAutoClose(True)
            
            # 创建并启动导出线程
            from threads.report_thread import PDFExportThread
            self.export_thread = PDFExportThread(data)
            self.export_thread.progress_signal.connect(self.progress_dialog.setValue)
            self.export_thread.result_signal.connect(self._on_export_finished)
            
            # 连接取消按钮
            self.progress_dialog.canceled.connect(self.export_thread.stop)
            
            self.export_thread.start()
            self.progress_dialog.show()
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出 PDF 报告时发生错误: {str(e)}")

    def _on_export_finished(self, result):
        """导出完成事件"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        if result.get("success"):
            filepath = result.get("filepath")
            QMessageBox.information(self, "导出成功", f"PDF 报告已成功导出至：\n{filepath}")
        else:
            QMessageBox.critical(self, "导出失败", f"导出 PDF 报告失败: {result.get('error')}")