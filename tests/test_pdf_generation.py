#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF生成的核心功能

直接测试PDF生成逻辑，不依赖完整的GUI界面
"""

import os
import sys
from datetime import datetime
import numpy as np
import cv2

# 测试ReportLab的PDF生成功能
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    print("ReportLab导入成功")
except Exception as e:
    print(f"ReportLab导入失败: {str(e)}")
    sys.exit(1)

def test_pdf_generation():
    """测试PDF生成功能"""
    try:
        # 模拟数据
        crack_count = 2
        vehicle_count = 150
        bci_score = max(0, min(100, 100 - crack_count * 5 - vehicle_count * 0.1))
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 创建PDF文件
        pdf_filename = f"桥梁健康监测报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        # 设置样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=24,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # 准备内容
        flowables = []
        flowables.append(Paragraph("桥梁健康监测报告", title_style))
        flowables.append(Spacer(1, 2*cm))
        flowables.append(Paragraph(f"生成时间: {current_time}", normal_style))
        flowables.append(Spacer(1, 1*cm))
        flowables.append(Paragraph("结论：", subtitle_style))
        flowables.append(Spacer(1, 0.5*cm))
        flowables.append(Paragraph(f"桥梁健康评分: <b>{bci_score:.1f}</b>", normal_style))
        flowables.append(Spacer(1, 1*cm))
        
        # 创建一个简单的测试图像作为证据
        test_image = np.zeros((300, 600, 3), dtype=np.uint8)
        cv2.putText(test_image, "测试裂缝检测图像", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        temp_image_path = "temp_test_image.png"
        cv2.imwrite(temp_image_path, test_image)
        
        # 添加图像到PDF
        flowables.append(Paragraph("证据：裂缝检测结果", subtitle_style))
        flowables.append(Spacer(1, 0.5*cm))
        img = Image(temp_image_path)
        img_width = 15*cm
        img_height = img_width * (img.imageHeight / img.imageWidth)
        img.drawWidth = img_width
        img.drawHeight = img_height
        img.hAlign = 'CENTER'
        flowables.append(img)
        
        # 生成PDF
        doc.build(flowables)
        
        # 删除临时图像
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # 检查PDF文件是否生成
        if os.path.exists(pdf_path):
            print(f"PDF文件生成成功: {pdf_path}")
            
            # 尝试自动打开PDF
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                else:  # macOS or Linux
                    import subprocess
                    subprocess.run(['open', pdf_path] if os.name == 'darwin' else ['xdg-open', pdf_path])
                print("PDF文件已尝试打开")
            except Exception as e:
                print(f"自动打开PDF失败: {str(e)}")
            
            return True
        else:
            print("PDF文件生成失败")
            return False
            
    except Exception as e:
        print(f"PDF生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pdf_generation()
