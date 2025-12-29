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
            cls._instance._max_crack_width = 0.0  # 最大裂缝宽度
            cls._instance._health_score = 98  # 桥梁健康指数
            cls._instance.vehicle_count = 0  # 车辆总数
            cls._instance.truck_count = 0  # 卡车数量
            cls._instance.car_count = 0  # 小汽车数量
            cls._instance.bus_count = 0  # 公交车数量
            cls._instance.detection_count = 0  # 今日检测次数
            cls._instance.current_project_id = None  # 当前项目ID
            cls._instance.last_traffic_score = 100.0  # 最近一次交通健康评分
        return cls._instance
    
    def reset(self):
        """重置所有全局数据"""
        self.crack_count = 0
        self._max_crack_width = 0.0
        self._health_score = 98
        self.vehicle_count = 0
        self.truck_count = 0
        self.car_count = 0
        self.bus_count = 0
        self.detection_count = 0
        self.current_project_id = None
        self.last_traffic_score = 100.0

    def get_crack_level(self):
        """获取主要裂缝等级"""
        width = self._max_crack_width
        if width < 0.2:
            return "I 级"
        elif 0.2 <= width < 1.0:
            return "II 级"
        else:
            return "III 级"

    def get_truck_ratio(self):
        """获取重载车辆占比 (%)"""
        if self.vehicle_count == 0:
            return 0.0
        return round((self.truck_count / self.vehicle_count) * 100, 1)

    def increment_detection_count(self):
        """增加检测次数"""
        self.detection_count += 1
    
    def get_detection_count(self):
        """获取检测次数（实时从数据库查询）"""
        try:
            from utils.db_manager import DBManager
            db = DBManager()
            return db.get_today_detection_count()
        except Exception:
            return self.detection_count
    
    def update_crack_data(self, count, max_width):
        """更新裂缝数据"""
        self.crack_count = count
        self._max_crack_width = max_width
    
    def update_vehicle_count(self, count):
        """更新车辆总数"""
        self.vehicle_count = count
    
    def update_traffic_stats(self, total, truck, car, bus):
        """更新交通统计数据"""
        self.vehicle_count = total
        self.truck_count = truck
        self.car_count = car
        self.bus_count = bus
    
    def update_traffic_score(self, score):
        """更新交通健康评分"""
        self.last_traffic_score = score
    
    def get_traffic_stats(self):
        """获取交通统计数据"""
        return {
            "total": self.vehicle_count,
            "truck": self.truck_count,
            "car": self.car_count,
            "bus": self.bus_count
        }
    
    def set_current_project_id(self, project_id):
        """设置当前项目ID"""
        self.current_project_id = project_id
    
    def get_current_project_id(self):
        """获取当前项目ID"""
        return self.current_project_id

# 创建全局状态实例
global_state = GlobalState()
