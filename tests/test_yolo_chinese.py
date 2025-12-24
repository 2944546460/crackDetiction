#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试YOLO检测模型的中文标签显示功能
"""

import cv2
import numpy as np
from models.yolo_detection import YoloModel
import os

def create_test_image():
    """创建一个测试图像，包含一些简单的裂缝图案"""
    # 创建一个白色背景的图像
    image = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # 绘制一些模拟的裂缝
    cv2.line(image, (100, 100), (200, 150), (0, 0, 0), 2)
    cv2.line(image, (300, 200), (500, 150), (0, 0, 0), 2)
    cv2.line(image, (200, 300), (400, 350), (0, 0, 0), 2)
    
    return image

def main():
    """主函数"""
    print("开始测试YOLO检测模型的中文标签显示功能")
    
    # 创建测试图像
    test_image = create_test_image()
    cv2.imwrite("test_image.jpg", test_image)
    
    # 初始化YOLO模型
    model = YoloModel()
    model.initialize()
    
    # 测试检测功能
    try:
        print("进行图像检测...")
        processed_image, result = model.process_image(test_image)
        
        # 显示处理后的图像
        cv2.imshow("YOLO检测结果（中文标签测试）", processed_image)
        
        # 保存处理后的图像
        cv2.imwrite("test_result.jpg", processed_image)
        print(f"检测结果已保存到 test_result.jpg")
        print(f"检测到 {result['stats']['total_cracks']} 处裂缝")
        
        # 等待用户按键
        print("按任意键退出...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        model.release()

if __name__ == "__main__":
    main()
