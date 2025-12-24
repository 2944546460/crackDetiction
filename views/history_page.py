#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录页面

用于查询和回溯过往的检测数据
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QTableWidgetItem, QLabel, QFrame, QSplitter, QPushButton, QDialog,
    QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import os
import sys

# 添加项目根目录到Python路径，确保能够正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class HistoryPage(QWidget):
    """历史记录页面类"""
    
    def __init__(self):
        """初始化历史记录页面"""
        super().__init__()
        
        # 设置中文字体
        rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']
        
        # 历史记录数据
        self.history_data = []
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局（垂直布局）
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("历史记录")
        title_label.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; margin-bottom: 10px; }")
        main_layout.addWidget(title_label)
        
        # 创建上下结构的分割器
        main_splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：表格区域
        table_group = QGroupBox("检测记录")
        table_layout = QVBoxLayout(table_group)
        
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["时间", "类型", "结果摘要", "健康分", "操作"])
        
        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        
        # 连接表格点击事件
        self.table_widget.cellClicked.connect(self._on_table_row_clicked)
        
        # 添加刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self._load_data)
        
        table_layout.addWidget(refresh_btn)
        table_layout.addWidget(self.table_widget)
        
        main_splitter.addWidget(table_group)
        
        # 下半部分：图表区域
        charts_group = QGroupBox("数据统计")
        charts_layout = QHBoxLayout(charts_group)
        
        # 左右图表分割器
        charts_splitter = QSplitter(Qt.Horizontal)
        
        # 左图：健康评分趋势图
        self.health_chart_container = QFrame()
        self.health_chart_container.setMinimumHeight(300)
        self._init_health_chart()
        
        # 右图：重车流量统计图
        self.truck_chart_container = QFrame()
        self.truck_chart_container.setMinimumHeight(300)
        self._init_truck_chart()
        
        charts_splitter.addWidget(self.health_chart_container)
        charts_splitter.addWidget(self.truck_chart_container)
        charts_splitter.setSizes([400, 400])  # 设置初始大小比例
        
        charts_layout.addWidget(charts_splitter)
        
        main_splitter.addWidget(charts_group)
        main_splitter.setSizes([400, 300])  # 设置上下部分的初始大小比例
        
        main_layout.addWidget(main_splitter, 1)  # 添加伸缩因子，使内容随窗口大小变化
    
    def _init_health_chart(self):
        """初始化健康评分趋势图"""
        # 创建图表布局
        chart_layout = QVBoxLayout(self.health_chart_container)
        
        # 创建Figure对象
        self.health_figure = Figure(figsize=(8, 6), dpi=100)
        
        # 设置图表背景为透明
        self.health_figure.patch.set_alpha(0)
        
        # 创建画布
        self.health_canvas = FigureCanvas(self.health_figure)
        self.health_canvas.setStyleSheet("background-color: transparent;")
        
        # 添加画布到布局
        chart_layout.addWidget(self.health_canvas)
        
        # 创建图表
        self.health_ax = self.health_figure.add_subplot(111)
        
        # 设置图表背景为透明
        self.health_ax.set_facecolor('none')
        
        # 设置图表样式
        self.health_ax.spines['top'].set_visible(False)
        self.health_ax.spines['right'].set_visible(False)
        self.health_ax.spines['left'].set_color('#bdc3c7')
        self.health_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.health_ax.set_xlabel('时间', fontsize=12, color='#34495e')
        self.health_ax.set_ylabel('健康评分', fontsize=12, color='#34495e')
        
        # 设置标题
        self.health_ax.set_title('健康评分趋势图', fontsize=14, color='#2c3e50')
        
        # 设置网格线
        self.health_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    def _init_truck_chart(self):
        """初始化重车流量统计图"""
        # 创建图表布局
        chart_layout = QVBoxLayout(self.truck_chart_container)
        
        # 创建Figure对象
        self.truck_figure = Figure(figsize=(8, 6), dpi=100)
        
        # 设置图表背景为透明
        self.truck_figure.patch.set_alpha(0)
        
        # 创建画布
        self.truck_canvas = FigureCanvas(self.truck_figure)
        self.truck_canvas.setStyleSheet("background-color: transparent;")
        
        # 添加画布到布局
        chart_layout.addWidget(self.truck_canvas)
        
        # 创建图表
        self.truck_ax = self.truck_figure.add_subplot(111)
        
        # 设置图表背景为透明
        self.truck_ax.set_facecolor('none')
        
        # 设置图表样式
        self.truck_ax.spines['top'].set_visible(False)
        self.truck_ax.spines['right'].set_visible(False)
        self.truck_ax.spines['left'].set_color('#bdc3c7')
        self.truck_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.truck_ax.set_xlabel('日期', fontsize=12, color='#34495e')
        self.truck_ax.set_ylabel('重车数量', fontsize=12, color='#34495e')
        
        # 设置标题
        self.truck_ax.set_title('重车流量统计图', fontsize=14, color='#2c3e50')
        
        # 设置网格线
        self.truck_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    def _load_data(self):
        """加载历史记录数据"""
        try:
            from utils.db_manager import DBManager
            db = DBManager()
            
            # 获取历史记录数据
            self.history_data = db.get_history(limit=100)  # 获取最近100条记录
            
            # 更新表格
            self._update_table()
            
            # 更新图表
            self._update_charts()
            
        except Exception as e:
            print(f"加载历史数据失败: {str(e)}")
    
    def _update_table(self):
        """更新表格显示"""
        # 清空表格
        self.table_widget.setRowCount(0)
        
        # 添加数据行
        for i, record in enumerate(self.history_data):
            # 获取记录信息
            record_id = record["id"]
            project_name = record["project_name"]
            record_type = record["type"]
            score = record["score"]
            timestamp = record["timestamp"]
            details = record.get("details", None)
            
            # 生成结果摘要
            if record_type == "裂缝检测" and details:
                result_summary = f"裂缝数量: {details[2]}, 最大宽度: {details[1]:.2f}mm"
            elif record_type == "交通监测" and details:
                result_summary = f"总车辆: {details[0]}, 重车: {details[1]}"
            else:
                result_summary = "暂无详情"
            
            # 插入新行
            self.table_widget.insertRow(i)
            
            # 设置单元格内容
            self.table_widget.setItem(i, 0, QTableWidgetItem(timestamp))
            self.table_widget.setItem(i, 1, QTableWidgetItem(record_type))
            self.table_widget.setItem(i, 2, QTableWidgetItem(result_summary))
            self.table_widget.setItem(i, 3, QTableWidgetItem(f"{score:.1f}"))
            
            # 添加操作按钮
            view_btn = QPushButton("查看详情")
            view_btn.clicked.connect(lambda checked, idx=i: self._on_view_details(idx))
            self.table_widget.setCellWidget(i, 4, view_btn)
        
        # 调整列宽
        self.table_widget.resizeColumnsToContents()
        
        # 设置最后一列宽度固定
        self.table_widget.setColumnWidth(4, 100)
    
    def _update_charts(self):
        """更新图表显示"""
        self._update_health_chart()
        self._update_truck_chart()
    
    def _update_health_chart(self):
        """更新健康评分趋势图"""
        # 清空图表
        self.health_ax.clear()
        
        # 准备数据
        dates = []
        scores = []
        
        for record in self.history_data:
            record_type = record["type"]
            score = record["score"]
            timestamp = record["timestamp"]
            # 提取日期部分
            date_str = timestamp.split(' ')[0]
            dates.append(date_str)
            scores.append(score)
        
        # 反转列表，使时间顺序正确
        dates.reverse()
        scores.reverse()
        
        # 绘制折线图
        self.health_ax.plot(dates, scores, color='#3498db', linewidth=2, marker='o', markersize=4)
        
        # 设置图表样式
        self.health_ax.spines['top'].set_visible(False)
        self.health_ax.spines['right'].set_visible(False)
        self.health_ax.spines['left'].set_color('#bdc3c7')
        self.health_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.health_ax.set_xlabel('时间', fontsize=12, color='#34495e')
        self.health_ax.set_ylabel('健康评分', fontsize=12, color='#34495e')
        
        # 设置标题
        self.health_ax.set_title('健康评分趋势图', fontsize=14, color='#2c3e50')
        
        # 设置网格线
        self.health_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
        
        # 设置X轴标签旋转
        plt.xticks(rotation=45, ha='right')
        
        # 调整布局
        self.health_figure.tight_layout()
        
        # 刷新图表
        self.health_canvas.draw()
    
    def _update_truck_chart(self):
        """更新重车流量统计图"""
        # 清空图表
        self.truck_ax.clear()
        
        # 按日期统计重车数量
        truck_stats = {}
        
        for record in self.history_data:
            record_type = record["type"]
            timestamp = record["timestamp"]
            details = record.get("details", None)
            
            if record_type == "交通监测" and details:
                # 提取日期部分
                date_str = timestamp.split(' ')[0]
                truck_count = details[1]  # 重车数量
                
                if date_str in truck_stats:
                    truck_stats[date_str] += truck_count
                else:
                    truck_stats[date_str] = truck_count
        
        # 准备数据
        dates = sorted(truck_stats.keys())
        truck_counts = [truck_stats[date] for date in dates]
        
        # 绘制柱状图
        self.truck_ax.bar(dates, truck_counts, color='#e74c3c', alpha=0.8)
        
        # 设置图表样式
        self.truck_ax.spines['top'].set_visible(False)
        self.truck_ax.spines['right'].set_visible(False)
        self.truck_ax.spines['left'].set_color('#bdc3c7')
        self.truck_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.truck_ax.set_xlabel('日期', fontsize=12, color='#34495e')
        self.truck_ax.set_ylabel('重车数量', fontsize=12, color='#34495e')
        
        # 设置标题
        self.truck_ax.set_title('重车流量统计图', fontsize=14, color='#2c3e50')
        
        # 设置网格线
        self.truck_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7', axis='y')
        
        # 设置X轴标签旋转
        plt.xticks(rotation=45, ha='right')
        
        # 调整布局
        self.truck_figure.tight_layout()
        
        # 刷新图表
        self.truck_canvas.draw()
    
    def _on_table_row_clicked(self, row, column):
        """表格行点击事件"""
        self._on_view_details(row)
    
    def _on_view_details(self, row):
        """查看记录详情"""
        if 0 <= row < len(self.history_data):
            record = self.history_data[row]
            record_id = record["id"]
            project_name = record["project_name"]
            record_type = record["type"]
            score = record["score"]
            timestamp = record["timestamp"]
            details = record.get("details", None)
            
            # 创建详情对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("检测详情")
            dialog.setFixedSize(600, 500)
            
            # 创建对话框布局
            dialog_layout = QVBoxLayout(dialog)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            # 创建滚动区域内容
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            
            # 添加基本信息
            info_group = QGroupBox("基本信息")
            info_layout = QGridLayout(info_group)
            
            info_layout.addWidget(QLabel("项目名称:"), 0, 0)
            info_layout.addWidget(QLabel(project_name), 0, 1)
            
            info_layout.addWidget(QLabel("检测类型:"), 1, 0)
            info_layout.addWidget(QLabel(record_type), 1, 1)
            
            info_layout.addWidget(QLabel("检测时间:"), 2, 0)
            info_layout.addWidget(QLabel(timestamp), 2, 1)
            
            info_layout.addWidget(QLabel("健康评分:"), 3, 0)
            info_layout.addWidget(QLabel(f"{score:.1f}"), 3, 1)
            
            content_layout.addWidget(info_group)
            
            # 根据记录类型显示不同内容
            if record_type == "裂缝检测" and details:
                # 显示裂缝检测详情和图片
                crack_group = QGroupBox("裂缝检测详情")
                crack_layout = QVBoxLayout(crack_group)
                
                # 添加裂缝统计信息
                stats_layout = QGridLayout()
                stats_layout.addWidget(QLabel("裂缝数量:"), 0, 0)
                stats_layout.addWidget(QLabel(str(details[2])), 0, 1)
                
                stats_layout.addWidget(QLabel("最大宽度:"), 1, 0)
                stats_layout.addWidget(QLabel(f"{details[1]:.2f}mm"), 1, 1)
                
                crack_layout.addLayout(stats_layout)
                
                # 添加图片显示
                image_path = details[0]
                if os.path.exists(image_path):
                    image_label = QLabel("检测图片")
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; margin-bottom: 5px; }")
                    crack_layout.addWidget(image_label)
                    
                    pixmap = QPixmap(image_path)
                    image_widget = QLabel()
                    image_widget.setPixmap(pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    image_widget.setAlignment(Qt.AlignCenter)
                    crack_layout.addWidget(image_widget)
                else:
                    crack_layout.addWidget(QLabel(f"图片文件不存在: {image_path}"))
                
                content_layout.addWidget(crack_group)
                
            elif record_type == "交通监测" and details:
                # 显示交通监测详情
                traffic_group = QGroupBox("交通监测详情")
                traffic_layout = QGridLayout(traffic_group)
                
                traffic_layout.addWidget(QLabel("总车辆数:"), 0, 0)
                traffic_layout.addWidget(QLabel(str(details[0])), 0, 1)
                
                traffic_layout.addWidget(QLabel("重车数量:"), 1, 0)
                traffic_layout.addWidget(QLabel(str(details[1])), 1, 1)
                
                traffic_layout.addWidget(QLabel("轿车数量:"), 2, 0)
                traffic_layout.addWidget(QLabel(str(details[2])), 2, 1)
                
                traffic_layout.addWidget(QLabel("公交车数量:"), 3, 0)
                traffic_layout.addWidget(QLabel(str(details[3])), 3, 1)
                
                content_layout.addWidget(traffic_group)
            
            # 设置滚动区域内容
            scroll_area.setWidget(content_widget)
            
            # 添加到对话框
            dialog_layout.addWidget(scroll_area)
            
            # 显示对话框
            dialog.exec_()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    
    history_page = HistoryPage()
    layout.addWidget(history_page)
    
    window.setWindowTitle("历史记录页面测试")
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec_())
