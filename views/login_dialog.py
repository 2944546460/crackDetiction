#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户登录窗口

提供系统进入前的身份验证界面
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPixmap, QIcon

class LoginDialog(QDialog):
    """用户登录对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 1. 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(800, 500)
        
        # 2. 主容器（带阴影和圆角）
        self.container = QFrame(self)
        self.container.setObjectName("LoginContainer")
        self.container.setGeometry(10, 10, 780, 480)
        self.container.setStyleSheet("""
            #LoginContainer {
                background-color: white;
                border-radius: 15px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)
        
        # 3. 布局设计：左侧装饰，右侧表单
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- 左侧装饰面板 ---
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        self.left_panel.setFixedWidth(350)
        self.left_panel.setStyleSheet("""
            #LeftPanel {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2980b9, stop:1 #3498db);
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }
        """)
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.addStretch()
        
        # Logo 占位
        logo_label = QLabel("🌉")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 100px; color: white;")
        left_layout.addWidget(logo_label)
        
        # 欢迎文字
        welcome_title = QLabel("智桥卫士")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("color: white; font-size: 28px; font-weight: bold; font-family: 'Microsoft YaHei';")
        left_layout.addWidget(welcome_title)
        
        welcome_desc = QLabel("智慧监测 · 守护安全")
        welcome_desc.setAlignment(Qt.AlignCenter)
        welcome_desc.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px; margin-top: 10px;")
        left_layout.addWidget(welcome_desc)
        
        left_layout.addStretch()
        layout.addWidget(self.left_panel)
        
        # --- 右侧表单面板 ---
        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        self.right_panel.setStyleSheet("#RightPanel { background: white; border-top-right-radius: 15px; border-bottom-right-radius: 15px; }")
        
        # 使用 QGridLayout 来精确控制层叠关系
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(50, 0, 50, 40)
        self.right_layout.setSpacing(15)
        
        # 1. 顶部栏容器 (专门放关闭按钮)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 10, 0, 0)
        top_bar.addStretch()
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 32px;
                color: #bdc3c7;
                background-color: transparent;
                line-height: 40px;
            }
            QPushButton:hover {
                color: #e74c3c;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        top_bar.addWidget(self.close_btn)
        self.right_layout.addLayout(top_bar)
        
        # 2. 标题
        title_label = QLabel("系统登录")
        title_label.setFixedHeight(60) # 固定高度确保不被裁剪
        title_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-top: 10px;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        self.right_layout.addWidget(title_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setText("admin")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding-left: 15px;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                font-size: 14px;
                background: #f5f7fa;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background: white;
            }
        """)
        self.right_layout.addWidget(self.username_input)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setText("123456")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding-left: 15px;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                font-size: 14px;
                background: #f5f7fa;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background: white;
            }
        """)
        self.right_layout.addWidget(self.password_input)
        
        self.right_layout.addSpacing(10)
        
        # 登录按钮
        self.login_btn = QPushButton("立即登录")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3ea6e9, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
        self.login_btn.clicked.connect(self._handle_login)
        self.right_layout.addWidget(self.login_btn)
        
        # 退出按钮 (灰色小按钮)
        self.exit_btn = QPushButton("退出系统")
        self.exit_btn.setFixedHeight(40)  # 增加高度，防止文字被裁剪
        self.exit_btn.setMinimumWidth(100) # 确保有足够宽度
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #95a5a6;
                border: none;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #7f8c8d;
            }
        """)
        self.exit_btn.clicked.connect(self.reject)
        self.right_layout.addWidget(self.exit_btn, 0, Qt.AlignCenter) # 居中对齐
        
        self.right_layout.addStretch()
        
        layout.addWidget(self.right_panel)
        
        # 居中显示
        self._center()

    def _get_input_qss(self):
        """获取输入框样式"""
        return """
            QLineEdit {
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                padding: 0 15px;
                background: #f8f9fa;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background: white;
            }
        """

    def _center(self):
        """将窗口居中显示"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        self._drag_pos = None

    def _handle_login(self):
        """处理登录逻辑"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if username == "admin" and password == "123456":
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "账号或密码错误，请重新输入！")
            self.password_input.clear()
            self.password_input.setFocus()
