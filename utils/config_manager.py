#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
用于管理系统的全局配置，包括检测参数、摄像头设置和系统路径等
"""

import json
import os
from utils.logger import logger

class ConfigManager:
    """配置管理器类 (单例模式)"""
    
    _instance = None
    _config = None
    _config_file = "config.json"
    
    # 默认配置
    _default_config = {
        "Detection": {
            "conf_threshold": 0.25,
            "iou_threshold": 0.45,
            "model_path": "best_seg.pt",
            "pixel_ratio": 1.0  # 像素比例：mm/pixel
        },
        "Camera": {
            "camera_id": 0,
            "resolution": "1280x720"
        },
        "System": {
            "save_dir": "outputs",
            "theme": "light"
        }
    }
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器，仅在第一次加载配置"""
        if self._config is None:
            self.load_config()
            
    def load_config(self):
        """从文件加载配置，如果文件不存在则使用默认配置"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并加载的配置和默认配置（防止缺少新字段）
                    self._config = self._merge_configs(self._default_config.copy(), loaded_config)
            else:
                self._config = self._default_config.copy()
                self.save_config()  # 创建默认配置文件
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，将使用默认配置")
            self._config = self._default_config.copy()
            
    def _merge_configs(self, default, loaded):
        """递归合并配置字典"""
        for key, value in default.items():
            if key in loaded:
                if isinstance(value, dict) and isinstance(loaded[key], dict):
                    self._merge_configs(value, loaded[key])
                else:
                    # 如果类型匹配，则使用加载的值，否则保持默认
                    if type(value) == type(loaded[key]):
                        default[key] = loaded[key]
        return default
            
    def save_config(self):
        """保存当前配置到文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            
    def get(self, section, key):
        """获取配置项的值"""
        if section in self._config and key in self._config[section]:
            return self._config[section][key]
        return None
        
    def set(self, section, key, value):
        """设置配置项的值"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        
    def get_all(self):
        """获取所有配置"""
        return self._config
