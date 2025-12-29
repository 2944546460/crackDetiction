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
    QMessageBox, QLineEdit, QFormLayout, QDoubleSpinBox, QSpinBox,
    QDateEdit, QComboBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QDate
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
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

class EditRecordDialog(QDialog):
    """编辑记录对话框"""
    def __init__(self, record_type, details=None, score=0.0, parent=None):
        super().__init__(parent)
        self.record_type = record_type
        self.initial_score = score
        self.setWindowTitle(f"编辑{record_type}详情")
        self.setFixedWidth(350)
        self._init_ui(details)
        
    def _init_ui(self, details):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 健康分字段 (所有类型通用)
        self.score_spin = QDoubleSpinBox()
        self.score_spin.setRange(0.0, 100.0)
        self.score_spin.setDecimals(1)
        self.score_spin.setValue(self.initial_score)
        form_layout.addRow("健康评分:", self.score_spin)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        form_layout.addRow(line)
        
        if self.record_type == "裂缝检测":
            current_width = details[1] if details and len(details) > 1 else 0.0
            current_count = details[2] if details and len(details) > 2 else 0
            
            self.width_spin = QDoubleSpinBox()
            self.width_spin.setRange(0.0, 100.0)
            self.width_spin.setDecimals(2)
            self.width_spin.setSuffix(" mm")
            self.width_spin.setValue(current_width)
            
            self.count_spin = QSpinBox()
            self.count_spin.setRange(0, 1000)
            self.count_spin.setValue(current_count)
            
            form_layout.addRow("最大裂缝宽度:", self.width_spin)
            form_layout.addRow("裂缝数量:", self.count_spin)
            
        elif self.record_type == "交通监测":
            # [total, truck, car, bus]
            current_total = details[0] if details and len(details) > 0 else 0
            current_truck = details[1] if details and len(details) > 1 else 0
            current_car = details[2] if details and len(details) > 2 else 0
            current_bus = details[3] if details and len(details) > 3 else 0
            
            self.total_spin = QSpinBox()
            self.total_spin.setRange(0, 10000)
            self.total_spin.setValue(current_total)
            
            self.truck_spin = QSpinBox()
            self.truck_spin.setRange(0, 10000)
            self.truck_spin.setValue(current_truck)
            
            self.car_spin = QSpinBox()
            self.car_spin.setRange(0, 10000)
            self.car_spin.setValue(current_car)
            
            self.bus_spin = QSpinBox()
            self.bus_spin.setRange(0, 10000)
            self.bus_spin.setValue(current_bus)
            
            form_layout.addRow("总车辆数:", self.total_spin)
            form_layout.addRow("重车数量:", self.truck_spin)
            form_layout.addRow("小车数量:", self.car_spin)
            form_layout.addRow("公交车数量:", self.bus_spin)
            
            # 自动计算总数逻辑
            self.truck_spin.valueChanged.connect(self._update_total)
            self.car_spin.valueChanged.connect(self._update_total)
            self.bus_spin.valueChanged.connect(self._update_total)
            
        else:
            label = QLabel("当前记录类型不支持手动编辑详情")
            form_layout.addRow(label)
            
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存修改")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 5px; font-weight: bold;")
        self.cancel_btn = QPushButton("取消")
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _update_total(self):
        """当各车型数量变化时，自动更新总车辆数"""
        if hasattr(self, 'total_spin'):
            total = self.truck_spin.value() + self.car_spin.value() + self.bus_spin.value()
            self.total_spin.setValue(total)

    def get_values(self):
        score = self.score_spin.value()
        if self.record_type == "裂缝检测":
            return score, self.width_spin.value(), self.count_spin.value()
        elif self.record_type == "交通监测":
            return score, self.total_spin.value(), self.truck_spin.value(), self.car_spin.value(), self.bus_spin.value()
        return score, None

