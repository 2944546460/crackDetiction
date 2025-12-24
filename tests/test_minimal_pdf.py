#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简PDF文本渲染测试脚本
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def test_minimal_pdf():
    """创建一个极简的PDF文件，仅包含文本内容，用于测试文字渲染"""
    print("创建极简PDF测试文件...")
    
    # 创建PDF文件
    pdf_filename = f"minimal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # 尝试注册系统字体
    fonts_to_test = [
        ('SimHei', 'C:\\Windows\\Fonts\\simhei.ttf'),
        ('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc'),
    ]
    
    font_registered = False
    for font_name, font_path in fonts_to_test:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"成功注册字体: {font_name} - {font_path}")
                font_registered = True
                break
            except Exception as e:
                print(f"注册字体失败 {font_name}: {str(e)}")
    
    # 设置样式
    styles = []
    
    # 测试1: 使用系统字体
    if font_registered:
        styles.append(ParagraphStyle(
            'ChineseStyle',
            parent=None,
            fontSize=12,
            alignment=TA_LEFT,
            fontName=font_name,
            textColor='#000000',
            backColor='#ffffff'
        ))
    
    # 测试2: 使用Helvetica字体（ReportLab内置）
    styles.append(ParagraphStyle(
        'HelveticaStyle',
        parent=None,
        fontSize=12,
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor='#000000',
        backColor='#ffffff'
    ))
    
    # 测试3: 使用Helvetica-Bold字体
    styles.append(ParagraphStyle(
        'HelveticaBoldStyle',
        parent=None,
        fontSize=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        textColor='#000000',
        backColor='#ffffff'
    ))
    
    # 准备内容
    flowables = []
    
    # 添加标题
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=None,
        fontSize=18,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor='#000000',
        backColor='#ffffff'
    )
    
    flowables.append(Paragraph("PDF文本渲染测试", title_style))
    flowables.append(Spacer(1, 1*cm))
    
    # 添加测试内容
    content_tests = [
        "这是一段中文测试文本：桥梁健康监测报告",
        "This is an English test text: Bridge Health Monitoring Report"
    ]
    
    for i, style in enumerate(styles):
        flowables.append(Paragraph(f"样式 {i+1} ({style.fontName}):", style))
        for content in content_tests:
            flowables.append(Paragraph(content, style))
        flowables.append(Spacer(1, 0.5*cm))
    
    # 生成PDF
    doc.build(flowables)
    print(f"PDF生成完成: {pdf_path}")
    
    # 自动打开PDF
    if os.path.exists(pdf_path):
        if os.name == 'nt':  # Windows
            os.startfile(pdf_path)
        else:  # macOS or Linux
            import subprocess
            subprocess.run(['open', pdf_path] if os.name == 'darwin' else ['xdg-open', pdf_path])
    
    print("测试完成!")

if __name__ == "__main__":
    test_minimal_pdf()