#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局状态管理

使用单例模式实现全局数据共享，存储各页面之间需要共享的数据
"""

class GlobalState:
    """全局状态管理单例类"""
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(GlobalState, cls).__new__(cls)
            # 初始化全局数据
            cls._instance.crack_count = 0  # 裂缝数量
            cls._instance.max_crack_width = 0.0  # 最大裂缝宽度
            cls._instance.vehicle_count = 0  # 车辆总数
        return cls._instance
    
    def reset(self):
        """重置所有全局数据"""
        self.crack_count = 0
        self.max_crack_width = 0.0
        self.vehicle_count = 0
    
    def update_crack_data(self, count, max_width):
        """更新裂缝数据"""
        self.crack_count = count
        self.max_crack_width = max_width
    
    def update_vehicle_count(self, count):
        """更新车辆总数"""
        self.vehicle_count = count

# 创建全局状态实例
global_state = GlobalState()
