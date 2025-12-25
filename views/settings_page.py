#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置页面
用于配置系统参数，如检测阈值、摄像头ID、保存路径等
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, 
    QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, 
    QPushButton, QFileDialog, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from utils.config_manager import ConfigManager
from utils.logger import logger
import os

class SettingsPage(QWidget):
    """系统设置页面"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self._init_ui()
        self._load_current_settings()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 设置页面背景色
        self.setStyleSheet("background-color: #f4f6f9;")
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("系统设置")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # 滚动区域（防止设置项过多超出屏幕）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- 检测设置 ---
        detection_group = self._create_group_box("检测参数设置")
        detection_layout = QFormLayout(detection_group)
        detection_layout.setSpacing(15)
        
        # 置信度阈值
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.0, 1.0)
        self.conf_spin.setSingleStep(0.05)
        self.conf_spin.setDecimals(2)
        detection_layout.addRow("置信度阈值 (Conf Threshold):", self.conf_spin)
        
        # IOU阈值
        self.iou_spin = QDoubleSpinBox()
        self.iou_spin.setRange(0.0, 1.0)
        self.iou_spin.setSingleStep(0.05)
        self.iou_spin.setDecimals(2)
        detection_layout.addRow("IOU阈值 (IOU Threshold):", self.iou_spin)
        
        # 模型路径
        model_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("选择模型文件 (.pt)")
        model_btn = QPushButton("浏览...")
        model_btn.clicked.connect(self._browse_model)
        model_layout.addWidget(self.model_path_edit)
        model_layout.addWidget(model_btn)
        detection_layout.addRow("模型路径 (Model Path):", model_layout)
        
        scroll_layout.addWidget(detection_group)
        
        # --- 摄像头设置 ---
        camera_group = self._create_group_box("摄像头设置")
        camera_layout = QFormLayout(camera_group)
        camera_layout.setSpacing(15)
        
        # 摄像头ID
        self.camera_id_spin = QSpinBox()
        self.camera_id_spin.setRange(0, 10)
        camera_layout.addRow("摄像头 ID:", self.camera_id_spin)
        
        # 分辨率
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        camera_layout.addRow("分辨率 (Resolution):", self.resolution_combo)
        
        scroll_layout.addWidget(camera_group)
        
        # --- 系统设置 ---
        system_group = self._create_group_box("系统设置")
        system_layout = QFormLayout(system_group)
        system_layout.setSpacing(15)
        
        # 结果保存路径
        save_layout = QHBoxLayout()
        self.save_dir_edit = QLineEdit()
        self.save_dir_edit.setPlaceholderText("选择保存目录")
        save_btn = QPushButton("浏览...")
        save_btn.clicked.connect(self._browse_save_dir)
        save_layout.addWidget(self.save_dir_edit)
        save_layout.addWidget(save_btn)
        system_layout.addRow("结果保存路径:", save_layout)
        
        # 主题设置
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        system_layout.addRow("界面主题 (Theme):", self.theme_combo)
        
        scroll_layout.addWidget(system_group)
        
        # 添加弹簧
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # --- 底部按钮 ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存设置")
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        
    def _create_group_box(self, title):
        """创建统一风格的GroupBox"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 20px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        return group
        
    def _load_current_settings(self):
        """加载当前配置到UI"""
        # Detection
        self.conf_spin.setValue(self.config_manager.get("Detection", "conf_threshold"))
        self.iou_spin.setValue(self.config_manager.get("Detection", "iou_threshold"))
        self.model_path_edit.setText(self.config_manager.get("Detection", "model_path"))
        
        # Camera
        self.camera_id_spin.setValue(self.config_manager.get("Camera", "camera_id"))
        current_res = self.config_manager.get("Camera", "resolution")
        index = self.resolution_combo.findText(current_res)
        if index >= 0:
            self.resolution_combo.setCurrentIndex(index)
            
        # System
        self.save_dir_edit.setText(self.config_manager.get("System", "save_dir"))
        current_theme = self.config_manager.get("System", "theme")
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
            
    def _browse_model(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "", "YOLO Models (*.pt);;All Files (*)"
        )
        if file_path:
            self.model_path_edit.setText(file_path)
            
    def _browse_save_dir(self):
        """浏览保存目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if dir_path:
            self.save_dir_edit.setText(dir_path)
            
    def _save_settings(self):
        """保存设置"""
        try:
            # Detection
            self.config_manager.set("Detection", "conf_threshold", self.conf_spin.value())
            self.config_manager.set("Detection", "iou_threshold", self.iou_spin.value())
            self.config_manager.set("Detection", "model_path", self.model_path_edit.text())
            
            # Camera
            self.config_manager.set("Camera", "camera_id", self.camera_id_spin.value())
            self.config_manager.set("Camera", "resolution", self.resolution_combo.currentText())
            
            # System
            self.config_manager.set("System", "save_dir", self.save_dir_edit.text())
            self.config_manager.set("System", "theme", self.theme_combo.currentText())
            
            # 保存文件
            self.config_manager.save_config()
            
            QMessageBox.information(self, "成功", "设置已保存！\n部分设置可能需要重启应用才能生效。")
            
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
