# -*- coding: utf-8 -*-
"""
长文本处理模块 - Long Text Processor

功能：
- 文本分块处理
- 上下文窗口管理
- 文本快速拼接
- 滑动窗口摘要

使用：
    from long_text_processor import LongTextProcessor
    
    processor = LongTextProcessor(max_chunk_size=4000)
    result = processor.process_long_text(long_text)
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass
class TextChunk:
    """文本块"""
    index: int
    content: str
    start_pos: int
    end_pos: int
    token_count: int


@dataclass
class ProcessResult:
    """处理结果"""
    chunks: List[TextChunk]
    summary: str
    total_tokens: int
    process_time: float


class LongTextProcessor:
    """
    长文本处理器
    
    支持：
    - 智能分块
    - 滑动窗口
    - 上下文保持
    - 快速拼接
    """
    
    def __init__(
        self,
        max_chunk_size: int = 4000,
        overlap: int = 200,
        method: str = "smart"  # smart/fixed/sentence
    ):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.method = method
        
        # 统计
        self.stats = {
            "total_processed": 0,
            "total_chunks": 0,
            "avg_chunk_size": 0
        }
    
    def process_long_text(
        self,
        text: str,
        prompt: str = None
    ) -> ProcessResult:
        """
        处理长文本
        
        参数:
            text: 长文本
            prompt: 处理提示（可选）
        
        返回:
            ProcessResult: 处理结果
        """
        start_time = time.time()
        
        # 分块
        chunks = self.chunk_text(text)
        
        # 生成摘要
        summary = self._generate_summary(chunks, prompt)
        
        # 统计
        total_tokens = sum(c.token_count for c in chunks)
        
        self.stats["total_processed"] += 1
        self.stats["total_chunks"] += len(chunks)
        
        process_time = time.time() - start_time
        
        return ProcessResult(
            chunks=chunks,
            summary=summary,
            total_tokens=total_tokens,
            process_time=process_time
        )
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        将文本分块
        
        返回:
            List[TextChunk]: 文本块列表
        """
        if self.method == "fixed":
            return self._chunk_fixed(text)
        elif self.method == "sentence":
            return self._chunk_sentence(text)
        else:  # smart
            return self._chunk_smart(text)
    
    def _chunk_fixed(self, text: str) -> List[TextChunk]:
        """固定大小分块"""
        chunks = []
        text_len = len(text)
        
        for i in range(0, text_len, self.max_chunk_size - self.overlap):
            chunk_text = text[i:i + self.max_chunk_size]
            chunks.append(TextChunk(
                index=len(chunks),
                content=chunk_text,
                start_pos=i,
                end_pos=min(i + self.max_chunk_size, text_len),
                token_count=self._estimate_tokens(chunk_text)
            ))
            
            # 最后一块
            if i + self.max_chunk_size >= text_len:
                break
        
        return chunks
    
    def _chunk_sentence(self, text: str) -> List[TextChunk]:
        """按句子分块"""
        import re
        # 简单按句号、问号、感叹号分割
        sentences = re.split(r'[。！？\.\!\?]', text)
        
        chunks = []
        current_chunk = ""
        current_pos = 0
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            if len(current_chunk) + len(sent) <= self.max_chunk_size:
                current_chunk += sent + "。"
            else:
                if current_chunk:
                    chunks.append(TextChunk(
                        index=len(chunks),
                        content=current_chunk,
                        start_pos=current_pos,
                        end_pos=current_pos + len(current_chunk),
                        token_count=self._estimate_tokens(current_chunk)
                    ))
                current_chunk = sent + "。"
                current_pos += len(current_chunk)
        
        # 最后一个块
        if current_chunk:
            chunks.append(TextChunk(
                index=len(chunks),
                content=current_chunk,
                start_pos=current_pos,
                end_pos=current_pos + len(current_chunk),
                token_count=self._estimate_tokens(current_chunk)
            ))
        
        return chunks
    
    def _chunk_smart(self, text: str) -> List[TextChunk]:
        """智能分块（按段落+重叠）"""
        # 按段落分割
        paragraphs = text.split("\n\n")
        
        chunks = []
        current_chunk = ""
        current_pos = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果单个段落超过最大块大小，进一步分割
            if len(para) > self.max_chunk_size:
                # 先保存当前块
                if current_chunk:
                    chunks.append(TextChunk(
                        index=len(chunks),
                        content=current_chunk,
                        start_pos=current_pos,
                        end_pos=current_pos + len(current_chunk),
                        token_count=self._estimate_tokens(current_chunk)
                    ))
                    current_pos += len(current_chunk) + 2  # +2 for \n\n
                    current_chunk = ""
                
                # 对长段落进行固定分块
                sub_chunks = self._chunk_fixed(para)
                chunks.extend(sub_chunks)
            elif len(current_chunk) + len(para) + 2 <= self.max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(TextChunk(
                        index=len(chunks),
                        content=current_chunk,
                        start_pos=current_pos,
                        end_pos=current_pos + len(current_chunk),
                        token_count=self._estimate_tokens(current_chunk)
                    ))
                    current_pos += len(current_chunk) + 2
                
                current_chunk = para
        
        # 最后一个块
        if current_chunk:
            chunks.append(TextChunk(
                index=len(chunks),
                content=current_chunk,
                start_pos=current_pos,
                end_pos=current_pos + len(current_chunk),
                token_count=self._estimate_tokens(current_chunk)
            ))
        
        return chunks
    
    def _estimate_tokens(self, text: str) -> int:
        """估算token数量（中文约1.5字符/token）"""
        # 简单估算：中文约2字符/token，英文约4字符/token
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english = sum(1 for c in text if c.isascii())
        other = len(text) - chinese - english
        
        return int(chinese / 1.5 + english / 4 + other / 2)
    
    def _generate_summary(
        self,
        chunks: List[TextChunk],
        prompt: str = None
    ) -> str:
        """生成摘要"""
        if not chunks:
            return ""
        
        total_len = sum(len(c.content) for c in chunks)
        
        return f"共{len(chunks)}块，总长度{total_len}字符"
    
    def merge_chunks(
        self,
        chunks: List[TextChunk],
        method: str = "sequential"
    ) -> str:
        """
        合并文本块
        
        方法：
        - sequential: 顺序拼接
        - sliding: 滑动窗口拼接
        """
        if method == "sliding":
            return self._merge_sliding(chunks)
        else:
            return self._merge_sequential(chunks)
    
    def _merge_sequential(self, chunks: List[TextChunk]) -> str:
        """顺序拼接"""
        return "\n\n".join(c.content for c in chunks)
    
    def _merge_sliding(self, chunks: List[TextChunk]) -> str:
        """滑动窗口拼接"""
        if len(chunks) <= 1:
            return chunks[0].content if chunks else ""
        
        result = chunks[0].content
        
        for i in range(1, len(chunks)):
            # 保留重叠部分
            overlap_text = chunks[i].content[:self.overlap]
            rest_text = chunks[i].content[self.overlap:]
            result += "...\n" + overlap_text + rest_text
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return self.stats.copy()


# 测试
if __name__ == "__main__":
    processor = LongTextProcessor(max_chunk_size=1000, method="smart")
    print("LongTextProcessor: OK")
    
    # 测试
    test_text = "第一段内容。" * 200 + "\n\n" + "第二段内容。" * 200
    result = processor.process_long_text(test_text)
    
    print(f"分块数: {len(result.chunks)}")
    print(f"总token: {result.total_tokens}")
    print(f"处理时间: {result.process_time:.2f}s")
