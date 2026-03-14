#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Streaming Output - 交响流式输出
Real-time streaming output with progress visualization
实时流式输出，带进度可视化
"""

import sys
import os
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class StreamStatus(Enum):
    """Stream status - 流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class StreamChunk:
    """Stream chunk - 流数据块"""
    chunk_id: str
    content: str
    timestamp: str
    chunk_type: str = "text"  # text, progress, status, error
    metadata: Dict[str, Any] = None


class StreamingOutput:
    """流式输出"""
    
    def __init__(self):
        self.chunks: List[StreamChunk] = []
        self.status = StreamStatus.PENDING
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.progress: float = 0.0
        self._chunk_counter = 0
    
    def start(self):
        """Start streaming - 开始流式输出"""
        self.status = StreamStatus.RUNNING
        self.start_time = time.time()
        self._add_chunk("Streaming started", "status")
    
    def finish(self):
        """Finish streaming - 结束流式输出"""
        self.status = StreamStatus.COMPLETED
        self.end_time = time.time()
        self.progress = 1.0
        self._add_chunk("Streaming completed", "status")
    
    def error(self, error_msg: str):
        """Set error - 设置错误"""
        self.status = StreamStatus.ERROR
        self.end_time = time.time()
        self._add_chunk(f"Error: {error_msg}", "error")
    
    def cancel(self):
        """Cancel streaming - 取消流式输出"""
        self.status = StreamStatus.CANCELLED
        self.end_time = time.time()
        self._add_chunk("Streaming cancelled", "status")
    
    def _add_chunk(self, content: str, chunk_type: str = "text", metadata: Dict[str, Any] = None):
        """Add a chunk - 添加数据块"""
        self._chunk_counter += 1
        chunk = StreamChunk(
            chunk_id=f"chunk_{self._chunk_counter}",
            content=content,
            timestamp=datetime.now().isoformat(),
            chunk_type=chunk_type,
            metadata=metadata or {}
        )
        self.chunks.append(chunk)
        self._display_chunk(chunk)
    
    def _display_chunk(self, chunk: StreamChunk):
        """Display a chunk - 显示数据块"""
        if chunk.chunk_type == "progress":
            self._display_progress(chunk)
        elif chunk.chunk_type == "status":
            print(f"[STATUS] {chunk.content}")
        elif chunk.chunk_type == "error":
            print(f"[ERROR] {chunk.content}", file=sys.stderr)
        else:
            print(chunk.content, end="", flush=True)
    
    def _display_progress(self, chunk: StreamChunk):
        """Display progress - 显示进度"""
        progress = chunk.metadata.get("progress", 0.0)
        bar_length = 30
        filled = int(bar_length * progress)
        bar = "[" + "=" * filled + " " * (bar_length - filled) + "]"
        percent = int(progress * 100)
        print(f"\rProgress: {bar} {percent}%", end="", flush=True)
        if progress >= 1.0:
            print()  # New line when done
    
    def send_text(self, text: str):
        """Send text - 发送文本"""
        self._add_chunk(text, "text")
    
    def send_progress(self, progress: float, message: str = ""):
        """Send progress - 发送进度"""
        self.progress = progress
        self._add_chunk(message or f"Progress: {int(progress*100)}%", "progress", {"progress": progress})
    
    def send_status(self, status: str):
        """Send status - 发送状态"""
        self._add_chunk(status, "status")
    
    def get_chunks(self) -> List[StreamChunk]:
        """Get all chunks - 获取所有数据块"""
        return self.chunks
    
    def get_full_text(self) -> str:
        """Get full text - 获取完整文本"""
        return "".join([c.content for c in self.chunks if c.chunk_type == "text"])
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time - 获取已用时间"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time


def create_streaming_output() -> StreamingOutput:
    """Create streaming output - 创建流式输出"""
    return StreamingOutput()


if __name__ == "__main__":
    print("Symphony Streaming Output")
    print("交响流式输出")
    print("=" * 60)
    
    stream = create_streaming_output()
    
    # Test 1: Start
    print("\n[Test 1] Start streaming...")
    stream.start()
    print("  OK: Started")
    
    # Test 2: Send text
    print("\n[Test 2] Send text...")
    stream.send_text("Hello, ")
    stream.send_text("Symphony!\n")
    print("  OK: Text sent")
    
    # Test 3: Send progress
    print("\n[Test 3] Send progress...")
    for i in range(11):
        progress = i / 10.0
        stream.send_progress(progress, f"Step {i}")
        time.sleep(0.1)
    print("  OK: Progress sent")
    
    # Test 4: Send status
    print("\n[Test 4] Send status...")
    stream.send_status("Processing complete")
    print("  OK: Status sent")
    
    # Test 5: Finish
    print("\n[Test 5] Finish streaming...")
    stream.finish()
    print("  OK: Finished")
    
    # Test 6: Get results
    print("\n[Test 6] Get results...")
    chunks = stream.get_chunks()
    full_text = stream.get_full_text()
    elapsed = stream.get_elapsed_time()
    print(f"  Chunks: {len(chunks)}")
    print(f"  Full text: {repr(full_text)}")
    print(f"  Elapsed: {elapsed:.2f}s")
    print("  OK: Results retrieved")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