class HistoryPage(QWidget):
    """历史记录页面类"""
    
    def __init__(self):
        """初始化历史记录页面"""
        super().__init__()
        
        # 设置中文字体
        rcParams['font.family'] = ['Microsoft YaHei', 'SimHei']
        
        # 历史记录数据和分页状态
        self.history_data = []
        self.current_page = 1
        self.page_size = 15
        self.total_records = 0
        
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

        # 1. 筛选与工具栏
        filter_card = QFrame()
        filter_card.setStyleSheet("background: transparent; border: none;")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(0, 0, 0, 5)
        
        # 统一控件样式
        control_style = """
            QComboBox, QDateEdit {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 120px;
                background: white;
                color: #606266;
            }
            QComboBox:hover, QDateEdit:hover {
                border-color: #409eff;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            /* 日历弹窗样式优化 */
            QCalendarWidget QWidget { 
                background-color: white;
            }
            QCalendarWidget QTableView {
                border: 1px solid #e4e7ed;
                selection-background-color: #409eff;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #606266;
                selection-background-color: #409eff;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #c0c4cc;
            }
            QCalendarWidget QToolButton {
                color: #303133;
                background-color: transparent;
                border: none;
                margin: 5px;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #f5f7fa;
                color: #409eff;
            }
            QCalendarWidget QToolButton#qt_calendar_prevbutton {
                qproperty-icon: none;
                qproperty-text: "<";
            }
            QCalendarWidget QToolButton#qt_calendar_nextbutton {
                qproperty-icon: none;
                qproperty-text: ">";
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 14px;
                color: #303133;
                background-color: white;
                selection-background-color: #409eff;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #e4e7ed;
                color: #606266;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #f5f7fa;
                color: #409eff;
            }
        """

        # 记录类型筛选
        filter_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部", "裂缝检测", "交通监测"])
        self.type_combo.setStyleSheet(control_style)
        self.type_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addSpacing(15)
        
        # 时间筛选
        filter_layout.addWidget(QLabel("从:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd") # 确保日期显示完整
        self.start_date_edit.setStyleSheet(control_style)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1)) # 默认一个月前
        self.start_date_edit.dateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.start_date_edit)
        
        filter_layout.addWidget(QLabel("至:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd") # 确保日期显示完整
        self.end_date_edit.setStyleSheet(control_style)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.end_date_edit)
        
        filter_layout.addStretch() # 弹簧
        
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
        filter_layout.addWidget(refresh_btn)

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
        filter_layout.addWidget(export_btn)
        
        table_layout.addWidget(filter_card)
        
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
        self.table_widget.setColumnWidth(4, 220) # 给操作按钮留足空间，防止遮挡
        
        # 连接表格点击事件
        self.table_widget.cellClicked.connect(self._on_table_row_clicked)
        
        table_layout.addWidget(self.table_widget)
        
        # 3. 分页栏
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 5, 0, 0)
        
        self.page_info_label = QLabel("第 1 页 / 共 1 页 (总计 0 条)")
        self.page_info_label.setStyleSheet("color: #666666; font-size: 13px;")
        pagination_layout.addWidget(self.page_info_label)
        
        pagination_layout.addStretch()
        
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setFixedWidth(80)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev_page)
        
        self.next_btn = QPushButton("下一页")
        self.next_btn.setFixedWidth(80)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next_page)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10 条/页", "15 条/页", "20 条/页", "50 条/页"])
        self.page_size_combo.setCurrentText(f"{self.page_size} 条/页")
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addSpacing(10)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addSpacing(15)
        pagination_layout.addWidget(self.page_size_combo)
        
        table_layout.addLayout(pagination_layout)
        
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
        self.health_canvas.setMinimumSize(200, 150)
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
        self.truck_canvas.setMinimumSize(200, 150)
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
        """加载历史记录数据 (支持分页和筛选)"""
        try:
            from utils.db_manager import DBManager
            db = DBManager()
            
            # 获取筛选参数
            record_type = self.type_combo.currentText()
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # 计算偏移量
            offset = (self.current_page - 1) * self.page_size
            
            # 获取数据和总数
            self.history_data = db.get_history(
                limit=self.page_size, 
                offset=offset, 
                record_type=record_type, 
                start_date=start_date, 
                end_date=end_date
            )
            self.total_records = db.get_history_count(
                record_type=record_type, 
                start_date=start_date, 
                end_date=end_date
            )
            
            # 更新分页信息
            total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
            self.page_info_label.setText(f"第 {self.current_page} 页 / 共 {total_pages} 页 (总计 {self.total_records} 条)")
            
            # 更新按钮状态
            self.prev_btn.setEnabled(self.current_page > 1)
            self.next_btn.setEnabled(self.current_page < total_pages)
            
            # 更新表格
            self._update_table()
            
            # 更新图表
            self._update_charts()
            
        except Exception as e:
            logger.error(f"加载历史数据失败: {str(e)}")

    def _on_filter_changed(self):
        """筛选条件改变时，重置页码并重新加载"""
        self.current_page = 1
        self._load_data()

    def _on_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data()

    def _on_next_page(self):
        """下一页"""
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self._load_data()

    def _on_page_size_changed(self, text):
        """每页条数改变时，重置页码并重新加载"""
        try:
            new_size = int(text.split(' ')[0])
            if new_size != self.page_size:
                self.page_size = new_size
                self.current_page = 1
                self._load_data()
        except ValueError:
            pass
    
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
            view_btn = QPushButton("详情")
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setFixedWidth(60)
            view_btn.setFixedHeight(30)
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
            
            edit_btn = QPushButton("编辑")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setFixedWidth(60)
            edit_btn.setFixedHeight(30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    color: #ffffff;
                    background-color: #27ae60;
                    border: none;
                    border-radius: 4px;
                    padding: 0;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #219150; }
            """)
            # 只有裂缝检测和交通监测支持编辑
            if record_type not in ["裂缝检测", "交通监测"]:
                edit_btn.setEnabled(False)
                edit_btn.setStyleSheet("background-color: #bdc3c7; color: #ffffff; border-radius: 4px;")
            edit_btn.clicked.connect(lambda checked, rec=record: self._on_edit_record(rec))

            delete_btn = QPushButton("删除")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setFixedWidth(60)
            delete_btn.setFixedHeight(30)
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
            btn_layout.setContentsMargins(5, 0, 5, 0) 
            btn_layout.setSpacing(10) # 按钮间距
            btn_layout.setAlignment(Qt.AlignCenter) # 确保水平和垂直都居中
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
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

    def _on_edit_record(self, record):
        """编辑记录处理"""
        record_id = record["id"]
        record_type = record["type"]
        score = record["score"]
        details = record.get("details")
        
        if record_type not in ["裂缝检测", "交通监测"] or not details:
            QMessageBox.information(self, "提示", "该记录类型暂不支持编辑")
            return
            
        dialog = EditRecordDialog(record_type, details, score, self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                from utils.db_manager import DBManager
                db = DBManager()
                success = False
                
                if record_type == "裂缝检测":
                    new_score, new_width, new_count = dialog.get_values()
                    success = db.update_crack_details(record_id, new_width, new_count, new_score)
                elif record_type == "交通监测":
                    new_score, new_total, new_truck, new_car, new_bus = dialog.get_values()
                    success = db.update_traffic_stats(record_id, new_total, new_truck, new_car, new_bus, new_score)
                
                if success:
                    # 重新加载数据并刷新页面
                    self._load_data()
                    QMessageBox.information(self, "成功", "记录已成功更新")
                else:
                    QMessageBox.error(self, "失败", "更新记录失败，请检查数据库状态")
            except Exception as e:
                logger.error(f"编辑记录异常: {e}")
                QMessageBox.critical(self, "错误", f"更新过程中发生异常: {str(e)}")

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
        
        # 准备数据并按时间排序
        chart_data = []
        for record in self.history_data:
            score = record["score"]
            timestamp_str = record["timestamp"]
            try:
                # 解析完整时间对象
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                chart_data.append((dt, score))
            except Exception as e:
                logger.error(f"解析时间字符串失败: {timestamp_str}, 错误: {e}")
        
        # 按时间升序排序
        chart_data.sort(key=lambda x: x[0])
        
        if not chart_data:
            self.health_ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', color='#999', transform=self.health_ax.transAxes)
        else:
            dates = [x[0] for x in chart_data]
            scores = [x[1] for x in chart_data]
            
            # 绘制阈值背景带
            # 注意：在使用时间轴时，axhspan 的 x 范围会自动覆盖
            self.health_ax.axhspan(90, 100, color='green', alpha=0.1, label='优秀')
            self.health_ax.axhspan(60, 90, color='yellow', alpha=0.1, label='良好')
            self.health_ax.axhspan(0, 60, color='red', alpha=0.1, label='警戒')
            
            # 增加基准线（警戒线）
            self.health_ax.axhline(y=60, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
            
            # 绘制折线图
            self.health_ax.plot(dates, scores, color='#3498db', linewidth=2.5, marker='o', 
                               markersize=4, markerfacecolor='white', markeredgewidth=1.5, label='健康分')
            
            # 设置 X 轴格式化
            self.health_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            
            # 让时间标签自动倾斜
            self.health_figure.autofmt_xdate()
        
        # 设置坐标轴范围
        self.health_ax.set_ylim(0, 105)
        
        # 设置图表样式
        self.health_ax.spines['top'].set_visible(False)
        self.health_ax.spines['right'].set_visible(False)
        self.health_ax.spines['left'].set_color('#bdc3c7')
        self.health_ax.spines['bottom'].set_color('#bdc3c7')
        
        # 设置坐标轴标签
        self.health_ax.set_xlabel('检测时间', fontsize=10, color='#666')
        self.health_ax.set_ylabel('评分 (0-100)', fontsize=10, color='#666')
        
        # 设置标题
        self.health_ax.set_title('桥梁健康状态趋势', fontsize=12, color='#333', pad=15, fontweight='bold')
        
        # 设置网格线
        self.health_ax.grid(True, linestyle=':', alpha=0.4, color='#bdc3c7')
        
        # 调整布局
        try:
            self.health_figure.tight_layout()
        except:
            pass
        
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
        try:
            self.truck_figure.tight_layout()
        except:
            pass
        
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
            dialog.setFixedSize(600, 650)
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
            
            # 添加评分依据 (响应用户对健康分依据的疑问)
            basis_group = QGroupBox("评分依据 (Health Score Basis)")
            basis_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #3498db;
                    border-radius: 6px;
                    margin-top: 15px;
                    padding-top: 10px;
                    background-color: #f8fbff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #2980b9;
                }
            """)
            basis_layout = QVBoxLayout(basis_group)
            
            basis_text = QLabel()
            basis_text.setWordWrap(True)
            basis_text.setStyleSheet("color: #444; line-height: 1.6; font-size: 13px; padding: 10px;")
            
            if record_type == "裂缝检测":
                max_width = details[1] if details else 0
                crack_count = details[2] if details else 0
                
                # 重新计算各项扣分以展示
                if max_width < 0.1: w_deduction = 0
                elif max_width <= 0.2: w_deduction = 5 + (max_width - 0.1) * 50
                elif max_width <= 0.5: w_deduction = 10 + (max_width - 0.2) * 66.7
                else: w_deduction = 30 + min(40, (max_width - 0.5) * 80)
                
                c_deduction = min(30, crack_count * 2)
                
                basis_text.setText(
                    f"<div style='margin-bottom: 8px;'><b>评分公式：</b> <span style='color: #2980b9;'>100 - 宽度扣分 - 数量扣分</span></div>"
                    f"<table width='100%' style='border-collapse: collapse;'>"
                    f"<tr><td style='padding: 4px;'>1. <b>宽度扣分:</b></td><td style='color: #e74c3c; font-weight: bold;'>-{w_deduction:.1f} 分</td></tr>"
                    f"<tr><td colspan='2' style='color: #7f8c8d; font-size: 12px; padding-left: 15px;'>依据：最大宽度 {max_width:.2f}mm (标准: &lt;0.1mm不扣分, 0.2mm扣10分, 0.5mm扣30分)</td></tr>"
                    f"<tr><td style='padding: 4px; padding-top: 10px;'>2. <b>数量扣分:</b></td><td style='color: #e74c3c; font-weight: bold; padding-top: 10px;'>-{c_deduction:.1f} 分</td></tr>"
                    f"<tr><td colspan='2' style='color: #7f8c8d; font-size: 12px; padding-left: 15px;'>依据：发现 {crack_count} 条裂缝 (标准: 每条扣2分，上限30分)</td></tr>"
                    f"</table>"
                    f"<br><div style='border-top: 1px solid #ddd; padding-top: 8px; color: #2c3e50;'><b>最终得分：{score:.1f}</b></div>"
                )
            elif record_type == "交通监测":
                total = details[0] if details else 0
                truck = details[1] if details else 0
                
                # 重新计算各项扣分以展示
                truck_ratio = truck / total if total > 0 else 0
                if truck_ratio < 0.1: t_deduction = truck_ratio * 50
                elif truck_ratio <= 0.3: t_deduction = 5 + (truck_ratio - 0.1) * 100
                else: t_deduction = 25 + min(35, (truck_ratio - 0.3) * 116.7)
                
                f_deduction = min(30, total / 10.0)
                
                basis_text.setText(
                    f"<div style='margin-bottom: 8px;'><b>评分公式：</b> <span style='color: #2980b9;'>100 - 重车比扣分 - 流量扣分</span></div>"
                    f"<table width='100%' style='border-collapse: collapse;'>"
                    f"<tr><td style='padding: 4px;'>1. <b>重车比扣分:</b></td><td style='color: #e74c3c; font-weight: bold;'>-{t_deduction:.1f} 分</td></tr>"
                    f"<tr><td colspan='2' style='color: #7f8c8d; font-size: 12px; padding-left: 15px;'>依据：重车比例 {truck_ratio*100:.1f}% (标准: &lt;10%扣0-5, 30%扣25, &gt;30%严重负载)</td></tr>"
                    f"<tr><td style='padding: 4px; padding-top: 10px;'>2. <b>流量负荷扣分:</b></td><td style='color: #e74c3c; font-weight: bold; padding-top: 10px;'>-{f_deduction:.1f} 分</td></tr>"
                    f"<tr><td colspan='2' style='color: #7f8c8d; font-size: 12px; padding-left: 15px;'>依据：累计流量 {total} 辆 (标准: 每10辆扣1分，上限30分)</td></tr>"
                    f"</table>"
                    f"<br><div style='border-top: 1px solid #ddd; padding-top: 8px; color: #2c3e50;'><b>最终得分：{score:.1f}</b></div>"
                )
            
            basis_layout.addWidget(basis_text)
            content_layout.addWidget(basis_group)
            
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
