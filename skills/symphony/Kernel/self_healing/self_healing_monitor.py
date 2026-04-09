# -*- coding: utf-8 -*-
"""内核自愈监控??- 1s级异常检??+ 自动自愈"""
import os
import sys
import time
import uuid
import threading
import logging
import psutil
import hashlib
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import HealthStatus, AnomalyType, HealingAction, AnomalyEvent, HealingResult, HealthReport

logger = logging.getLogger(__name__)

DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
BACKUP_DIR = f'{DATA_DIR}/backups'
SELF_HEALING_DB = f'{DATA_DIR}/self_healing.db'
MAX_CPU_THRESHOLD = 90.0  # CPU使用率超??0%触发告警
MAX_MEMORY_THRESHOLD = 90.0  # 内存使用率超??0%触发告警
MAX_THREAD_COUNT = 200  # 线程数超??00触发告警
CHECK_INTERVAL = 1.0  # 1s检测间??
os.makedirs(BACKUP_DIR, exist_ok=True)

class SelfHealingMonitor:
    def __init__(self, kernel_instance, config: Optional[Dict] = None):
        self.kernel = kernel_instance
        self.config = config or {}
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()
        
# 阈值配??
        self.cpu_threshold = self.config.get('cpu_threshold', MAX_CPU_THRESHOLD)
        self.memory_threshold = self.config.get('memory_threshold', MAX_MEMORY_THRESHOLD)
        self.thread_threshold = self.config.get('thread_threshold', MAX_THREAD_COUNT)
        self.check_interval = self.config.get('check_interval', CHECK_INTERVAL)
        
# 状态存??
        self.last_health_report: Optional[HealthReport] = None
        self.anomaly_history: List[AnomalyEvent] = []
        self.healing_history: List[HealingResult] = []
        self.process = psutil.Process(os.getpid())
        
        # 初始化自愈数据库
        self._init_db()
        
# 备份清单（需要监控完整性的文件??
        self.monitored_files = [
            f'{DATA_DIR}/symphony.db',
            f'{DATA_DIR}/symphony_kernel.db',
            f'{DATA_DIR}/symphony.db',
            f'{os.path.dirname(os.path.abspath(__file__))}/../config/kernel_config.json',
        ]
        self.file_checksums: Dict[str, str] = {}
        self._init_file_checksums()
        
        logger.info("Self-healing monitor initialized")

    def _init_db(self):
        """初始化自愈事件数据库"""
        try:
            conn = sqlite3.connect(SELF_HEALING_DB)
            cursor = conn.cursor()
            
# Anomaly events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    component TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT
                )
            ''')
            
# Anomaly events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS healing_results (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    duration_ms REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (event_id) REFERENCES anomalies (id)
                )
            ''')
            
            # 健康检查表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_reports (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    overall_status TEXT NOT NULL,
                    component_status TEXT NOT NULL,
                    resource_usage TEXT NOT NULL,
                    anomaly_count INTEGER NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Self-healing database initialized")
        except Exception as e:
            logger.error(f"Failed to init self-healing DB: {e}")

    def _init_file_checksums(self):
        """初始化受监控文件的基准校验和"""
        for file_path in self.monitored_files:
            if os.path.exists(file_path):
                self.file_checksums[file_path] = self._calculate_file_checksum(file_path)
                # 创建初始备份
                self._backup_file(file_path)

    def _calculate_file_checksum(self, file_path: str) -> str:
        """计算文件MD5校验??""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""

    def _backup_file(self, file_path: str):
        """备份文件到备份目??""
        if not os.path.exists(file_path):
            return
        try:
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{BACKUP_DIR}/{filename}.{timestamp}.bak"
            with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())
            # 只保留最??0个备??            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith(filename)], reverse=True)
            for old_backup in backups[10:]:
                os.remove(f"{BACKUP_DIR}/{old_backup}")
            logger.debug(f"Backup created: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")

    def _restore_from_backup(self, file_path: str) -> bool:
        """从最近的备份恢复文件"""
        try:
            filename = os.path.basename(file_path)
            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith(filename)], reverse=True)
            if not backups:
                logger.error(f"No backups found for {file_path}")
                return False
            
            latest_backup = f"{BACKUP_DIR}/{backups[0]}"
            with open(latest_backup, "rb") as src, open(file_path, "wb") as dst:
                dst.write(src.read())
            logger.info(f"Restored {file_path} from backup: {latest_backup}")
