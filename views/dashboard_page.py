#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页总览页面

展示系统状态的仪表盘，包含关键指标卡片和项目信息
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGroupBox, QGridLayout, QSplitter, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
import os
from utils.global_state import global_state


class DashboardPage(QWidget):
    """首页总览页面类"""
    
    def __init__(self):
        """初始化首页总览页面"""
        super().__init__()
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("首页总览")
        title_label.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; margin-bottom: 10px; font-family: 'Microsoft YaHei'; }")
        main_layout.addWidget(title_label)
        
        # 创建顶部指标卡片区域
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        # 创建系统状态卡片
        status_card = self._create_metric_card("系统状态", "运行正常", "green", has_icon=True)
        metrics_layout.addWidget(status_card)
        
        # 创建今日检测卡片
        detection_count = global_state.get_detection_count()
        detection_card = self._create_metric_card("今日检测", f"{detection_count} 次", "black")
        self.detection_card = detection_card  # 保存引用以便后续更新
        metrics_layout.addWidget(detection_card)
        
        # 创建发现病害卡片
        defect_card = self._create_metric_card("发现病害", "3 处", "red")
        metrics_layout.addWidget(defect_card)
        
        main_layout.addLayout(metrics_layout)
        
        # 创建中部图表区
        content_section = QFrame()
        content_section.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; }")
        content_layout = QHBoxLayout(content_section)
        content_layout.setSpacing(40)  # 增加左右间距
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建左侧桥梁图片显示
        image_frame = QFrame()
        image_frame.setStyleSheet("border: none;") # 移除内部边框
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加左侧标题，保持与右侧对齐
        image_title = QLabel("桥梁概览")
        image_title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; margin-bottom: 15px; font-family: 'Microsoft YaHei'; border: none; }")
        image_layout.addWidget(image_title)
        
        # 尝试加载本地桥梁图片，如果没有则显示占位符
        bridge_image_label = QLabel()
        bridge_image_label.setAlignment(Qt.AlignCenter)
        bridge_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 检查是否有示例图片
        image_path = "icons/八一大桥.jpg"
        if os.path.exists(image_path):
            # 初始显示图片，稍后在resizeEvent中会调整大小
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            bridge_image_label.setPixmap(scaled_pixmap)
            # 保存原始图片用于后续缩放
            self.original_pixmap = pixmap
        else:
            # 显示占位符
            bridge_image_label.setText("桥梁图片占位符")
            bridge_image_label.setStyleSheet("QLabel { font-size: 16px; color: #666666; border: 2px dashed #cccccc; padding: 20px; border-radius: 10px; }")
            self.original_pixmap = None
        
        # 设置图片标签样式
        bridge_image_label.setStyleSheet("QLabel { border-radius: 5px; background-color: #f8f9fa; border: 1px solid #e9ecef; }")
        
        # 存储桥梁图片标签引用
        self.bridge_image_label = bridge_image_label
        
        # 设置图片标签可以垂直伸缩
        bridge_image_label.setMinimumHeight(350)  # 稍微增加高度以平衡右侧列表
        image_layout.addWidget(bridge_image_label, 1)
        
        # 创建右侧项目信息列表
        info_frame = QFrame()
        info_frame.setStyleSheet("border: none;") # 移除内部边框
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建项目信息标题
        info_title = QLabel("项目信息")
        info_title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; margin-bottom: 15px; font-family: 'Microsoft YaHei'; border: none; }")
        info_layout.addWidget(info_title)
        
        # 创建项目信息网格布局
        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        
        # 添加项目信息
        info_items = [
            ("桥名", "八一大桥"),
            ("结构", "混凝土"),
            ("管养单位", "气象局"),
            ("建造年份", "1997年"),
            ("全长", "500米"),
            ("主跨", "100米"),
            ("设计荷载", "公路-I级"),
            ("检测频率", "每月1次")
        ]
        
        for i, (key, value) in enumerate(info_items):
            key_label = QLabel(f"{key}：")
            key_label.setStyleSheet("QLabel { font-weight: bold; color: #333333; font-family: 'Microsoft YaHei'; }")
            value_label = QLabel(value)
            value_label.setStyleSheet("QLabel { color: #666666; font-family: 'Microsoft YaHei'; }")
            
            info_grid.addWidget(key_label, i, 0)
            info_grid.addWidget(value_label, i, 1)
        
        info_layout.addLayout(info_grid)
        info_layout.addStretch()
        
        # 将左侧图片和右侧信息添加到内容布局
        content_layout.addWidget(image_frame, 1)
        content_layout.addWidget(info_frame, 1)
        
        main_layout.addWidget(content_section, 1)  # 添加伸缩因子
        main_layout.addStretch()
    
    def resizeEvent(self, event):
        """窗口大小变化时调整桥梁图片大小"""
        super().resizeEvent(event)
        
        if hasattr(self, 'bridge_image_label') and hasattr(self, 'original_pixmap') and self.original_pixmap:
            # 获取标签的当前大小
            label_size = self.bridge_image_label.size()
            
            # 缩放图片以适应标签大小，保持宽高比
            scaled_pixmap = self.original_pixmap.scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 更新标签上的图片
            self.bridge_image_label.setPixmap(scaled_pixmap)
    
    def update_detection_count(self):
        """更新今日检测次数的显示"""
        from PyQt5.QtWidgets import QLabel
        
        if hasattr(self, 'detection_card'):
            # 获取卡片中的布局
            layout = self.detection_card.layout()
            if layout:
                # 获取内容布局
                content_layout = layout.itemAt(1).layout()
                if content_layout:
                    # 获取值标签
                    value_label = content_layout.itemAt(0).widget()
                    if isinstance(value_label, QLabel):
                        # 更新值标签的文本
                        detection_count = global_state.get_detection_count()
                        value_label.setText(f"{detection_count} 次")
    
    def _create_metric_card(self, title, value, value_color, has_icon=False):
        """创建指标卡片
        
        Args:
            title: 卡片标题
            value: 卡片值
            value_color: 值的颜色
            has_icon: 是否显示图标
            
        Returns:
            QFrame: 指标卡片
        """
        card = QFrame()
        card.setObjectName("metric_card")
        card.setStyleSheet("QFrame#metric_card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; }")
        
        layout = QVBoxLayout(card)
        
        # 创建标题
        title_label = QLabel(title)
        title_label.setStyleSheet("QLabel { font-size: 14px; color: #666666; margin-bottom: 10px; font-family: 'Microsoft YaHei'; }")
        layout.addWidget(title_label)
        
        # 创建内容布局（可能包含图标和值）
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        
        if has_icon:
            # 创建状态图标
            icon_label = QLabel()
            icon_label.setFixedSize(20, 20)
            icon_label.setStyleSheet("QLabel { background-color: " + value_color + "; border-radius: 10px; }")
            content_layout.addWidget(icon_label)
            
            # 创建值标签
            value_label = QLabel(value)
            value_label.setStyleSheet(f"QLabel {{ font-size: 18px; color: #333333; margin-left: 10px; font-family: 'Microsoft YaHei'; }}")
            content_layout.addWidget(value_label)
        else:
            # 创建值标签（大数字）
            value_label = QLabel(value)
            value_label.setStyleSheet(f"QLabel {{ font-size: 24px; font-weight: bold; color: {value_color}; font-family: 'Microsoft YaHei'; }}")
            content_layout.addWidget(value_label)
        
        layout.addLayout(content_layout)
        layout.setAlignment(Qt.AlignCenter)
        
        return card