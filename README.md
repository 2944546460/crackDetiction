# 智桥卫士 (Bridge Guardian) 🌉

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-PyQt5-orange)](https://www.riverbankcomputing.com/software/pyqt/)
[![AI Model](https://img.shields.io/badge/AI-YOLOv11-red)](https://github.com/ultralytics/ultralytics)

**智桥卫士** 是一款集成了深度学习技术的现代化桥梁健康监测系统。它能够自动识别桥梁表面的裂缝损伤，并实时监测桥面的交通荷载情况，为桥梁的安全运维提供数据支撑。

---

## ✨ 核心功能

### 1. 🔍 智能裂缝检测
- **深度识别**：基于 YOLOv11 分割模型，精准识别桥梁裂缝。
- **像素标定**：支持交互式像素标定，将检测到的裂缝宽度从像素转换为毫米（mm）。
- **批量处理**：支持对整个文件夹内的图像进行自动化批量检测。
- **损伤评估**：根据裂缝宽度自动评估损伤等级。

### 2. 🚗 交通荷载监测
- **多源输入**：支持实时摄像头流和视频文件输入。
- **目标追踪**：采用 ByteTrack 算法对每一辆车进行唯一 ID 追踪。
- **流量统计**：基于越界线逻辑，精准统计累计交通流量（区分小车、卡车、大巴）。
- **实时测速**：基于目标位移自动计算车辆的行驶速度（km/h）。
- **拥堵分析**：实时计算车道占用率。

### 3. 📊 数据管理与报告
- **历史回溯**：完整的数据库支持，可查询过往的检测记录与交通数据。
- **专业报告**：一键生成包含检测结果、统计图表和处理意见的 PDF 报告。
- **可视化图表**：内置实时折线图，直观展示交通流量波动。

---

## 🛠️ 技术栈

- **GUI 框架**: PyQt5 (现代化的蓝色主题界面)
- **视觉处理**: OpenCV, Ultralytics YOLOv11
- **目标追踪**: ByteTrack
- **数据存储**: SQLite
- **绘图引擎**: Matplotlib (集成于 Qt 界面)
- **报告生成**: ReportLab
- **日志管理**: Python Logging (支持按天轮转)

---

## 🚀 快速开始

### 1. 环境准备
建议使用 Python 3.8 或以上版本。

```bash
# 克隆仓库 (如果有)
# git clone https://github.com/your-repo/bridge-guardian.git
# cd bridge-guardian

# 安装依赖
pip install ultralytics PyQt5 opencv-python matplotlib reportlab
```

### 2. 运行程序
```bash
python main.py
```

### 3. 默认凭据
- **用户名**: `admin`
- **密码**: `123456`

---

## 📂 项目结构

- `main.py`: 程序启动入口。
- `views/`: 包含所有界面代码（登录、仪表盘、检测、交通、报告等）。
- `models/`: YOLO 模型封装及视频处理逻辑。
- `threads/`: 耗时任务子线程（检测、导出、加载）。
- `utils/`: 通用工具（配置管理、数据库、日志、全局样式）。
- `icons/`: UI 资源文件。
- `logs/`: 系统运行日志。

---

## 📝 授权说明
本项目仅供学习与科研使用。
