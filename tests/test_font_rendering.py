#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试PDF字体渲染问题的脚本
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import cv2
import numpy as np

def test_pdf_fonts():
    """测试不同字体配置下的PDF生成"""
    print("开始测试PDF字体渲染...")
    
    # 创建PDF文件
    pdf_filename = f"test_fonts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # 注册中文字体
    use_chinese_font = False
    try:
        simhei_path = "C:\Windows\Fonts\simhei.ttf"
        if os.path.exists(simhei_path):
            pdfmetrics.registerFont(TTFont('SimHei', simhei_path))
            use_chinese_font = True
            print(f"成功注册中文字体: {simhei_path}")
        else:
            print(f"未找到中文字体: {simhei_path}")
    except Exception as font_error:
        print(f"注册中文字体失败: {str(font_error)}")
    
    # 获取默认样式表
    styles = getSampleStyleSheet()
    
    # 测试1: 使用默认样式
    print("测试1: 使用默认样式...")
    default_style = styles['Normal']
    
    # 测试2: 使用自定义样式，不设置文本颜色
    print("测试2: 使用自定义样式，不设置文本颜色...")
    custom_style1 = ParagraphStyle(
        'CustomStyle1',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        fontName='SimHei' if use_chinese_font else 'Helvetica'
    )
    
    # 测试3: 使用自定义样式，显式设置文本颜色为黑色
    print("测试3: 使用自定义样式，显式设置文本颜色为黑色...")
    custom_style2 = ParagraphStyle(
        'CustomStyle2',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        fontName='SimHei' if use_chinese_font else 'Helvetica',
        textColor='#000000'  # 显式设置文本颜色为黑色
    )
    
    # 测试4: 使用自定义样式，显式设置文本颜色为红色
    print("测试4: 使用自定义样式，显式设置文本颜色为红色...")
    custom_style3 = ParagraphStyle(
        'CustomStyle3',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        fontName='SimHei' if use_chinese_font else 'Helvetica',
        textColor='#FF0000'  # 显式设置文本颜色为红色
    )
    
    # 测试5: 使用标题样式
    print("测试5: 使用标题样式...")
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        fontName='SimHei' if use_chinese_font else 'Helvetica-Bold',
        textColor='#000000'
    )
    
    # 准备内容
    flowables = []
    
    flowables.append(Paragraph("PDF字体渲染测试", title_style))
    flowables.append(Spacer(1, 1*cm))
    
    flowables.append(Paragraph("1. 使用默认样式:", styles['Heading2']))
    flowables.append(Paragraph("这是一段使用默认样式的文本。桥梁健康监测报告测试。", default_style))
    flowables.append(Spacer(1, 0.5*cm))
    
    flowables.append(Paragraph("2. 自定义样式（未设置文本颜色）:", styles['Heading2']))
    flowables.append(Paragraph("这是一段使用自定义样式但未设置文本颜色的文本。桥梁健康监测报告测试。", custom_style1))
    flowables.append(Spacer(1, 0.5*cm))
    
    flowables.append(Paragraph("3. 自定义样式（显式黑色文本）:", styles['Heading2']))
    flowables.append(Paragraph("这是一段使用自定义样式并显式设置文本颜色为黑色的文本。桥梁健康监测报告测试。", custom_style2))
    flowables.append(Spacer(1, 0.5*cm))
    
    flowables.append(Paragraph("4. 自定义样式（显式红色文本）:", styles['Heading2']))
    flowables.append(Paragraph("这是一段使用自定义样式并显式设置文本颜色为红色的文本。桥梁健康监测报告测试。", custom_style3))
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
    test_pdf_fonts()