"""
决策日志记录器 - Decision Logger Module

负责记录智能决策系统中的各类决策数据：
- 工具调用记录
- 重规划记录
- 耗时统计
- 决策记录数据类

使用 SQLite 数据库存储，支持实时写入和自动建表。
"""

import sqlite3
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager


# ==================== 数据类定义 ====================

@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

    def finish(self, result: Any = None, error: Optional[str] = None):
        """结束工具调用"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        if error:
            self.success = False
            self.error = error
        if result is not None:
            self.result = result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "result": str(self.result)[:1000] if self.result else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "error": self.error
        }


@dataclass
class DecisionRecord:
    """决策记录数据类"""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[ToolCall] = field(default_factory=list)
    replan_count: int = 0
    duration: float = 0.0
    effect_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    # 额外扩展字段
    decision_type: str = ""  # 决策类型
    model_name: str = ""    # 使用的模型
    session_id: str = ""    # 会话ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "input_data": json.dumps(self.input_data, ensure_ascii=False),
            "output_data": json.dumps(self.output_data, ensure_ascii=False),
            "tool_calls": json.dumps([tc.to_dict() for tc in self.tool_calls], ensure_ascii=False),
            "replan_count": self.replan_count,
            "duration": self.duration,
            "effect_score": self.effect_score,
            "tags": json.dumps(self.tags, ensure_ascii=False),
            "decision_type": self.decision_type,
            "model_name": self.model_name,
            "session_id": self.session_id
        }


# ==================== 数据库管理 ====================

class DecisionDatabase:
    """决策数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认使用模块目录下的数据库
            base_dir = Path(__file__).parent
            db_path = base_dir / "decisions.db"
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库和表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 决策记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    tool_calls TEXT,
                    replan_count INTEGER DEFAULT 0,
                    duration REAL DEFAULT 0.0,
                    effect_score REAL DEFAULT 0.0,
                    tags TEXT,
                    decision_type TEXT DEFAULT '',
                    model_name TEXT DEFAULT '',
                    session_id TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 工具调用详细记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    arguments TEXT,
                    result TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    success INTEGER DEFAULT 1,
                    error TEXT,
                    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
                )
            """)
            
            # 重规划记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS replans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id TEXT NOT NULL,
                    replan_index INTEGER NOT NULL,
                    reason TEXT,
                    timestamp REAL NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
                )
            """)
            
            # 耗时统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duration_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    duration REAL,
                    FOREIGN KEY (decision_id) REFERENCES decisions(decision_id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_session ON decisions(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_calls_decision ON tool_calls(decision_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_replans_decision ON replans(decision_id)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def insert_decision(self, record: DecisionRecord) -> bool:
        """插入决策记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                data = record.to_dict()
                cursor.execute("""
                    INSERT INTO decisions (
                        decision_id, timestamp, input_data, output_data, tool_calls,
                        replan_count, duration, effect_score, tags,
                        decision_type, model_name, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["decision_id"], data["timestamp"], data["input_data"],
                    data["output_data"], data["tool_calls"], data["replan_count"],
                    data["duration"], data["effect_score"], data["tags"],
                    data["decision_type"], data["model_name"], data["session_id"]
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"插入决策记录失败: {e}")
            return False
    
    def update_decision(self, decision_id: str, **kwargs) -> bool:
        """更新决策记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                set_clauses = []
                values = []
                for key, value in kwargs.items():
                    if key == "tags":
                        value = json.dumps(value, ensure_ascii=False)
                    elif key in ("input_data", "output_data"):
                        value = json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                values.append(decision_id)
                cursor.execute(
                    f"UPDATE decisions SET {', '.join(set_clauses)} WHERE decision_id = ?",
                    values
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"更新决策记录失败: {e}")
            return False
    
    def get_decision(self, decision_id: str) -> Optional[Dict]:
        """获取单条决策记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"获取决策记录失败: {e}")
            return None
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """获取最近的决策记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取最近决策记录失败: {e}")
            return []


# ==================== 工具调用记录器 ====================

class ToolCallLogger:
    """工具调用记录器"""
    
    def __init__(self, decision_id: str, db: DecisionDatabase = None):
        self.decision_id = decision_id
        self.db = db or DecisionDatabase()
        self._current_call: Optional[ToolCall] = None
    
    def start_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolCall:
        """开始记录工具调用"""
        self._current_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            start_time=time.time()
        )
        return self._current_call
    
    def end_call(self, result: Any = None, error: Optional[str] = None):
        """结束工具调用并保存"""
        if self._current_call:
            self._current_call.finish(result=result, error=error)
            self._save_call()
            self._current_call = None
    
    def _save_call(self):
        """保存工具调用到数据库"""
        if self._current_call:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    tc = self._current_call
                    cursor.execute("""
                        INSERT INTO tool_calls (
                            decision_id, tool_name, arguments, result,
                            start_time, end_time, duration, success, error
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.decision_id, tc.tool_name,
                        json.dumps(tc.arguments, ensure_ascii=False),
                        str(tc.result)[:1000] if tc.result else None,
                        tc.start_time, tc.end_time, tc.duration,
                        1 if tc.success else 0, tc.error
                    ))
                    conn.commit()
            except Exception as e:
                print(f"保存工具调用失败: {e}")
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def __call__(self, tool_name: str, arguments: Dict[str, Any]):
        """作为装饰器使用"""
        return self.start_call(tool_name, arguments)


# ==================== 重规划记录器 ====================

class ReplanRecorder:
    """重规划记录器"""
    
    def __init__(self, decision_id: str, db: DecisionDatabase = None):
        self.decision_id = decision_id
        self.db = db or DecisionDatabase()
        self.replan_count = 0
    
    def record(self, reason: str, input_data: Dict = None, output_data: Dict = None):
        """记录一次重规划"""
        self.replan_count += 1
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO replans (
                        decision_id, replan_index, reason, timestamp, input_data, output_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.decision_id,
                    self.replan_count,
                    reason,
                    time.time(),
                    json.dumps(input_data, ensure_ascii=False) if input_data else None,
                    json.dumps(output_data, ensure_ascii=False) if output_data else None
                ))
                conn.commit()
        except Exception as e:
            print(f"记录重规划失败: {e}")
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db.db_path)
        try:
            yield conn
        finally:
            conn.close()


