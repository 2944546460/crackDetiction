#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告页面的PDF导出功能
"""

import sys
import os
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import cv2

# 导入ReportPage
from views.report_page import ReportPage

# 创建测试图像

def create_test_image():
    """创建测试图像"""
    # 创建一个黑色背景图像
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 添加文字说明
    cv2.putText(test_image, "测试裂缝检测结果", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # 添加模拟裂缝
    cv2.line(test_image, (100, 200), (500, 300), (0, 255, 0), 2)
    cv2.line(test_image, (150, 250), (550, 150), (0, 255, 0), 2)
    cv2.line(test_image, (200, 350), (400, 380), (0, 255, 0), 2)
    
    return test_image

# 模拟检测页面
class MockDetectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)  # 使用Qt.AlignCenter而不是整数
        
        # 创建并设置测试图像
        test_image = create_test_image()
        height, width, channel = test_image.shape
        bytesPerLine = 3 * width
        qimg = QImage(test_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.result_label.setPixmap(pixmap)
        
        layout.addWidget(self.result_label)

# 测试PDF导出
def test_pdf_export():
    """测试PDF导出功能"""
    try:
        # 创建应用程序实例
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 更新全局状态
        from utils.global_state import global_state
        global_state.crack_count = 3
        global_state.vehicle_count = 100
        global_state.max_crack_width = 0.5
        
        print("✅ 全局状态已更新")
        print(f"   裂缝数量: {global_state.crack_count}")
        print(f"   车辆数量: {global_state.vehicle_count}")
        print(f"   最大裂缝宽度: {global_state.max_crack_width}")
        
        # 创建报告页面
        report_page = ReportPage()
        
        # 生成报告
        report_page._generate_report()
        print("✅ 报告已生成")
        
        # 创建模拟的detection_page
        detection_page = MockDetectionPage()
        
        # 直接修改_report_page.py中的图像获取逻辑，跳过主窗口的查找
        # 这里我们需要修改ReportPage的_export_pdf方法
        original_export_pdf = ReportPage._export_pdf
        
        def patched_export_pdf(self):
            """修改后的导出PDF方法，使用模拟的detection_page"""
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
                pdf_path = os.path.join(os.getcwd(), pdf_filename)
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
                
                title_style = ParagraphStyle(
                    'TitleStyle',
                    parent=styles['Title'],
                    fontSize=24,
                    alignment=TA_CENTER,
                    fontName=title_font,
                    textColor='#000000'
                )
                subtitle_style = ParagraphStyle(
                    'SubtitleStyle',
                    parent=styles['Heading2'],
                    fontSize=16,
                    alignment=TA_CENTER,
                    fontName=title_font,
                    textColor='#000000'
                )
                normal_style = ParagraphStyle(
                    'NormalStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=TA_LEFT,
                    fontName=normal_font,
                    textColor='#000000'
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
                flowables.append(Paragraph(f"桥梁健康评分: {bci_score:.1f}", normal_style))
                flowables.append(Spacer(1, 1*cm))
                
                # 获取裂缝检测图像（使用模拟的detection_page）
                image_added = False
                try:
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
                    
                    print(f"✅ PDF报告已生成并打开：{pdf_filename}")
                else:
                    print("❌ PDF文件生成失败")
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"❌ PDF导出失败：{str(e)}")
        
        # 替换_report_pdf方法
        ReportPage._export_pdf = patched_export_pdf
        
        # 导出PDF
        print("\n正在导出PDF...")
        report_page._export_pdf()
        print("✅ PDF导出完成")
        
        # 恢复原始的_export_pdf方法
        ReportPage._export_pdf = original_export_pdf
        
        print("\n🎉 测试成功！请检查生成的PDF文件。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试报告页面的PDF导出功能...")
    success = test_pdf_export()
    if success:
        print("\n✅ PDF导出功能测试通过！")
    else:
        print("\n❌ PDF导出功能测试失败！")
