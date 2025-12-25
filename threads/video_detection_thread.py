#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频检测线程

用于处理视频文件的裂缝检测任务，支持暂停、恢复和停止操作
"""

from threads.base_thread import BaseThread
from models.yolo_detection import YoloModel
from models.base_model import VideoProcessingModel
from utils.config_manager import ConfigManager
from utils.logger import logger
import cv2
import time
from datetime import datetime


class VideoDetectionThread(BaseThread):
    """视频检测线程类"""
    
    def __init__(self, video_path, model_path=None):
        """初始化视频检测线程
        
        Args:
            video_path: 视频文件路径
            model_path: YOLO模型文件路径
        """
        super().__init__()
        self._video_path = video_path
        self._model_path = model_path
        self._detection_model = None
        self._video_model = None
        self._frame_count = 0
        self._total_frames = 0
        self._counted_ids = set()  # 已计数的车辆 ID 集合
        self._total_vehicle_count = 0  # 累计流量
        self._crossing_line_y = None  # 越界线 Y 坐标 (画面中间)
        self._id_history = {}  # 记录 ID 的历史位置和时间: {id: (time, x, y)}
        self._current_speeds = {}  # 记录当前各 ID 的速度
    
    def _run(self):
        """执行视频检测任务"""
        try:
            # 初始化YOLO检测模型
            self._detection_model = YoloModel(self._model_path)
            self._detection_model.initialize()
            
            # 初始化视频处理模型
            self._video_model = VideoProcessingModel()
            self._video_model.initialize() # 调用初始化
            if not self._video_model.open_video(self._video_path):
                raise Exception(f"无法打开视频文件: {self._video_path}")
            
            self._total_frames = self._video_model.total_frames
            
            # 处理视频帧
            self._process_video_frames()
            
        finally:
            # 释放资源
            if self._detection_model:
                self._detection_model.release()
            if self._video_model:
                self._video_model.close_video()
    
    def _process_video_frames(self):
        """处理视频帧"""
        from utils.global_state import global_state
        
        # 获取视频的 FPS，如果没有则默认 30
        fps = self._video_model._fps if self._video_model._fps > 0 else 30
        frame_delay = 1.0 / fps # 计算每帧理论耗时
        
        frame_interval = 1  # 处理间隔
        processed_frames = 0
        start_time = time.time()
        
        while self._is_running:
            # 检查是否暂停
            self._wait_for_resume()
            
            # 获取下一帧
            frame = self._video_model.get_frame()
            if frame is None:
                break
            
            h, w = frame.shape[:2]
            if self._crossing_line_y is None:
                self._crossing_line_y = h // 2  # 默认在画面中间设置越界线
            
            self._frame_count += 1
            
            # 每隔指定间隔处理一帧
            if self._frame_count % frame_interval == 0:
                loop_start = time.time()  # 记录循环开始时间

                # 进行目标追踪
                processed_frame, result = self._detection_model.process_video_frame(frame, persist=True)
                
                # 流量统计逻辑
                detected_objects = result.get("detected_objects", [])
                current_car_count = 0
                current_truck_count = 0
                current_bus_count = 0
                
                now = time.time()
                active_ids = set()
                pixel_to_meter = 0.05  # 像素到米的换算系数 (估算值，实际需标定)
                
                for obj in detected_objects:
                    obj_id = obj["id"]
                    obj_cls = obj.get("class", -1)
                    center_x, center_y = obj["center"]
                    active_ids.add(obj_id)
                    
                    # 统计当前帧各车型数量
                    if obj_cls == 2: # car
                        current_car_count += 1
                    elif obj_cls == 7: # truck
                        current_truck_count += 1
                    elif obj_cls == 5: # bus
                        current_bus_count += 1
                    
                    # 计算速度逻辑
                    if obj_id in self._id_history:
                        prev_time, prev_x, prev_y = self._id_history[obj_id]
                        time_diff = now - prev_time
                        
                        if time_diff > 0:
                            # 计算像素位移
                            dist_px = ((center_x - prev_x)**2 + (center_y - prev_y)**2)**0.5
                            # 转换为米
                            dist_m = dist_px * pixel_to_meter
                            # 计算速度 (km/h)
                            speed_kmh = (dist_m / time_diff) * 3.6
                            
                            # 平滑处理：简单的加权平均
                            if obj_id in self._current_speeds:
                                self._current_speeds[obj_id] = self._current_speeds[obj_id] * 0.7 + speed_kmh * 0.3
                            else:
                                self._current_speeds[obj_id] = speed_kmh
                    
                    # 更新历史位置
                    self._id_history[obj_id] = (now, center_x, center_y)
                    
                    # 2. 进阶：越界线判定 (中心点穿过中间线才计数)
                    if obj_id not in self._counted_ids:
                        # 如果车辆中心点超过了越界线（向下行驶）
                        if center_y > self._crossing_line_y:
                            self._counted_ids.add(obj_id)
                            self._total_vehicle_count += 1
                
                # 清理过期 ID
                expired_ids = [tid for tid in self._id_history if tid not in active_ids]
                for tid in expired_ids:
                    del self._id_history[tid]
                    if tid in self._current_speeds:
                        del self._current_speeds[tid]
                
                # 计算当前平均车速
                avg_speed = 0
                if self._current_speeds:
                    avg_speed = sum(self._current_speeds.values()) / len(self._current_speeds)
                
                # 更新全局状态
                global_state.update_traffic_stats(
                    total=self._total_vehicle_count,
                    truck=current_truck_count, # 传递当前帧的统计
                    car=current_car_count,
                    bus=current_bus_count
                )
                
                # 在画面上绘制越界线和统计信息
                cv2.line(processed_frame, (0, self._crossing_line_y), (w, self._crossing_line_y), (0, 255, 255), 2)
                cv2.putText(processed_frame, f"Total Flow: {self._total_vehicle_count}", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(processed_frame, f"Current: {len(detected_objects)} | Avg Speed: {avg_speed:.1f} km/h", (20, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                # 兼容旧的结果格式，添加统计数据供 UI 显示
                result["stats"] = {
                    "total_vehicles": self._total_vehicle_count,
                    "current_frame_vehicles": len(detected_objects),
                    "car": current_car_count,
                    "truck": current_truck_count,
                    "bus": current_bus_count,
                    "avg_speed": avg_speed
                }
                
                # 发送处理结果信号
                self.frame_processed_signal.emit(processed_frame, result)
                
                # 控制播放速度：根据 FPS 进行补偿，防止播放过快
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                processed_frames += 1
                
                # 更新进度
                progress = int((self._frame_count / self._total_frames) * 100)
                self._update_progress(progress)
                
                # 计算并显示FPS
                if processed_frames % 10 == 0:
                    elapsed_time = time.time() - start_time
                    fps = processed_frames / elapsed_time if elapsed_time > 0 else 0
                    logger.debug(f"视频检测FPS: {fps:.2f}")
        
        # 视频处理完成，发送最终结果
        final_result = {
            "video_path": self._video_path,
            "total_frames": self._total_frames,
            "processed_frames": processed_frames,
            "processing_time": time.time() - start_time
        }
        self.result_signal.emit(final_result)


class ImageDetectionThread(BaseThread):
    """图像检测线程类，用于处理单张图像的裂缝检测"""
    
    def __init__(self, image_path, model_path=None):
        """初始化图像检测线程
        
        Args:
            image_path: 图像文件路径或numpy数组
            model_path: YOLO模型文件路径
        """
        super().__init__()
        self.config_manager = ConfigManager()
        self._image_path = image_path
        
        if model_path is None:
            model_path = self.config_manager.get("Detection", "model_path")
            
        self._model_path = model_path
        self._detection_model = None
    
    def _run(self):
        """执行图像检测任务"""
        try:
            # 初始化YOLO检测模型
            self._detection_model = YoloModel(self._model_path)
            self._detection_model.initialize()
            
            # 处理图像
            processed_image, result = self._detection_model.process_image(self._image_path)
            
            # 发送处理结果信号
            final_result = {
                "original_image": self._image_path,
                "processed_image": processed_image,
                "detection_result": result
            }
            self.result_signal.emit(final_result)
            
        finally:
            # 释放资源
            if self._detection_model:
                self._detection_model.release()


class CrackAnalysisThread(BaseThread):
    """裂缝分析线程类，用于对检测结果进行进一步分析"""
    
    def __init__(self, detection_result):
        """初始化裂缝分析线程
        
        Args:
            detection_result: 裂缝检测结果
        """
        super().__init__()
        self._detection_result = detection_result
    
    def _run(self):
        """执行裂缝分析任务"""
        from models.yolo_detection import CrackAnalysisModel
        
        try:
            # 初始化裂缝分析模型
            analysis_model = CrackAnalysisModel()
            analysis_model.initialize()
            
            # 进行裂缝分析
            analysis_result = analysis_model.analyze_cracks(self._detection_result)
            
            # 发送分析结果信号
            final_result = {
                "detection_result": self._detection_result,
                "analysis_result": analysis_result
            }
            self.result_signal.emit(final_result)
            
        finally:
            # 释放资源
            if 'analysis_model' in locals():
                analysis_model.release()


class BatchDetectionThread(BaseThread):
    """批量图像检测线程"""
    
    def __init__(self, image_paths):
        """初始化批量检测线程
        
        Args:
            image_paths: 图像文件路径列表
        """
        super().__init__()
        self.image_paths = image_paths
        self.config_manager = ConfigManager()
        self.model_path = self.config_manager.get("Detection", "model_path")
        self.detection_model = None

    def _run(self):
        """执行批量检测任务"""
        try:
            from models.yolo_detection import YoloModel
            from utils.db_manager import DBManager
            from utils.global_state import global_state
            import cv2
            import os
            
            # 初始化模型
            self.detection_model = YoloModel(self.model_path)
            self.detection_model.initialize()
            
            db = DBManager()
            total = len(self.image_paths)
            results = []
            
            output_dir = self.config_manager.get("System", "save_dir") or "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            for i, img_path in enumerate(self.image_paths):
                if not self._is_running:
                    break
                
                # 处理单张图片
                image = cv2.imread(img_path)
                if image is None:
                    continue
                    
                processed_image, result = self.detection_model.process_image(image)
                
                # 保存处理后的图片
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(output_dir, f"batch_{timestamp}_{i}.jpg")
                cv2.imwrite(save_path, processed_image)
                
                # 写入数据库
                stats = result.get("stats", {})
                total_cracks = stats.get("total_cracks", 0)
                max_width_mm = stats.get("max_width_mm", 0)
                
                db.add_crack_record(
                    project_id=global_state.get_current_project_id() or 1,
                    score=result.get("score", 0),
                    image_path=save_path,
                    width=max_width_mm,
                    count=total_cracks
                )
                
                results.append({
                    "path": img_path,
                    "cracks": total_cracks,
                    "max_width": max_width_mm
                })
                
                # 更新进度
                progress = int(((i + 1) / total) * 100)
                self._update_progress(progress)
                
            self.result_signal.emit({"success": True, "total": total, "processed": len(results)})
            
        except Exception as e:
            logger.exception("批量处理失败")
            self.result_signal.emit({"success": False, "error": str(e)})
        finally:
            if self.detection_model:
                self.detection_model.release()
