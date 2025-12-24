#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估报告页面

用于计算桥梁健康评分 (BCI) 并生成评估报告
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QSpinBox,
    QPushButton, QLabel, QFrame, QMessageBox, QHBoxLayout,
    QTextBrowser
)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ReportPage(QWidget):
    """评估报告页面类"""
    
    def __init__(self):
        """初始化评估报告页面"""
        super().__init__()
        
        # 设置中文字体
        rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']
        
        self._init_ui()
        self._load_global_state_data()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 设置页面背景色
        self.setStyleSheet("background-color: #f4f6f9;")
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("评估报告")
        title_label.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; margin-bottom: 10px; font-family: 'Microsoft YaHei'; color: #333333; }")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建表单区（横向排列）
        form_section = QFrame()
        form_section.setObjectName("form_card")
        form_section.setStyleSheet("QFrame#form_card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); }")
        form_layout = QHBoxLayout(form_section)
        form_layout.setSpacing(30)
        form_layout.setAlignment(Qt.AlignCenter)
        
        # 创建裂缝检测扣分区域
        crack_layout = QVBoxLayout()
        crack_label = QLabel("裂缝检测扣分")
        crack_label.setStyleSheet("QLabel { font-size: 14px; color: #666666; margin-bottom: 5px; font-family: 'Microsoft YaHei'; }")
        self.crack_spinbox = QSpinBox()
        self.crack_spinbox.setRange(0, 100)
        self.crack_spinbox.setValue(0)
        self.crack_spinbox.setStyleSheet("QSpinBox { padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'Microsoft YaHei'; }")
        crack_layout.addWidget(crack_label)
        crack_layout.addWidget(self.crack_spinbox)
        
        # 创建交通荷载扣分区域
        traffic_layout = QVBoxLayout()
        traffic_label = QLabel("交通荷载扣分")
        traffic_label.setStyleSheet("QLabel { font-size: 14px; color: #666666; margin-bottom: 5px; font-family: 'Microsoft YaHei'; }")
        self.traffic_spinbox = QSpinBox()
        self.traffic_spinbox.setRange(0, 100)
        self.traffic_spinbox.setValue(0)
        self.traffic_spinbox.setStyleSheet("QSpinBox { padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'Microsoft YaHei'; }")
        traffic_layout.addWidget(traffic_label)
        traffic_layout.addWidget(self.traffic_spinbox)
        
        # 创建生成报告按钮
        self.generate_btn = QPushButton("生成评估报告")
        self.generate_btn.setObjectName("start_btn")
        self.generate_btn.setStyleSheet("QPushButton#start_btn { background-color: #3498db; color: white; border: none; border-radius: 4px; padding: 10px 20px; font-size: 14px; font-weight: bold; font-family: 'Microsoft YaHei'; }")
        self.generate_btn.clicked.connect(self._generate_report)
        
        # 添加到横向布局
        form_layout.addLayout(crack_layout)
        form_layout.addLayout(traffic_layout)
        form_layout.addWidget(self.generate_btn)
        
        main_layout.addWidget(form_section)
        
        # 创建仪表盘区域
        self.dashboard_section = QFrame()
        self.dashboard_section.setObjectName("dashboard_card")
        self.dashboard_section.setStyleSheet("QFrame#dashboard_card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); }")
        self.dashboard_layout = QVBoxLayout(self.dashboard_section)
        self.dashboard_section.hide()
        
        # 创建仪表盘标题
        dashboard_title = QLabel("桥梁健康度仪表盘")
        dashboard_title.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 30px; text-align: center; font-family: 'Microsoft YaHei'; }")
        self.dashboard_layout.addWidget(dashboard_title)
        
        # 创建仪表盘画布
        self._init_gauge()
        
        main_layout.addWidget(self.dashboard_section)
        
        # 创建详细诊断建议卡片
        self.diagnosis_section = QFrame()
        self.diagnosis_section.setObjectName("diagnosis_card")
        self.diagnosis_section.setStyleSheet("QFrame#diagnosis_card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); }")
        diagnosis_layout = QVBoxLayout(self.diagnosis_section)
        
        # 创建诊断建议标题
        diagnosis_title = QLabel("详细诊断建议")
        diagnosis_title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; color: #333333; margin-bottom: 15px; font-family: 'Microsoft YaHei'; }")
        diagnosis_layout.addWidget(diagnosis_title)
        
        # 创建QTextBrowser显示诊断文本
        self.diagnosis_text = QTextBrowser()
        self.diagnosis_text.setReadOnly(True)
        self.diagnosis_text.setStyleSheet("QTextBrowser { background-color: transparent; border: none; font-family: 'Microsoft YaHei'; font-size: 14px; color: #666666; }")
        self.diagnosis_text.setPlaceholderText("点击'生成评估报告'查看详细诊断建议")
        diagnosis_layout.addWidget(self.diagnosis_text)
        
        self.diagnosis_section.hide()
        main_layout.addWidget(self.diagnosis_section)
        
        # 创建导出PDF按钮
        self.export_btn = QPushButton("导出 PDF")
        self.export_btn.setObjectName("start_btn")
        self.export_btn.setStyleSheet("QPushButton#start_btn { background-color: #3498db; color: white; border: none; border-radius: 4px; padding: 12px 30px; font-size: 14px; font-weight: bold; font-family: 'Microsoft YaHei'; margin-top: 20px; }")
        self.export_btn.clicked.connect(self._export_pdf)
        self.export_btn.hide()
        main_layout.addWidget(self.export_btn, alignment=Qt.AlignCenter)
    
    def _init_gauge(self):
        """初始化仪表盘"""
        # 创建Figure对象
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_alpha(0)  # 透明背景
        
        # 创建画布
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.dashboard_layout.addWidget(self.canvas)
        
        # 创建仪表盘图表
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('none')  # 透明背景
        
        # 设置仪表盘参数
        self.gauge_min = 0
        self.gauge_max = 100
        
        # 绘制半圆环
        self.gauge_arc = self.ax.pie(
            [100],  # 一个完整的饼图
            startangle=180,  # 从180度开始
            colors=['#e0e0e0'],  # 背景色
            radius=0.8,  # 半径
            wedgeprops={'width': 0.2, 'edgecolor': 'none'}
        )[0][0]
        
        # 绘制分数进度
        self.score_arc = self.ax.pie(
            [0, 100],  # 分数和剩余部分
            startangle=180,  # 从180度开始
            colors=['#3498db', 'none'],  # 分数颜色和透明
            radius=0.8,  # 半径
            wedgeprops={'width': 0.2, 'edgecolor': 'none'}
        )[0][0]
        
        # 在中间绘制分数
        self.score_text = self.ax.text(
            0, 0, '0', 
            ha='center', va='center', 
            fontsize=60, fontweight='bold', 
            color='#3498db'
        )
        
        # 在底部绘制单位
        self.unit_text = self.ax.text(
            0, -0.2, '健康评分', 
            ha='center', va='center', 
            fontsize=20, color='#666666'
        )
        
        # 隐藏坐标轴
        self.ax.axis('off')
        
        # 调整布局
        self.figure.tight_layout()
    
    def _update_gauge(self, score):
        """更新仪表盘显示
        
        Args:
            score: 桥梁健康评分
        """
        # 计算分数占比
        score_ratio = score / 100
        
        # 更新分数进度
        self.score_arc.set_theta1(180)
        self.score_arc.set_theta2(180 + score_ratio * 180)
        
        # 根据分数设置颜色
        if score > 80:
            color = '#27ae60'  # 绿色
        elif score > 60:
            color = '#f39c12'  # 黄色
        else:
            color = '#e74c3c'  # 红色
        
        self.score_arc.set_color(color)
        self.score_text.set_text(str(int(score)))
        self.score_text.set_color(color)
        
        # 刷新图表
        self.canvas.draw()
    
    def _generate_report(self):
        """生成评估报告"""
        # 计算BCI分数
        crack_penalty = self.crack_spinbox.value()
        traffic_penalty = self.traffic_spinbox.value()
        
        # 基础分为100，减去各项扣分
        bci_score = 100 - crack_penalty - traffic_penalty
        
        # 确保分数在0-100之间
        bci_score = max(0, min(100, bci_score))
        
        # 更新仪表盘
        self._update_gauge(bci_score)
        
        # 根据分数生成诊断建议
        diagnosis_text = self._generate_diagnosis(bci_score, crack_penalty, traffic_penalty)
        
        # 更新诊断建议文本
        self.diagnosis_text.setText(diagnosis_text)
        
        # 显示仪表盘和诊断建议区域
        self.dashboard_section.show()
        self.diagnosis_section.show()
        self.export_btn.show()
    
    def _generate_diagnosis(self, bci_score, crack_penalty, traffic_penalty):
        """根据分数生成诊断建议
        
        Args:
            bci_score: 桥梁健康评分
            crack_penalty: 裂缝检测扣分
            traffic_penalty: 交通荷载扣分
            
        Returns:
            str: 诊断建议文本
        """
        diagnosis = []
        
        # 裂缝检测建议
        if crack_penalty == 0:
            diagnosis.append("1. 裂缝检测：未发现明显裂缝，结构整体完好。")
        elif crack_penalty < 30:
            diagnosis.append(f"1. 裂缝检测：检测到轻微裂缝，建议加强日常巡查，定期观察裂缝变化情况。")
        elif crack_penalty < 60:
            diagnosis.append(f"1. 裂缝检测：检测到中度裂缝，建议及时进行维修加固处理。")
        else:
            diagnosis.append(f"1. 裂缝检测：检测到严重裂缝，建议立即采取措施进行紧急维修。")
        
        # 交通荷载建议
        if traffic_penalty == 0:
            diagnosis.append("2. 交通荷载：当前荷载状况良好，未发现超限情况。")
        elif traffic_penalty < 30:
            diagnosis.append(f"2. 交通荷载：当前荷载状况基本正常，建议适当控制重型车辆通行。")
        elif traffic_penalty < 60:
            diagnosis.append(f"2. 交通荷载：当前荷载状况较重，建议限制重型车辆通行，加强监控。")
        else:
            diagnosis.append(f"2. 交通荷载：当前荷载状况严重超限，建议立即采取限行措施并进行加固。")
        
        # 综合建议
        if bci_score > 80:
            diagnosis.append("\n3. 综合评估：桥梁整体健康状况良好，建议保持定期检查即可。")
        elif bci_score > 60:
            diagnosis.append("\n3. 综合评估：桥梁整体健康状况一般，建议按照上述建议进行维修和管理。")
        else:
            diagnosis.append("\n3. 综合评估：桥梁整体健康状况较差，建议立即委托专业机构进行全面检测和维修。")
        
        return "\n".join(diagnosis)
    
    def _export_pdf(self):
        """导出PDF报告"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm, inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from datetime import datetime
            import os
            import subprocess
            import cv2
            import numpy as np
            from PyQt5.QtGui import QPixmap, QImage
            
            # 从GlobalState获取最新数据
            from utils.global_state import global_state
            crack_count = global_state.crack_count
            vehicle_count = global_state.vehicle_count
            
            # 计算健康评分
            bci_score = max(0, min(100, 100 - crack_count * 5 - vehicle_count * 0.1))
            
            # 获取当前时间
            current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            
            # 创建PDF文件
            pdf_filename = f"桥梁健康监测报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            # 确保reports目录存在
            reports_dir = os.path.join(os.getcwd(), "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            pdf_path = os.path.join(reports_dir, pdf_filename)
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            
            # 注册中文字体
            try:
                # 尝试注册黑体字体
                simhei_path = "C:\\Windows\\Fonts\\simhei.ttf"
                if os.path.exists(simhei_path):
                    pdfmetrics.registerFont(TTFont('SimHei', simhei_path))
                    use_chinese_font = True
                else:
                    use_chinese_font = False
            except Exception as font_error:
                print(f"注册中文字体失败: {str(font_error)}")
                use_chinese_font = False
            
            # 设置样式
            styles = getSampleStyleSheet()
            
            # 根据是否有中文字体选择合适的字体
            title_font = 'SimHei' if use_chinese_font else 'Helvetica-Bold'
            normal_font = 'SimHei' if use_chinese_font else 'Helvetica'
            
            # 修复文本显示为黑块的问题：确保所有文本样式都显式设置了文本颜色和背景
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=None,  # 不继承默认样式，避免可能的冲突
                fontSize=24,
                alignment=TA_CENTER,
                fontName=title_font,
                textColor='#000000',  # 显式设置文本颜色为黑色
                backColor='#ffffff',  # 显式设置背景颜色为白色
                spaceAfter=12
            )
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=None,  # 不继承默认样式，避免可能的冲突
                fontSize=16,
                alignment=TA_CENTER,
                fontName=title_font,
                textColor='#000000',  # 显式设置文本颜色为黑色
                backColor='#ffffff',  # 显式设置背景颜色为白色
                spaceAfter=8
            )
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=None,  # 不继承默认样式，避免可能的冲突
                fontSize=12,
                alignment=TA_LEFT,
                fontName=normal_font,
                textColor='#000000',  # 显式设置文本颜色为黑色
                backColor='#ffffff',  # 显式设置背景颜色为白色
                spaceAfter=6
            )
            
            # 准备内容
            flowables = []
            
            # 添加标题
            flowables.append(Paragraph("桥梁健康监测报告", title_style))
            flowables.append(Spacer(1, 2*cm))
            
            # 添加时间
            flowables.append(Paragraph(f"生成时间: {current_time}", normal_style))
            flowables.append(Spacer(1, 1*cm))
            
            # 添加健康评分
            flowables.append(Paragraph("结论：", subtitle_style))
            flowables.append(Spacer(1, 0.5*cm))
            flowables.append(Paragraph(f"桥梁健康评分: <b>{bci_score:.1f}</b>", normal_style))
            flowables.append(Spacer(1, 1*cm))
            
            # 获取裂缝检测图像
            image_added = False
            try:
                # 尝试从detection_page获取检测结果图像
                from views.main_window import MainWindow
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                
                if app:
                    for widget in app.topLevelWidgets():
                        if isinstance(widget, MainWindow):
                            main_window = widget
                            if hasattr(main_window, 'detection_page'):
                                detection_page = main_window.detection_page
                                if hasattr(detection_page, 'result_label'):
                                    pixmap = detection_page.result_label.pixmap()
                                    if not pixmap.isNull():
                                        # 将QPixmap转换为numpy数组
                                        image = pixmap.toImage()
                                        s = image.bits().asstring(image.byteCount())
                                        img_array = np.frombuffer(s, dtype=np.uint8)
                                        img_array = img_array.reshape(image.height(), image.width(), 4)
                                        
                                        # 保存为临时图像
                                        temp_image_path = "temp_detection_result.png"
                                        cv2.imwrite(temp_image_path, cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR))
                                        
                                        # 添加图像到PDF
                                        flowables.append(Paragraph("证据：裂缝检测结果", subtitle_style))
                                        flowables.append(Spacer(1, 0.5*cm))
                                        
                                        # 调整图像大小
                                        img = Image(temp_image_path)
                                        img_width = 15*cm
                                        img_height = img_width * (img.imageHeight / img.imageWidth)
                                        img.drawWidth = img_width
                                        img.drawHeight = img_height
                                        img.hAlign = 'CENTER'
                                        flowables.append(img)
                                        
                                        # 删除临时文件
                                        if os.path.exists(temp_image_path):
                                            os.remove(temp_image_path)
                                        
                                        image_added = True
                                    break
            except Exception as img_error:
                print(f"获取检测图像失败: {str(img_error)}")
            
            # 如果没有添加图像，显示提示信息
            if not image_added:
                flowables.append(Paragraph("证据：未获取到检测图像", normal_style))
            
            # 生成PDF
            doc.build(flowables)
            
            # 自动打开PDF文件
            if os.path.exists(pdf_path):
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                else:  # macOS or Linux
                    subprocess.run(['open', pdf_path] if os.name == 'darwin' else ['xdg-open', pdf_path])
                
                QMessageBox.information(self, "导出成功", f"PDF报告已生成并打开：{pdf_filename}")
            else:
                QMessageBox.critical(self, "导出失败", "PDF文件生成失败")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "导出错误", f"PDF导出失败：{str(e)}")
    
    def _load_global_state_data(self):
        """加载全局状态数据并自动计算健康分"""
        from utils.global_state import global_state
        
        # 获取全局状态中的数据
        crack_count = global_state.crack_count
        max_crack_width = global_state.max_crack_width
        vehicle_count = global_state.vehicle_count
        
        # 计算扣分
        crack_penalty = crack_count * 5  # 每条裂缝扣5分
        traffic_penalty = vehicle_count * 0.1  # 每辆车扣0.1分
        
        # 确保扣分在0-100之间
        crack_penalty = max(0, min(100, crack_penalty))
        traffic_penalty = max(0, min(100, traffic_penalty))
        
        # 更新输入框
        self.crack_spinbox.setValue(int(crack_penalty))
        self.traffic_spinbox.setValue(int(traffic_penalty))
        
        # 自动生成报告
        self._generate_report()