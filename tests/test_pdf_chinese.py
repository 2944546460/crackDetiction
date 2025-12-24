#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF中文显示
"""

import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入reportlab相关模块
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 尝试注册中文字体
def register_chinese_fonts():
    """尝试注册中文字体"""
    # 尝试查找Windows系统字体目录
    if os.name == 'nt':
        font_dirs = [
            'C:\\Windows\\Fonts',
            'C:\\WINNT\\Fonts',
        ]
    else:
        font_dirs = [
            '/usr/share/fonts',
            '/Library/Fonts',
            '~/Library/Fonts',
        ]
    
    # 常用的中文字体文件名
    chinese_fonts = [
        'simhei.ttf',  # 黑体
        'simsun.ttc',  # 宋体
        'msyh.ttf',    # 微软雅黑
        'msyhbd.ttf',  # 微软雅黑粗体
        'simkai.ttf',  # 楷体
    ]
    
    # 尝试找到并注册字体
    registered_fonts = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for font_name in chinese_fonts:
                font_path = os.path.join(font_dir, font_name)
                if os.path.exists(font_path):
                    # 提取字体名（不含扩展名）
                    base_font_name = os.path.splitext(font_name)[0]
                    # 注册字体
                    try:
                        if font_name.endswith('.ttc'):
                            # TrueType Collection需要指定索引
                            pdfmetrics.registerFont(TTFont(base_font_name, font_path, index=0))
                            pdfmetrics.registerFont(TTFont(f'{base_font_name}-Bold', font_path, index=1))
                            registered_fonts.append((base_font_name, font_path))
                            registered_fonts.append((f'{base_font_name}-Bold', font_path))
                        else:
                            pdfmetrics.registerFont(TTFont(base_font_name, font_path))
                            registered_fonts.append((base_font_name, font_path))
                        print(f"✅ 成功注册字体: {base_font_name} -> {font_path}")
                    except Exception as e:
                        print(f"❌ 注册字体失败 {base_font_name}: {str(e)}")
    
    return registered_fonts

# 模拟GlobalState类
class MockGlobalState:
    def __init__(self):
        self.crack_count = 2
        self.vehicle_count = 50

global_state = MockGlobalState()

# 测试PDF生成（中文）
def test_pdf_generation_chinese():
    """测试PDF中文生成功能"""
    try:
        # 计算健康评分
        crack_count = global_state.crack_count
        vehicle_count = global_state.vehicle_count
        bci_score = max(0, min(100, 100 - crack_count * 5 - vehicle_count * 0.1))
        
        # 获取当前时间
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 创建PDF文件
        pdf_filename = f"中文测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        # 设置样式
        styles = getSampleStyleSheet()
        
        # 尝试注册中文字体
        registered_fonts = register_chinese_fonts()
        
        # 准备内容
        flowables = []
        
        # 测试1: 使用Helvetica字体（不支持中文）
        flowables.append(Spacer(1, 1*cm))
        flowables.append(Paragraph("--- 测试1: 使用Helvetica字体（不支持中文） ---", styles['Heading3']))
        flowables.append(Spacer(1, 0.5*cm))
        
        title_style_helvetica = ParagraphStyle(
            'TitleStyleHelvetica',
            parent=styles['Title'],
            fontSize=24,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor='#000000'
        )
        
        normal_style_helvetica = ParagraphStyle(
            'NormalStyleHelvetica',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            fontName='Helvetica',
            textColor='#000000'
        )
        
        flowables.append(Paragraph("桥梁健康监测报告", title_style_helvetica))
        flowables.append(Spacer(1, 0.5*cm))
        flowables.append(Paragraph(f"生成时间: {current_time}", normal_style_helvetica))
        flowables.append(Paragraph(f"桥梁健康评分: {bci_score:.1f}", normal_style_helvetica))
        
        # 测试2: 使用系统中文字体（如果有）
        flowables.append(Spacer(1, 2*cm))
        flowables.append(Paragraph("--- 测试2: 使用系统中文字体（如果有） ---", styles['Heading3']))
        flowables.append(Spacer(1, 0.5*cm))
        
        # 如果有注册的中文字体，使用它
        if registered_fonts:
            # 使用第一个注册的字体
            first_font_name = registered_fonts[0][0]
            
            title_style_chinese = ParagraphStyle(
                'TitleStyleChinese',
                parent=styles['Title'],
                fontSize=24,
                alignment=TA_CENTER,
                fontName=first_font_name,
                textColor='#000000'
            )
            
            normal_style_chinese = ParagraphStyle(
                'NormalStyleChinese',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                fontName=first_font_name,
                textColor='#000000'
            )
            
            flowables.append(Paragraph(f"使用字体: {first_font_name}", normal_style_helvetica))
            flowables.append(Paragraph("桥梁健康监测报告", title_style_chinese))
            flowables.append(Spacer(1, 0.5*cm))
            flowables.append(Paragraph(f"生成时间: {current_time}", normal_style_chinese))
            flowables.append(Paragraph(f"桥梁健康评分: {bci_score:.1f}", normal_style_chinese))
            flowables.append(Paragraph("这是一段中文测试文字，用于验证中文字体是否正常显示。", normal_style_chinese))
        else:
            flowables.append(Paragraph("没有找到可注册的中文字体", normal_style_helvetica))
        
        # 生成PDF
        doc.build(flowables)
        
        print(f"✅ 中文PDF生成成功: {pdf_filename}")
        print(f"📁 文件路径: {pdf_path}")
        
        # 自动打开PDF文件
        if os.path.exists(pdf_path):
            print(f"🔍 尝试打开PDF文件...")
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            else:  # macOS or Linux
                import subprocess
                subprocess.run(['open', pdf_path] if os.name == 'darwin' else ['xdg-open', pdf_path])
            print(f"✅ PDF文件已打开")
        
        return True
        
    except Exception as e:
        print(f"❌ 中文PDF生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试PDF中文显示...")
    success = test_pdf_generation_chinese()
    if success:
        print("\n🎉 测试完成！请检查PDF文件中的中文是否正常显示。")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
