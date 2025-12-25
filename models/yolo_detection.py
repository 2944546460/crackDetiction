#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO检测模型

使用Ultralytics YOLOv11实现裂缝检测功能，默认使用训练好的best.pt模型
"""

import cv2
import numpy as np
from models.base_model import ImageProcessingModel
from ultralytics import YOLO
import os
from PIL import Image, ImageDraw, ImageFont
from utils.config_manager import ConfigManager
from utils.logger import logger


class YoloModel(ImageProcessingModel):
    """YOLO裂缝检测工具类
    
    单例或工具类，用于封装Ultralytics YOLO模型，实现裂缝检测功能
    默认使用配置文件中的模型，也支持加载其他YOLO模型
    """
    
    def __init__(self, model_path=None):
        """初始化YOLO检测模型
        
        Args:
            model_path: YOLO模型文件路径，如果为None则默认使用配置文件中的模型
        """
        super().__init__()
        self.config_manager = ConfigManager()
        
        # 如果未提供路径，从配置读取
        if model_path is None:
            model_path = self.config_manager.get("Detection", "model_path")
            
        self._model_path = model_path
        self._model = None
        self._class_names = ["crack"]  # 裂缝检测的类别名称
    
    def initialize(self):
        """初始化模型，加载YOLO权重"""
        try:
            if self._model_path is None:
                # 如果没有提供模型路径，优先使用当前目录下的best.pt模型
                if os.path.exists("best_seg.pt"):
                    self._model = YOLO("best_seg.pt")
                    logger.info("使用默认的训练模型: best_seg.pt")
                else:
                    # 如果best.pt不存在，使用yolov11n.pt
                    self._model = YOLO("yolov11n.pt")
                    logger.info("使用默认的YOLOv11n模型")
            else:
                if not os.path.exists(self._model_path):
                    raise FileNotFoundError(f"YOLO模型文件不存在: {self._model_path}")
                self._model = YOLO(self._model_path)
                logger.info(f"加载YOLO模型: {self._model_path}")
            
            self._set_initialized(True)
            logger.info("YOLO检测模型初始化完成")
        except Exception as e:
            logger.error(f"YOLO检测模型初始化失败: {e}")
            self._set_initialized(False)
    
    def process(self, data):
        """处理数据的核心方法
        
        Args:
            data: 输入数据，可以是图像文件路径或numpy数组
            
        Returns:
            processed_data: 处理后的图像
            result: 检测结果
        """
        return self.process_image(data)
    
    def process_image(self, image):
        """处理单张图像，进行裂缝检测
        
        Args:
            image: 输入图像，可以是numpy数组（BGR格式）或图像文件路径
            
        Returns:
            processed_image: 处理后的图像（numpy数组，BGR格式），绘制了检测框
            result: 检测结果数据，包括检测到的裂缝信息
        """
        if not self.is_initialized:
            self.initialize()
            if not self.is_initialized:
                raise RuntimeError("YOLO检测模型未初始化")
        
       # 读取图像
        original_image = self.read_image(image)
        # processed_image = original_image.copy()  <-- 这行可以删掉，plot() 会返回新图
        
        # 进行检测
        results = self._model(original_image)
        
        # --- 核心修改开始 ---
        
        # 方案：直接使用 YOLO 自带的绘图功能
        # 这会自动绘制 框(Boxes) + 掩膜(Masks) + 标签(Labels)
        # img=original_image 参数确保在原图上绘制
        # conf=True 显示置信度
        # boxes=True 显示检测框
        processed_image = results[0].plot(conf=True, boxes=True, img=original_image)
        # --- 核心修改结束 ---

        # 下面统计数据的逻辑可以保留，用来生成报告
        detected_cracks = []
        pixel_ratio = self.config_manager.get("Detection", "pixel_ratio") or 1.0
        
        for result in results:
            boxes = result.boxes
            masks = result.masks
            
            if len(boxes) > 0:
                for i, box in enumerate(boxes):
                    # 获取基本信息用于统计
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    
                    # 计算像素宽度
                    # 如果有掩码，使用掩码计算更精确的宽度
                    if masks is not None and i < len(masks):
                        mask_pixels = np.sum(masks.data[i].cpu().numpy() > 0)
                        # 粗略估计：宽度 = 面积 / 长度 (使用对角线作为长度近似)
                        length_px = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                        width_px = mask_pixels / length_px if length_px > 0 else 0
                    else:
                        # 如果没有掩码，使用最小边作为宽度
                        width_px = min(x2 - x1, y2 - y1)
                    
                    # 转换为毫米
                    width_mm = width_px * pixel_ratio
                    
                    # 存储裂缝信息
                    crack_info = {
                        "bounding_box": [int(x1), int(y1), int(x2), int(y2)],
                        "confidence": confidence,
                        "width_px": width_px,
                        "width_mm": width_mm,
                        "area_px": (x2 - x1) * (y2 - y1),
                        "center": [(x1 + x2) / 2, (y1 + y2) / 2]
                    }
                    detected_cracks.append(crack_info)
                    
        # 计算裂缝统计信息
        max_width_mm = max([crack["width_mm"] for crack in detected_cracks]) if detected_cracks else 0
        crack_stats = {
            "total_cracks": len(detected_cracks),
            "average_confidence": np.mean([crack["confidence"] for crack in detected_cracks]) if detected_cracks else 0,
            "max_width_mm": max_width_mm,
            "total_crack_area_px": sum([crack["area_px"] for crack in detected_cracks]),
            "image_area_px": original_image.shape[0] * original_image.shape[1],
            "crack_coverage": sum([crack["area_px"] for crack in detected_cracks]) / (original_image.shape[0] * original_image.shape[1]) if detected_cracks else 0
        }
        
        result = {
            "detected_cracks": detected_cracks,
            "stats": crack_stats
        }
        
        return processed_image, result
    
    def process_video_frame(self, frame, persist=True):
        """处理视频帧，进行目标追踪
        
        Args:
            frame: 输入视频帧（numpy数组，BGR格式）
            persist: 是否持久化追踪 (ByteTrack)
            
        Returns:
            processed_frame: 处理后的视频帧
            result: 检测结果（包含追踪 ID）
        """
        if not self.is_initialized:
            self.initialize()
            
        # 使用 track 模式启用目标追踪
        # persist=True 表示在帧之间保持追踪 ID
        results = self._model.track(frame, persist=persist, conf=0.3, iou=0.5)
        
        # 绘图
        processed_frame = results[0].plot(conf=True, boxes=True, img=frame)
        
        # 提取追踪信息
        detected_objects = []
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            confs = results[0].boxes.conf.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            
            for box, obj_id, conf, cls in zip(boxes, ids, confs, classes):
                detected_objects.append({
                    "id": int(obj_id),
                    "bbox": box.tolist(),
                    "conf": float(conf),
                    "class": int(cls),
                    "center": [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]
                })
                
        return processed_frame, {"detected_objects": detected_objects, "results": results[0]}
    
    def detect_image(self, image_path):
        """检测单张图像中的裂缝
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            annotated_image: 绘制了检测框的图像（numpy数组，BGR格式）
            stats: 检测结果的统计信息字典，包含裂缝数量、平均置信度等
        """
        annotated_image, detection_result = self.process_image(image_path)
        return annotated_image, detection_result["stats"]
    
    def release(self):
        """释放资源"""
        self._model = None
        self._set_initialized(False)
        logger.info("YOLO检测模型资源已释放")
    
    def set_class_names(self, class_names):
        """设置类别名称
        
        Args:
            class_names: 类别名称列表
        """
        self._class_names = class_names
    
    def get_class_names(self):
        """获取类别名称
        
        Returns:
            class_names: 类别名称列表
        """
        return self._class_names
    
    def _get_chinese_font(self, font_size=12):
        """自动查找Windows系统中的中文字体
        
        Args:
            font_size: 字体大小
            
        Returns:
            ImageFont: PIL字体对象，如果找不到字体则返回默认字体
        """
        import platform
        if platform.system() != 'Windows':
            # 如果不是Windows系统，返回默认字体
            return ImageFont.load_default()
        
        # Windows系统中常用的中文字体路径
        font_paths = [
            r'C:\Windows\Fonts\simhei.ttf',  # 黑体
            r'C:\Windows\Fonts\msyh.ttc',   # 微软雅黑
            r'C:\Windows\Fonts\msyhbd.ttc', # 微软雅黑粗体
            r'C:\Windows\Fonts\simsun.ttc', # 宋体
            r'C:\Windows\Fonts\simkai.ttf', # 楷体
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    logger.warning(f"加载字体{font_path}失败: {e}")
                    continue
        
        # 如果没有找到任何中文字体，返回默认字体
        logger.warning("未找到Windows系统中文字体，使用默认字体")
        return ImageFont.load_default()
    
    def _draw_chinese_text(self, image, text, position, font_size=12, color=(0, 0, 255)):
        """使用PIL在图像上绘制中文文本
        
        Args:
            image: OpenCV图像（numpy数组，BGR格式）
            text: 要绘制的文本
            position: 文本位置 (x, y)
            font_size: 字体大小
            color: 文本颜色 (BGR格式)
            
        Returns:
            image: 绘制了文本的OpenCV图像
        """
        # 转换BGR到RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # 创建绘图对象
        draw = ImageDraw.Draw(pil_image)
        
        # 获取中文字体
        font = self._get_chinese_font(font_size)
        
        # 转换颜色为RGB
        rgb_color = (color[2], color[1], color[0])
        
        # 绘制文本
        draw.text(position, text, fill=rgb_color, font=font)
        
        # 转换回OpenCV格式
        bgr_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return bgr_image


class CrackAnalysisModel(ImageProcessingModel):
    """裂缝分析模型，用于对检测到的裂缝进行进一步分析"""
    
    def __init__(self):
        """初始化裂缝分析模型"""
        super().__init__()
    
    def initialize(self):
        """初始化模型"""
        self._set_initialized(True)
        logger.info("裂缝分析模型初始化完成")
    
    def process(self, data):
        """处理数据的核心方法
        
        Args:
            data: 输入数据，可以是图像或裂缝检测结果
            
        Returns:
            processed_data: 处理后的图像或结果
            result: 分析结果
        """
        if isinstance(data, dict) and "detected_cracks" in data:
            # 如果输入是检测结果，直接进行分析
            return None, self.analyze_cracks(data)
        else:
            # 如果输入是图像，先进行裂缝检测，再分析
            detection_model = YoloModel()  # 默认使用best.pt模型
            detection_model.initialize()
            processed_image, detection_result = detection_model.process_image(data)
            analysis_result = self.analyze_cracks(detection_result)
            return processed_image, analysis_result
    
    def process_image(self, image):
        """处理单张图像，进行裂缝分析
        
        Args:
            image: 输入图像
            
        Returns:
            processed_image: 处理后的图像
            result: 分析结果
        """
        return self.process(image)
    
    def analyze_cracks(self, detection_result):
        """分析检测到的裂缝
        
        Args:
            detection_result: 裂缝检测结果
            
        Returns:
            analysis_result: 裂缝分析结果
        """
        detected_cracks = detection_result["detected_cracks"]
        
        # 如果没有检测到裂缝
        if not detected_cracks:
            return {
                "crack_level": "无裂缝",
                "severity": "低",
                "recommendation": "无需处理",
                "details": {}
            }
        
        # 使用检测结果中已经计算好的毫米宽度
        crack_widths_mm = [crack["width_mm"] for crack in detected_cracks]
        average_width_mm = np.mean(crack_widths_mm)
        max_width_mm = np.max(crack_widths_mm)
        
        # 计算裂缝密度
        crack_density = len(detected_cracks) / detection_result["stats"]["image_area_px"]
        
        # 根据裂缝特征评估严重程度 (通常以毫米为单位更有意义)
        if max_width_mm < 0.2 and crack_density < 0.0001:
            crack_level = "轻微裂缝"
            severity = "低"
            recommendation = "定期观察"
        elif max_width_mm < 1.0 and crack_density < 0.0005:
            crack_level = "中等裂缝"
            severity = "中"
            recommendation = "需要修复"
        else:
            crack_level = "严重裂缝"
            severity = "高"
            recommendation = "立即修复"
        
        analysis_result = {
            "crack_level": crack_level,
            "severity": severity,
            "recommendation": recommendation,
            "details": {
                "total_cracks": len(detected_cracks),
                "average_width_mm": average_width_mm,
                "max_width_mm": max_width_mm,
                "crack_density": crack_density,
                "crack_coverage": detection_result["stats"]["crack_coverage"]
            }
        }
        
        return analysis_result
    
    def release(self):
        """释放资源"""
        self._set_initialized(False)
        logger.info("裂缝分析模型资源已释放")
