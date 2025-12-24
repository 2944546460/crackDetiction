#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出修复是否有效
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

# 模拟GlobalState类
class MockGlobalState:
    def __init__(self):
        self.crack_count = 2
        self.vehicle_count = 50

global_state = MockGlobalState()

# 测试PDF生成
def test_pdf_generation():
    """测试PDF生成功能"""
    try:
        # 计算健康评分
        crack_count = global_state.crack_count
        vehicle_count = global_state.vehicle_count
        bci_score = max(0, min(100, 100 - crack_count * 5 - vehicle_count * 0.1))
        
        # 获取当前时间
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 创建PDF文件
        pdf_filename = f"测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        # 设置样式
        styles = getSampleStyleSheet()
        
        # 修复后：明确设置文字颜色为黑色
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=24,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor='#000000'  # 明确设置黑色
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor='#000000'  # 明确设置黑色
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            fontName='Helvetica',
            textColor='#000000'  # 明确设置黑色
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
        
        # 添加测试内容
        flowables.append(Paragraph("证据：测试内容", subtitle_style))
        flowables.append(Spacer(1, 0.5*cm))
        flowables.append(Paragraph("这是一段测试文字，用于验证PDF文字显示是否正常。如果文字显示为黑块，则修复失败。", normal_style))
        
        # 生成PDF
        doc.build(flowables)
        
        print(f"✅ PDF生成成功: {pdf_filename}")
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
        print(f"❌ PDF生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试PDF导出修复...")
    success = test_pdf_generation()
    if success:
        print("\n🎉 测试成功！请检查PDF文件中的文字是否正常显示。")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