# ==================== 耗时统计器 ====================

class DurationTracker:
    """耗时统计器"""
    
    def __init__(self, decision_id: str, db: DecisionDatabase = None):
        self.decision_id = decision_id
        self.db = db or DecisionDatabase()
        self._phases: Dict[str, float] = {}
    
    def start_phase(self, phase: str):
        """开始一个阶段"""
        self._phases[phase] = time.time()
    
    def end_phase(self, phase: str) -> Optional[float]:
        """结束一个阶段并记录耗时"""
        if phase in self._phases:
            start_time = self._phases.pop(phase)
            duration = time.time() - start_time
            self._save_duration(phase, start_time, time.time(), duration)
            return duration
        return None
    
    def _save_duration(self, phase: str, start_time: float, end_time: float, duration: float):
        """保存耗时记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO duration_stats (decision_id, phase, start_time, end_time, duration)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.decision_id, phase, start_time, end_time, duration))
                conn.commit()
        except Exception as e:
            print(f"保存耗时统计失败: {e}")
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理未结束的阶段
        for phase, start_time in self._phases.items():
            duration = time.time() - start_time
            self._save_duration(phase, start_time, time.time(), duration)


# ==================== 主决策记录器 ====================

class DecisionLogger:
    """综合决策日志记录器"""
    
    def __init__(self, db_path: str = None):
        self.db = DecisionDatabase(db_path)
        self._current_record: Optional[DecisionRecord] = None
        self._tool_logger: Optional[ToolCallLogger] = None
        self._replan_recorder: Optional[ReplanRecorder] = None
        self._duration_tracker: Optional[DurationTracker] = None
    
    def start_decision(
        self,
        input_data: Dict[str, Any],
        decision_type: str = "",
        model_name: str = "",
        session_id: str = "",
        tags: List[str] = None
    ) -> str:
        """开始一个新的决策记录"""
        self._current_record = DecisionRecord(
            input_data=input_data,
            decision_type=decision_type,
            model_name=model_name,
            session_id=session_id,
            tags=tags or []
        )
        
        # 初始化子记录器
        self._tool_logger = ToolCallLogger(self._current_record.decision_id, self.db)
        self._replan_recorder = ReplanRecorder(self._current_record.decision_id, self.db)
        self._duration_tracker = DurationTracker(self._current_record.decision_id, self.db)
        
        return self._current_record.decision_id
    
    def end_decision(self, output_data: Dict[str, Any] = None, effect_score: float = 0.0):
        """结束当前决策记录"""
        if self._current_record:
            self._current_record.output_data = output_data or {}
            self._current_record.effect_score = effect_score
            self._current_record.replan_count = self._replan_recorder.replan_count if self._replan_recorder else 0
            
            # 计算总耗时
            if self._current_record.timestamp:
                self._current_record.duration = time.time() - self._current_record.timestamp
            
            # 保存记录
            self.db.insert_decision(self._current_record)
            
            result = self._current_record
            self._current_record = None
            self._tool_logger = None
            self._replan_recorder = None
            self._duration_tracker = None
            return result
        return None
    
    @property
    def tool_logger(self) -> Optional[ToolCallLogger]:
        return self._tool_logger
    
    @property
    def replan_recorder(self) -> Optional[ReplanRecorder]:
        return self._replan_recorder
    
    @property
    def duration_tracker(self) -> Optional[DurationTracker]:
        return self._duration_tracker
    
    @property
    def current_decision_id(self) -> Optional[str]:
        return self._current_record.decision_id if self._current_record else None


# ==================== 便捷函数 ====================

def create_logger(db_path: str = None) -> DecisionLogger:
    """创建决策日志记录器"""
    return DecisionLogger(db_path)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试代码
    print("=== 决策日志记录器测试 ===")
    
    logger = create_logger()
    
    # 开始决策
    decision_id = logger.start_decision(
        input_data={"query": "测试查询", "context": {}},
        decision_type="test",
        model_name="gpt-4",
        session_id="test-session-001",
        tags=["test", "demo"]
    )
    print(f"开始决策: {decision_id}")
    
    # 记录工具调用
    with logger.duration_tracker:
        logger.duration_tracker.start_phase("thinking")
        tool_call = logger.tool_logger.start_call("web_search", {"query": "test"})
        # 模拟工具执行
        time.sleep(0.1)
        tool_call.finish(result="search results")
        logger.tool_logger.end_call()
        logger.duration_tracker.end_phase("thinking")
    
    # 记录重规划
    logger.replan_recorder.record("初始结果不够好", {"query": "test"}, {"result": "improved"})
    
    # 结束决策
    record = logger.end_decision(
        output_data={"answer": "测试答案"},
        effect_score=0.85
    )
    print(f"决策完成: {record.decision_id}, 效果分: {record.effect_score}")
    
    # 查询最近决策
    recent = logger.db.get_recent_decisions(5)
    print(f"最近决策数量: {len(recent)}")
    
    print("=== 测试完成 ===")
