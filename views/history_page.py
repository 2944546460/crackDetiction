#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录页面

用于查询和回溯过往的检测数据
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QTableWidgetItem, QLabel, QFrame, QSplitter, QPushButton, QDialog,
    QScrollArea, QGridLayout, QSizePolicy, QHeaderView, QProgressDialog,
    QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import os
import sys
from utils.logger import logger

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
        # 设置页面背景色
        self.setStyleSheet("background-color: #f4f6f9;")

        # 创建主布局（垂直布局）
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- 上半部分：表格卡片 ---
        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_card.setStyleSheet("""
            QFrame#table_card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setSpacing(15)

        # 1. 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 标题
        table_title = QLabel("检测记录列表")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333; font-family: 'Microsoft YaHei'; border: none; background: transparent;")
        toolbar_layout.addWidget(table_title)
        
        toolbar_layout.addStretch() # 弹簧
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        refresh_btn.clicked.connect(self._load_data)
        toolbar_layout.addWidget(refresh_btn)

        # 导出按钮
        export_btn = QPushButton("导出 Excel")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219150; }
        """)
        export_btn.clicked.connect(self._export_data) # 绑定导出功能
        toolbar_layout.addWidget(export_btn)
        
        table_layout.addLayout(toolbar_layout)
        
        # 2. 表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["时间", "类型", "结果摘要", "健康分", "操作"])
        
        # 表格样式
        self.table_widget.setStyleSheet("""
            QTableWidget {
                border: 1px solid #eeeeee;
                background-color: white;
                gridline-color: #eeeeee;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #eeeeee;
                font-weight: bold;
                color: #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #333333;
            }
        """)
        
        # 属性设置
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.table_widget.setAlternatingRowColors(True) # 隔行变色
        self.table_widget.verticalHeader().setVisible(False) # 隐藏行号
        
        # 列宽自适应
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # 自动铺满
        header.setSectionResizeMode(4, QHeaderView.Fixed) # 最后一列固定宽度
        self.table_widget.setColumnWidth(4, 200) # 给操作按钮留足空间，防止遮挡
        
        # 连接表格点击事件
        self.table_widget.cellClicked.connect(self._on_table_row_clicked)
        
        table_layout.addWidget(self.table_widget)
        
        # 添加表格卡片到主布局 (stretch=2)
        main_layout.addWidget(table_card, 2)
        
        # --- 下半部分：图表卡片 ---
        charts_card = QFrame()
        charts_card.setObjectName("charts_card")
        charts_card.setStyleSheet("""
            QFrame#charts_card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        # 设置最小高度
        charts_card.setMinimumHeight(300)
        
        charts_layout = QVBoxLayout(charts_card)
        charts_layout.setSpacing(10)
        
        # 标题
        chart_title = QLabel("数据趋势分析")
        chart_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333; font-family: 'Microsoft YaHei'; border: none; background: transparent; margin-bottom: 5px;")
        charts_layout.addWidget(chart_title)
        
        # 图表容器布局
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(20)
        
        # 左图：健康评分趋势图
        self.health_chart_container = QFrame()
        self.health_chart_container.setStyleSheet("background: transparent; border: none;")
        self._init_health_chart()
        
        # 右图：重车流量统计图
        self.truck_chart_container = QFrame()
        self.truck_chart_container.setStyleSheet("background: transparent; border: none;")
        self._init_truck_chart()
        
        graphs_layout.addWidget(self.health_chart_container)
        graphs_layout.addWidget(self.truck_chart_container)
        
        charts_layout.addLayout(graphs_layout)
        
        # 添加图表卡片到主布局 (stretch=1)
        main_layout.addWidget(charts_card, 1)
    
    def _init_health_chart(self):
        """初始化健康评分趋势图"""
        # 创建图表布局
        chart_layout = QVBoxLayout(self.health_chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0) # 移除内边距
        
        # 创建Figure对象
        self.health_figure = Figure(figsize=(8, 6), dpi=100)
        
        # 设置图表背景为透明
        self.health_figure.patch.set_alpha(0)
        
        # 创建画布
        self.health_canvas = FigureCanvas(self.health_figure)
        self.health_canvas.setStyleSheet("background-color: transparent;")
        self.health_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
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
        self.health_ax.set_xlabel('时间', fontsize=10, color='#666')
        self.health_ax.set_ylabel('健康评分', fontsize=10, color='#666')
        
        # 设置标题 (稍微调小字体以适应紧凑布局)
        self.health_ax.set_title('健康评分趋势', fontsize=12, color='#333', pad=10)
        
        # 设置网格线
        self.health_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    def _init_truck_chart(self):
        """初始化重车流量统计图"""
        # 创建图表布局
        chart_layout = QVBoxLayout(self.truck_chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建Figure对象
        self.truck_figure = Figure(figsize=(8, 6), dpi=100)
        
        # 设置图表背景为透明
        self.truck_figure.patch.set_alpha(0)
        
        # 创建画布
        self.truck_canvas = FigureCanvas(self.truck_figure)
        self.truck_canvas.setStyleSheet("background-color: transparent;")
        self.truck_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
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
        self.truck_ax.set_xlabel('日期', fontsize=10, color='#666')
        self.truck_ax.set_ylabel('重车数量', fontsize=10, color='#666')
        
        # 设置标题
        self.truck_ax.set_title('重车流量统计', fontsize=12, color='#333', pad=10)
        
        # 设置网格线
        self.truck_ax.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7', axis='y')
    
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
            logger.error(f"加载历史数据失败: {str(e)}")
    
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
            
            score_item = QTableWidgetItem(f"{score:.1f}")
            score_item.setTextAlignment(Qt.AlignCenter)
            if score < 60:
                score_item.setForeground(Qt.red)
            elif score > 90:
                score_item.setForeground(Qt.darkGreen)
            self.table_widget.setItem(i, 3, score_item)
            
            # 添加操作按钮
            view_btn = QPushButton("查看详情")
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setFixedWidth(85)  # 稍微加宽一点，确保文字不拥挤
            view_btn.setFixedHeight(30)  # 稍微加高一点，垂直居中更明显
            view_btn.setStyleSheet("""
                QPushButton {
                    color: #ffffff;
                    background-color: #3498db;
                    border: none;
                    border-radius: 4px;
                    padding: 0;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #2980b9; }
            """)
            view_btn.clicked.connect(lambda checked, idx=i: self._on_view_details(idx))
            
            delete_btn = QPushButton("删除")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setFixedWidth(85)  # 统一固定宽度
            delete_btn.setFixedHeight(30)  # 统一固定高度
            delete_btn.setStyleSheet("""
                QPushButton {
                    color: #ffffff;
                    background-color: #e74c3c;
                    border: none;
                    border-radius: 4px;
                    padding: 0;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)
            delete_btn.clicked.connect(lambda checked, rid=record_id: self._on_delete_record(rid))
            
            # 创建一个Widget来排列按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 0, 15, 0) # 左侧留5px，右侧留15px防止遮挡
            btn_layout.setSpacing(10) # 按钮间距
            btn_layout.setAlignment(Qt.AlignCenter) # 确保水平和垂直都居中
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(delete_btn)
            self.table_widget.setCellWidget(i, 4, btn_widget)
            
            # 适当增加行高
            self.table_widget.setRowHeight(i, 48)
        
        # 不再需要手动 resizeColumnsToContents，因为使用了 Stretch 模式
        # self.table_widget.resizeColumnsToContents()
        
        # 设置最后一列宽度固定 (通过HeaderView设置了，这里无需重复)
    
    def _export_data(self):
        """导出数据到 Excel"""
        if not self.history_data:
            QMessageBox.warning(self, "警告", "没有历史数据可供导出")
            return
            
        try:
            # 准备数据，展平详情
            export_list = []
            for item in self.history_data:
                row = {
                    "ID": item["id"],
                    "项目名称": item["project_name"],
                    "检测类型": item["type"],
                    "得分": item["score"],
                    "时间戳": item["timestamp"]
                }
                
                # 添加详情
                details = item.get("details")
                if details:
                    if item["type"] == "裂缝检测":
                        row["裂缝路径"] = details[0]
                        row["最大宽度(mm)"] = details[1]
                        row["裂缝数量"] = details[2]
                    elif item["type"] == "交通监测":
                        row["总车流量"] = details[0]
                        row["重车数量"] = details[1]
                        row["小车数量"] = details[2]
                        row["客车数量"] = details[3]
                
                export_list.append(row)
            
            # 创建进度对话框
            self.progress_dialog = QProgressDialog("正在导出 Excel 数据...", "取消", 0, 100, self)
            self.progress_dialog.setWindowTitle("导出中")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setAutoClose(True)
            
            # 创建并启动导出线程
            from threads.export_thread import ExcelExportThread
            self.export_thread = ExcelExportThread(export_list, filename_prefix="Bridge_History")
            self.export_thread.progress_signal.connect(self.progress_dialog.setValue)
            self.export_thread.result_signal.connect(self._on_export_finished)
            
            # 连接取消按钮
            self.progress_dialog.canceled.connect(self.export_thread.stop)
            
            self.export_thread.start()
            self.progress_dialog.show()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出启动失败: {str(e)}")

    def _on_export_finished(self, result):
        """导出完成回调"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        if result.get("success"):
            filepath = result.get("filepath")
            QMessageBox.information(self, "导出成功", f"数据已成功导出至：\n{filepath}")
        else:
            QMessageBox.critical(self, "导出失败", f"导出 Excel 失败: {result.get('error')}")

    def _on_delete_record(self, record_id):
        """删除记录处理"""
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这条检测记录吗？此操作不可撤销。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from utils.db_manager import DBManager
                db = DBManager()
                if db.delete_record(record_id):
                    # 重新加载数据
                    self._load_data()
                    QMessageBox.information(self, "成功", "记录已成功删除")
                else:
                    QMessageBox.error(self, "失败", "删除记录失败，请检查数据库状态")
            except Exception as e:
                logger.error(f"删除记录异常: {e}")
                QMessageBox.critical(self, "错误", f"删除过程中发生异常: {str(e)}")

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
            score = record["score"]
            timestamp = record["timestamp"]
            # 提取日期部分
            date_str = timestamp.split(' ')[0]
            dates.append(date_str)
            scores.append(score)
        
        # 反转列表，使时间顺序正确
        dates.reverse()
        scores.reverse()
        
        if not dates:
            self.health_ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', color='#999')
        else:
            # 绘制阈值背景带
            self.health_ax.axhspan(90, 100, color='green', alpha=0.1, label='优秀')
            self.health_ax.axhspan(60, 90, color='yellow', alpha=0.1, label='良好')
            self.health_ax.axhspan(0, 60, color='red', alpha=0.1, label='警戒')
            
            # 增加基准线（警戒线）
            self.health_ax.axhline(y=60, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
            self.health_ax.text(len(dates)-0.5 if len(dates)>0 else 0, 62, "警戒线", color='red', fontsize=9, fontweight='bold')

            # 绘制折线图
            self.health_ax.plot(dates, scores, color='#3498db', linewidth=2.5, marker='o', 
                               markersize=6, markerfacecolor='white', markeredgewidth=2, label='健康分')
        
        # 设置坐标轴范围
        self.health_ax.set_ylim(0, 105)
        
        # 设置图表样式
        self.health_ax.spines['top'].set_visible(False)
        self.health_ax.spines['right'].set_visible(False)
        self.health_ax.spines['left'].set_color('#bdc3c7')
        self.health_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.health_ax.set_xlabel('检测日期', fontsize=10, color='#666')
        self.health_ax.set_ylabel('评分 (0-100)', fontsize=10, color='#666')
        
        # 设置标题
        self.health_ax.set_title('桥梁健康状态趋势', fontsize=12, color='#333', pad=15, fontweight='bold')
        
        # 设置网格线
        self.health_ax.grid(True, linestyle=':', alpha=0.4, color='#bdc3c7')
        
        # 设置X轴标签旋转
        if dates:
            self.health_ax.set_xticks(range(len(dates)))
            self.health_ax.set_xticklabels(dates, rotation=35, ha='right', fontsize=9)
        
        # 调整布局
        self.health_figure.tight_layout()
        
        # 刷新图表
        self.health_canvas.draw()
    
    def _update_truck_chart(self):
        """更新交通流量统计图 (升级为多折线图)"""
        # 清空图表
        self.truck_ax.clear()
        
        # 按日期统计各类车辆数量
        daily_stats = {}
        
        for record in self.history_data:
            record_type = record["type"]
            timestamp = record["timestamp"]
            details = record.get("details", None)
            
            if record_type == "交通监测" and details:
                # 提取日期部分
                date_str = timestamp.split(' ')[0]
                # 解析详情 [total, truck, car, bus]
                # 数据库存储结构为: total, truck, car, bus
                truck_count = details[1]
                car_count = details[2]
                bus_count = details[3]
                
                if date_str not in daily_stats:
                    daily_stats[date_str] = {'truck': 0, 'car': 0, 'bus': 0}
                
                daily_stats[date_str]['truck'] += truck_count
                daily_stats[date_str]['car'] += car_count
                daily_stats[date_str]['bus'] += bus_count
        
        # 准备数据
        dates = sorted(daily_stats.keys())
        truck_counts = [daily_stats[d]['truck'] for d in dates]
        car_counts = [daily_stats[d]['car'] for d in dates]
        bus_counts = [daily_stats[d]['bus'] for d in dates]
        
        if not dates:
             self.truck_ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', color='#999')
        else:
            # 绘制多折线图
            # 轿车: 蓝色
            self.truck_ax.plot(dates, car_counts, color='#3498db', linewidth=2, marker='s', 
                              markersize=4, label='轿车 (Car)')
            # 重车: 红色 (加粗，重点关注)
            self.truck_ax.plot(dates, truck_counts, color='#e74c3c', linewidth=3, marker='D', 
                              markersize=5, label='重车 (Truck)')
            # 巴士: 绿色
            self.truck_ax.plot(dates, bus_counts, color='#2ecc71', linewidth=2, marker='^', 
                              markersize=4, label='巴士 (Bus)')
            
            # 添加图例
            self.truck_ax.legend(loc='upper right', fontsize=8, frameon=True, facecolor='white', framealpha=0.8)
        
        # 设置图表样式
        self.truck_ax.spines['top'].set_visible(False)
        self.truck_ax.spines['right'].set_visible(False)
        self.truck_ax.spines['left'].set_color('#bdc3c7')
        self.truck_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.truck_ax.set_xlabel('日期', fontsize=10, color='#666')
        self.truck_ax.set_ylabel('通过数量 (辆)', fontsize=10, color='#666')
        
        # 设置标题
        self.truck_ax.set_title('交通流量多维度统计', fontsize=12, color='#333', pad=15, fontweight='bold')
        
        # 设置网格线
        self.truck_ax.grid(True, linestyle=':', alpha=0.4, color='#bdc3c7')
        
        # 设置X轴标签旋转
        if dates:
            self.truck_ax.set_xticks(range(len(dates)))
            self.truck_ax.set_xticklabels(dates, rotation=35, ha='right', fontsize=9)
        
        # 调整布局
        self.truck_figure.tight_layout()
        
        # 刷新图表
        self.truck_canvas.draw()
    
    def _on_table_row_clicked(self, row, column):
        """表格行点击事件"""
        # 注意：因为我们现在使用 setCellWidget 放置按钮，点击按钮可能不会触发此事件
        # 除非点击其他单元格。如果需要整行点击都弹出详情，保持原样即可。
        # 这里为了避免误触，可能希望只有点击按钮才弹出，或者保持现状。
        # 暂时保持现状。
        self._on_view_details(row)
    
    def _on_view_details(self, row):
        """查看记录详情"""
        if 0 <= row < len(self.history_data):
            record = self.history_data[row]
            project_name = record["project_name"]
            record_type = record["type"]
            score = record["score"]
            timestamp = record["timestamp"]
            details = record.get("details", None)
            
            # 创建详情对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("检测详情")
            dialog.setFixedSize(600, 500)
            dialog.setStyleSheet("background-color: #ffffff;")
            
            # 创建对话框布局
            dialog_layout = QVBoxLayout(dialog)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("border: none;")
            
            # 创建滚动区域内容
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            
            # 添加基本信息
            info_group = QGroupBox("基本信息")
            info_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            info_layout = QGridLayout(info_group)
            
            info_layout.addWidget(QLabel("项目名称:"), 0, 0)
            info_layout.addWidget(QLabel(project_name), 0, 1)
            
            info_layout.addWidget(QLabel("检测类型:"), 1, 0)
            info_layout.addWidget(QLabel(record_type), 1, 1)
            
            info_layout.addWidget(QLabel("检测时间:"), 2, 0)
            info_layout.addWidget(QLabel(timestamp), 2, 1)
            
            info_layout.addWidget(QLabel("健康评分:"), 3, 0)
            score_lbl = QLabel(f"{score:.1f}")
            if score < 60: score_lbl.setStyleSheet("color: red; font-weight: bold;")
            elif score > 90: score_lbl.setStyleSheet("color: green; font-weight: bold;")
            info_layout.addWidget(score_lbl, 3, 1)
            
            content_layout.addWidget(info_group)
            
            # 根据记录类型显示不同内容
            if record_type == "裂缝检测" and details:
                # 显示裂缝检测详情和图片
                crack_group = QGroupBox("裂缝检测详情")
                crack_group.setStyleSheet(info_group.styleSheet())
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
                    image_widget.setStyleSheet("border: 1px solid #ccc; padding: 2px;")
                    crack_layout.addWidget(image_widget)
                else:
                    crack_layout.addWidget(QLabel(f"图片文件不存在: {image_path}"))
                
                content_layout.addWidget(crack_group)
                
            elif record_type == "交通监测" and details:
                # 显示交通监测详情
                traffic_group = QGroupBox("交通监测详情")
                traffic_group.setStyleSheet(info_group.styleSheet())
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
    
    # 简单的测试窗口
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0,0,0,0)
    
    history_page = HistoryPage()
    layout.addWidget(history_page)
    
    window.setWindowTitle("历史记录页面测试")
    window.resize(1000, 800)
    window.show()
    
    sys.exit(app.exec_())