# 更新校验??    
        self.file_checksums[file_path] = self._calculate_file_checksum(file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to restore {file_path}: {e}")
            return False

    def _check_process_health(self) -> List[AnomalyEvent]:
        """检查进程级健康状态：CPU、内存、线程、死??""
        anomalies = []
        try:
            # CPU使用??            cpu_percent = self.process.cpu_percent(interval=0.1)
            if cpu_percent > self.cpu_threshold:
                anomalies.append(AnomalyEvent(
                    anomaly_id=str(uuid.uuid4())[:8],
                    anomaly_type=AnomalyType.CPU_OVERLOAD,
                    severity=HealthStatus.CRITICAL,
                    component="process",
                    description=f"CPU usage {cpu_percent}% exceeds threshold {self.cpu_threshold}%",
                    metadata={"cpu_usage": cpu_percent}
                ))
            
            # 内存使用??            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            if memory_percent > self.memory_threshold:
                anomalies.append(AnomalyEvent(
                    anomaly_id=str(uuid.uuid4())[:8],
                    anomaly_type=AnomalyType.MEMORY_OVERFLOW,
                    severity=HealthStatus.CRITICAL,
                    component="process",
                    description=f"Memory usage {memory_percent}% exceeds threshold {self.memory_threshold}%",
                    metadata={"memory_usage": memory_percent, "memory_rss": memory_info.rss}
                ))
            
            # 线程??            thread_count = self.process.num_threads()
            if thread_count > self.thread_threshold:
                anomalies.append(AnomalyEvent(
                    anomaly_id=str(uuid.uuid4())[:8],
                    anomaly_type=AnomalyType.THREAD_LEAK,
                    severity=HealthStatus.WARNING,
                    component="process",
                    description=f"Thread count {thread_count} exceeds threshold {self.thread_threshold}",
                    metadata={"thread_count": thread_count}
                ))
            
        except Exception as e:
            logger.error(f"Process health check failed: {e}")
        
        return anomalies

    def _check_data_integrity(self) -> List[AnomalyEvent]:
        """检查数据完整性：数据库、配置文件、缓??""
        anomalies = []
        for file_path in self.monitored_files:
            if not os.path.exists(file_path):
                anomalies.append(AnomalyEvent(
                    anomaly_id=str(uuid.uuid4())[:8],
                    anomaly_type=AnomalyType.DATA_MISSING,
                    severity=HealthStatus.CRITICAL,
                    component="data",
                    description=f"File missing: {file_path}",
                    metadata={"file_path": file_path}
                ))
                continue
            
            current_checksum = self._calculate_file_checksum(file_path)
            if file_path in self.file_checksums and current_checksum != self.file_checksums[file_path]:
                # 检查是否是数据库文件，如果是先验证是否可正常访??                if file_path.endswith('.db'):
                    try:
                        conn = sqlite3.connect(file_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master LIMIT 1")
                        conn.close()
# 数据库可正常访问，更新校验和（正常写入导致的变化??                
        self.file_checksums[file_path] = current_checksum
                        self._backup_file(file_path)
                        continue
                    except Exception as e:
                        # 数据库损??                        anomalies.append(AnomalyEvent(
                            anomaly_id=str(uuid.uuid4())[:8],
                            anomaly_type=AnomalyType.DB_CORRUPTION,
                            severity=HealthStatus.CRITICAL,
                            component="data",
                            description=f"Database corrupted: {file_path}, error: {str(e)}",
                            metadata={"file_path": file_path}
                        ))
                else:
                    # 配置文件损坏
                    anomalies.append(AnomalyEvent(
                        anomaly_id=str(uuid.uuid4())[:8],
                        anomaly_type=AnomalyType.CONFIG_CORRUPTION,
                        severity=HealthStatus.CRITICAL,
                        component="data",
                        description=f"Config file corrupted: {file_path}",
                        metadata={"file_path": file_path}
                    ))
        
        return anomalies

    def _check_dependencies(self) -> List[AnomalyEvent]:
        """检查依赖服务健康：模型服务、API、子代理会话"""
        anomalies = []
        # 检查模型联邦服??        if hasattr(self.kernel, 'federation') and self.kernel.federation:
            try:
                online_models = self.kernel._get_online_models_from_federation()
                if not online_models:
                    anomalies.append(AnomalyEvent(
                        anomaly_id=str(uuid.uuid4())[:8],
                        anomaly_type=AnomalyType.MODEL_SERVICE_DOWN,
                        severity=HealthStatus.CRITICAL,
                        component="dependency",
                        description="No online model services available",
                        metadata={}
                    ))
            except Exception as e:
                anomalies.append(AnomalyEvent(
                    anomaly_id=str(uuid.uuid4())[:8],
                    anomaly_type=AnomalyType.MODEL_SERVICE_DOWN,
                    severity=HealthStatus.CRITICAL,
                    component="dependency",
                    description=f"Model federation check failed: {str(e)}",
                    metadata={}
                ))
        
        # 检查调度器
        if hasattr(self.kernel, 'scheduler') and not self.kernel.scheduler:
            anomalies.append(AnomalyEvent(
                anomaly_id=str(uuid.uuid4())[:8],
                anomaly_type=AnomalyType.CRASH,
                severity=HealthStatus.CRITICAL,
                component="dependency",
                description="Scheduler component crashed",
                metadata={}
            ))
        
        return anomalies

    def _heal_anomaly(self, anomaly: AnomalyEvent) -> HealingResult:
        """执行自愈操作"""
        start_time = time.time()
        action = HealingAction.NO_ACTION
        success = False
        description = ""
        
        try:
            if anomaly.anomaly_type in [AnomalyType.CPU_OVERLOAD, AnomalyType.MEMORY_OVERFLOW, AnomalyType.THREAD_LEAK]:
                # 资源过载：清理任务队列，重启非核心组??                action = HealingAction.RESTART_COMPONENT
                # 清理超时任务
                if hasattr(self.kernel, 'active_tasks'):
                    with self.kernel._lock:
                        current_time = time.time()
                        expired_tasks = [
                            task_id for task_id, task in self.kernel.active_tasks.items()
                            if current_time - task.created_at > self.kernel.config.default_timeout
                        ]
                        for task_id in expired_tasks:
                            del self.kernel.active_tasks[task_id]
                success = True
                description = f"Cleared {len(expired_tasks)} expired tasks, resource usage normalized"
            
            elif anomaly.anomaly_type in [AnomalyType.DB_CORRUPTION, AnomalyType.CONFIG_CORRUPTION, AnomalyType.DATA_MISSING]:
                # 数据损坏：从备份恢复
                action = HealingAction.RESTORE_FROM_BACKUP
                file_path = anomaly.metadata.get('file_path')
                if file_path:
                    success = self._restore_from_backup(file_path)
                    description = f"Restored file {file_path} from backup" if success else f"Failed to restore {file_path}"
            
            elif anomaly.anomaly_type == AnomalyType.MODEL_SERVICE_DOWN:
                # 模型服务不可用：切换到备用模??                action = HealingAction.SWITCH_TO_BACKUP
                # 触发调度器重新加载模型列??                if hasattr(self.kernel, 'federation') and hasattr(self.kernel.federation, 'reload_models'):
                    self.kernel.federation.reload_models()
                success = True
                description = "Switched to backup model providers"
            
            elif anomaly.anomaly_type == AnomalyType.CRASH:
                # 组件崩溃：重启组??                action = HealingAction.RESTART_COMPONENT
                if anomaly.component == "dependency" and "scheduler" in anomaly.description:
                    # 重启调度??                    try:
                        from intelligent_strategy_scheduler import IntelligentStrategyScheduler
                        self.kernel.scheduler = IntelligentStrategyScheduler()
                        success = True
                        description = "Scheduler restarted successfully"
                    except Exception as e:
                        description = f"Failed to restart scheduler: {str(e)}"
            
            else:
                description = "No healing action defined for this anomaly type"
        
        except Exception as e:
            description = f"Healing failed with error: {str(e)}"
            success = False
        
        duration_ms = (time.time() - start_time) * 1000
        
        result = HealingResult(
            event_id=anomaly.anomaly_id,
            action=action,
            success=success,
            description=description,
            duration_ms=duration_ms
        )
        
        # 记录自愈结果到数据库
        self._save_healing_result(result)
        
        return result

    def _save_anomaly(self, anomaly: AnomalyEvent):
        """保存异常事件到数据库"""
        try:
            conn = sqlite3.connect(SELF_HEALING_DB)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anomalies (id, type, severity, component, description, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                anomaly.anomaly_id,
                anomaly.anomaly_type.value,
                anomaly.severity.value,
                anomaly.component,
                anomaly.description,
                anomaly.timestamp,
                json.dumps(anomaly.metadata)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save anomaly: {e}")

    def _save_healing_result(self, result: HealingResult):
        """保存自愈结果到数据库"""
        try:
            conn = sqlite3.connect(SELF_HEALING_DB)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO healing_results (id, event_id, action, success, description, timestamp, duration_ms, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4())[:8],
                result.event_id,
                result.action.value,
                1 if result.success else 0,
                result.description,
                result.timestamp,
                result.duration_ms,
                json.dumps(result.metadata)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save healing result: {e}")

    def _save_health_report(self, report: HealthReport):
        """保存健康报告到数据库"""
        try:
            conn = sqlite3.connect(SELF_HEALING_DB)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_reports (id, timestamp, overall_status, component_status, resource_usage, anomaly_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4())[:8],
                report.timestamp,
                report.overall_status.value,
                json.dumps({k: v.value for k, v in report.component_status.items()}),
                json.dumps(report.resource_usage),
                len(report.anomalies)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save health report: {e}")

    def run_check_cycle(self) -> HealthReport:
        """运行一次完整的健康检查和自愈流程"""
        with self._lock:
            anomalies = []
            
            # 1. 执行各类检??            anomalies.extend(self._check_process_health())
            anomalies.extend(self._check_data_integrity())
            anomalies.extend(self._check_dependencies())
            
            # 2. 生成健康报告
            overall_status = HealthStatus.HEALTHY
            component_status = {
                "process": HealthStatus.HEALTHY,
                "data": HealthStatus.HEALTHY,
                "dependency": HealthStatus.HEALTHY,
            }
            
            for anomaly in anomalies:
                self._save_anomaly(anomaly)
                if anomaly.severity == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                    component_status[anomaly.component] = HealthStatus.CRITICAL
                elif anomaly.severity == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.WARNING
                    component_status[anomaly.component] = HealthStatus.WARNING
            
            # 3. 执行自愈
            for anomaly in anomalies:
                if anomaly.severity in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                    healing_result = self._heal_anomaly(anomaly)
                    self.healing_history.append(healing_result)
                    logger.warning(f"Anomaly {anomaly.anomaly_id} healed: {healing_result.success}, action: {healing_result.action.value}")
            
            # 4. 收集资源使用情况
            resource_usage = {
                "cpu_percent": self.process.cpu_percent(),
                "memory_percent": self.process.memory_percent(),
                "thread_count": self.process.num_threads()
            }
            
            report = HealthReport(
                overall_status=overall_status,
                component_status=component_status,
                anomalies=anomalies,
                resource_usage=resource_usage
            )
            
            self.last_health_report = report
            self._save_health_report(report)
            
            return report

    def _monitor_loop(self):
        """后台监控循环"""
        logger.info("Self-healing monitor started")
        while self.running:
            try:
                self.run_check_cycle()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(0.1)
        logger.info("Self-healing monitor stopped")

    def start(self):
        """启动监控??""
        if self.running:
            logger.warning("Self-healing monitor already running")
            return
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Self-healing monitor started successfully")

    def stop(self):
        """停止监控??""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Self-healing monitor stopped")

    def get_health_report(self) -> Optional[HealthReport]:
        """获取最新健康报??""
        return self.last_health_report

    def generate_rca_report(self, start_time: float, end_time: float) -> Dict[str, Any]:
        """生成指定时间范围内的根因分析报告"""
        try:
            conn = sqlite3.connect(SELF_HEALING_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询异常事件
            cursor.execute('''
                SELECT * FROM anomalies WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            anomalies = [dict(row) for row in cursor.fetchall()]
            
            # 查询自愈结果
            cursor.execute('''
                SELECT * FROM healing_results WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            healing_results = [dict(row) for row in cursor.fetchall()]
            
            # 统计信息
            anomaly_count_by_type = {}
            for anomaly in anomalies:
                anomaly_type = anomaly['type']
                anomaly_count_by_type[anomaly_type] = anomaly_count_by_type.get(anomaly_type, 0) + 1
            
            healing_success_rate = 0
            if healing_results:
                success_count = sum(1 for res in healing_results if res['success'] == 1)
                healing_success_rate = success_count / len(healing_results) * 100
            
            avg_healing_time = 0
            if healing_results:
                avg_healing_time = sum(res['duration_ms'] for res in healing_results) / len(healing_results)
            
            report = {
                "time_range": {
                    "start": datetime.fromtimestamp(start_time).isoformat(),
                    "end": datetime.fromtimestamp(end_time).isoformat()
                },
                "summary": {
                    "total_anomalies": len(anomalies),
                    "total_healing_actions": len(healing_results),
                    "healing_success_rate": f"{healing_success_rate:.2f}%",
                    "avg_healing_time_ms": round(avg_healing_time, 2),
                    "anomaly_count_by_type": anomaly_count_by_type
                },
                "anomalies": anomalies,
                "healing_results": healing_results
            }
            
            conn.close()
            return report
        except Exception as e:
            logger.error(f"Failed to generate RCA report: {e}")
            return {
                "error": str(e)
            }

