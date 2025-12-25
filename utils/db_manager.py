#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
用于管理桥梁检测系统的SQLite数据库
"""

import sqlite3
import os
from datetime import datetime


class DBManager:
    """数据库管理器类"""
    
    def __init__(self, db_path="bridge_data.db"):
        """
        初始化数据库连接
        
        Args:
            db_path (str): 数据库文件路径
        """
        # 获取数据库文件的绝对路径
        self.db_path = os.path.abspath(db_path)
        
        # 连接数据库
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute('PRAGMA foreign_keys = ON')  # 启用外键约束
        self.cursor = self.connection.cursor()
        
        # 初始化表格
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表格"""
        # 创建projects表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建inspection_records表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        ''')
        
        # 创建crack_details表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS crack_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            max_width REAL NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY (record_id) REFERENCES inspection_records(id) ON DELETE CASCADE
        )
        ''')
        
        # 创建traffic_stats表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            total_vehicles INTEGER NOT NULL,
            truck_count INTEGER NOT NULL,
            car_count INTEGER NOT NULL,
            bus_count INTEGER NOT NULL,
            FOREIGN KEY (record_id) REFERENCES inspection_records(id) ON DELETE CASCADE
        )
        ''')
        
        # 如果表已存在，确保添加car_count和bus_count列（兼容性处理）
        try:
            self.cursor.execute('ALTER TABLE traffic_stats ADD COLUMN car_count INTEGER NOT NULL DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在
            
        try:
            self.cursor.execute('ALTER TABLE traffic_stats ADD COLUMN bus_count INTEGER NOT NULL DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        # 提交事务
        self.connection.commit()
    
    def get_all_projects(self):
        """
        获取所有项目列表
        
        Returns:
            list: 包含所有项目字典的列表
        """
        sql = "SELECT id, name, type, created_at FROM projects ORDER BY created_at DESC"
        rows = self.fetch_all(sql)
        return [
            {"id": row[0], "name": row[1], "type": row[2], "created_at": row[3]}
            for row in rows
        ]
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """支持with语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句，自动关闭连接"""
        self.close()
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor
    
    def fetch_all(self, sql, params=None):
        """执行查询并返回所有结果"""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def fetch_one(self, sql, params=None):
        """执行查询并返回一条结果"""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchone()
    
    def lastrowid(self):
        """返回最后插入的行ID"""
        return self.cursor.lastrowid
    
    def add_project(self, name, type="混凝土桥梁"):
        """
        添加项目
        
        Args:
            name (str): 项目名称
            type (str): 桥梁类型，默认为"混凝土桥梁"
            
        Returns:
            int: 项目ID
        """
        self.cursor.execute(
            "INSERT INTO projects (name, type) VALUES (?, ?)",
            (name, type)
        )
        self.connection.commit()
        return self.lastrowid()
    
    def add_crack_record(self, project_id, score, image_path, width, count):
        """
        添加裂缝检测记录（事务处理）
        
        Args:
            project_id (int): 项目ID
            score (float): 检测得分
            image_path (str): 图片路径
            width (float): 最大裂缝宽度
            count (int): 裂缝数量
            
        Returns:
            int: 检测记录ID
        """
        try:
            # 开始事务
            self.connection.execute('BEGIN TRANSACTION')
            
            # 插入检测记录主表
            self.cursor.execute(
                "INSERT INTO inspection_records (project_id, type, score) VALUES (?, ?, ?)",
                (project_id, "裂缝检测", score)
            )
            record_id = self.lastrowid()
            
            # 插入裂缝详情子表
            self.cursor.execute(
                "INSERT INTO crack_details (record_id, image_path, max_width, count) VALUES (?, ?, ?, ?)",
                (record_id, image_path, width, count)
            )
            
            # 提交事务
            self.connection.commit()
            return record_id
        except Exception as e:
            # 回滚事务
            self.connection.rollback()
            raise e
    
    def add_traffic_record(self, project_id, score, total, truck, car, bus):
        """
        添加交通检测记录（事务处理）
        
        Args:
            project_id (int): 项目ID
            score (float): 检测得分
            total (int): 总车辆数
            truck (int): 卡车数量
            car (int): 轿车数量
            bus (int): 公交车数量
            
        Returns:
            int: 检测记录ID
        """
        try:
            # 生成本地时间戳
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 开始事务
            self.connection.execute('BEGIN TRANSACTION')
            
            # 插入检测记录主表
            self.cursor.execute(
                "INSERT INTO inspection_records (project_id, type, score, timestamp) VALUES (?, ?, ?, ?)",
                (project_id, "交通监测", score, current_time)
            )
            record_id = self.lastrowid()
            
            # 插入交通统计子表
            self.cursor.execute(
                "INSERT INTO traffic_stats (record_id, total_vehicles, truck_count, car_count, bus_count) VALUES (?, ?, ?, ?, ?)",
                (record_id, total, truck, car, bus)
            )
            
            # 提交事务
            self.connection.commit()
            return record_id
        except Exception as e:
            # 回滚事务
            self.connection.rollback()
            raise e
    
    def get_history(self, limit=20):
        """
        获取最近的检测记录
        
        Args:
            limit (int): 返回记录的最大数量，默认20条
            
        Returns:
            list: 检测记录列表，每条记录包含项目名称、检测类型、得分、时间戳等信息
        """
        # 查询最近的检测记录，连接项目表获取项目名称
        query = '''
        SELECT 
            i.id, p.name as project_name, i.type, i.score, i.timestamp
        FROM 
            inspection_records i
        JOIN 
            projects p ON i.project_id = p.id
        ORDER BY 
            i.timestamp DESC
        LIMIT ?
        '''
        
        self.cursor.execute(query, (limit,))
        records = self.cursor.fetchall()
        
        # 构建结果列表，每条记录包含更丰富的信息
        history = []
        for record in records:
            record_id, project_name, type, score, timestamp = record
            
            # 根据检测类型获取详细信息
            details = None
            if type == "裂缝检测":
                self.cursor.execute(
                    "SELECT image_path, max_width, count FROM crack_details WHERE record_id = ?",
                    (record_id,)
                )
                details = self.cursor.fetchone()
            elif type == "交通监测":
                self.cursor.execute(
                    "SELECT total_vehicles, truck_count, car_count, bus_count FROM traffic_stats WHERE record_id = ?",
                    (record_id,)
                )
                details = self.cursor.fetchone()
            
            # 构建记录字典
            history_item = {
                "id": record_id,
                "project_name": project_name,
                "type": type,
                "score": score,
                "timestamp": timestamp,
                "details": details
            }
            
            history.append(history_item)
        
        return history

    def delete_record(self, record_id):
        """
        删除指定的检测记录及其关联的详细数据
        
        Args:
            record_id (int): 检测记录的 ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 由于创建表时设置了 ON DELETE CASCADE，
            # 只需删除主记录，关联的 crack_details 或 traffic_stats 会自动删除
            query = "DELETE FROM inspection_records WHERE id = ?"
            self.cursor.execute(query, (record_id,))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            from utils.logger import logger
            logger.error(f"删除记录失败 (ID: {record_id}): {e}")
            return False


# 测试代码
if __name__ == "__main__":
    from utils.logger import logger
    with DBManager() as db:
        logger.info(f"数据库已连接：{db.db_path}")
        
        # 测试使用封装的方法创建一个项目
        project_id = db.add_project("测试桥梁项目", "混凝土桥梁")
        logger.info(f"创建的项目ID：{project_id}")
        
        # 测试使用封装的方法创建裂缝检测记录（事务处理）
        crack_record_id = db.add_crack_record(
            project_id=project_id,
            score=90.5,
            image_path="test_image.jpg",
            width=0.5,
            count=10
        )
        logger.info(f"创建的裂缝检测记录ID：{crack_record_id}")
        
        # 测试使用封装的方法创建交通检测记录（事务处理）
        traffic_record_id = db.add_traffic_record(
            project_id=project_id,
            score=85.0,
            total=100,
            truck=20,
            car=70,
            bus=10
        )
        logger.info(f"创建的交通检测记录ID：{traffic_record_id}")
        
        # 测试查询所有项目
        logger.info("\n查询所有项目：")
        projects = db.fetch_all("SELECT * FROM projects")
        for project in projects:
            logger.info(project)
        
        # 测试查询所有检测记录
        logger.info("\n查询所有检测记录：")
        records = db.fetch_all("SELECT * FROM inspection_records")
        for record in records:
            logger.info(record)
        
        # 测试查询所有裂缝详情
        logger.info("\n查询所有裂缝详情：")
        crack_details = db.fetch_all("SELECT * FROM crack_details")
        for detail in crack_details:
            logger.info(detail)
        
        # 测试查询所有交通统计
        logger.info("\n查询所有交通统计：")
        traffic_stats = db.fetch_all("SELECT * FROM traffic_stats")
        for stats in traffic_stats:
            logger.info(stats)
        
        # 测试获取历史记录
        logger.info("\n获取最近的检测记录：")
        history = db.get_history(limit=20)
        for i, record in enumerate(history, 1):
            logger.info(f"\n记录 #{i}:")
            logger.info(f"  ID: {record['id']}")
            logger.info(f"  项目名称: {record['project_name']}")
            logger.info(f"  检测类型: {record['type']}")
            logger.info(f"  得分: {record['score']}")
            logger.info(f"  时间戳: {record['timestamp']}")
            logger.info(f"  详情: {record['details']}")