#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
控制器基类

提供控制器层的通用功能和接口定义
"""

from abc import ABC, abstractmethod


class BaseController(ABC):
    """控制器基类"""
    
    def __init__(self):
        """初始化控制器"""
        self._is_initialized = False
    
    @abstractmethod
    def initialize(self):
        """初始化控制器，连接模型和视图"""
        pass
    
    def release(self):
        """释放控制器资源"""
        pass
    
    @property
    def is_initialized(self):
        """检查控制器是否已初始化"""
        return self._is_initialized
    
    def _set_initialized(self, value):
        """设置初始化状态"""
        self._is_initialized = value
    
    def _connect_signals(self):
        """连接模型和视图的信号"""
        pass
