#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_retriever.py - RAG检索增强生成
实现向量检索和知识增强
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib


class Document:
    """文档类"""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        初始化文档
        
        Args:
            content: 文档内容
            metadata: 元数据
        """
        self.content = content
        self.metadata = metadata or {}
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成文档ID"""
        return hashlib.md5(self.content.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }


class SimpleVectorStore:
    """简单向量存储（模拟）"""
    
    def __init__(self):
        """初始化向量存储"""
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, List[float]] = {}
    
    def add_document(self, doc: Document, embedding: List[float]) -> None:
        """添加文档"""
        self.documents[doc.id] = doc
        self.embeddings[doc.id] = embedding
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return self.documents.get(doc_id)
    
    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[tuple]:
        """
        搜索相似文档
        
        Args:
            query_embedding: 查询向量
            top_k: 返回数量
        
        Returns:
            [(文档ID, 相似度分数)]
        """
        results = []
        for doc_id, embedding in self.embeddings.items():
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append((doc_id, similarity))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


class SimpleEmbedder:
    """简单嵌入器（模拟）"""
    
    def embed(self, text: str) -> List[float]:
        """
        生成嵌入向量（模拟）
        
        Args:
            text: 文本
        
        Returns:
            嵌入向量
        """
        # 简单的模拟嵌入：基于字符的哈希
        embedding = []
        for i in range(128):
            hash_val = hash(f"{text}_{i}") % 1000 / 1000.0
            embedding.append(hash_val)
        return embedding


class RAGRetriever:
    """RAG检索器"""
    
    def __init__(self):
        """初始化RAG检索器"""
        self.vector_store = SimpleVectorStore()
        self.embedder = SimpleEmbedder()
        self.doc_count = 0
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加文档
        
        Args:
            content: 文档内容
            metadata: 元数据
        
        Returns:
            文档ID
        """
        doc = Document(content, metadata)
        embedding = self.embedder.embed(content)
        self.vector_store.add_document(doc, embedding)
        self.doc_count += 1
        return doc.id
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加文档
        
        Args:
            documents: 文档列表 [{"content": ..., "metadata": ...}]
        
        Returns:
            文档ID列表
        """
        doc_ids = []
        for doc_data in documents:
            doc_id = self.add_document(
                doc_data["content"],
                doc_data.get("metadata")
            )
            doc_ids.append(doc_id)
        return doc_ids
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回数量
        
        Returns:
            检索结果列表
        """
        query_embedding = self.embedder.embed(query)
        results = self.vector_store.search_similar(query_embedding, top_k)
        
        retrieved = []
        for doc_id, score in results:
            doc = self.vector_store.get_document(doc_id)
            if doc:
                retrieved.append({
                    "id": doc_id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "score": score
                })
        
        return retrieved
    
    def get_context_for_query(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """
        获取查询的上下文
        
        Args:
            query: 查询文本
            top_k: 返回数量
        
        Returns:
            上下文字符串
        """
        results = self.retrieve(query, top_k)
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result['content']}")
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_documents": self.doc_count,
            "embedding_dimension": 128
        }


class KnowledgeEnhancer:
    """知识增强器"""
    
    def __init__(self):
        """初始化知识增强器"""
        self.rag = RAGRetriever()
    
    def enhance_prompt(
        self,
        original_prompt: str,
        context: str
    ) -> str:
        """
        增强提示词
        
        Args:
            original_prompt: 原始提示词
            context: 上下文
        
        Returns:
            增强后的提示词
        """
        if not context:
            return original_prompt
        
        enhanced = f"""Based on the following context:

{context}

Please answer: {original_prompt}

Remember to:
1. Use information from the context
2. Be accurate and helpful
3. Cite sources when appropriate
"""
        return enhanced
    
    def query_with_rag(
        self,
        query: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        带RAG的查询
        
        Args:
            query: 查询
            top_k: 检索数量
        
        Returns:
            查询结果
        """
        context = self.rag.get_context_for_query(query, top_k)
        enhanced_prompt = self.enhance_prompt(query, context)
        
        return {
            "original_query": query,
            "context": context,
            "enhanced_prompt": enhanced_prompt,
            "sources": self.rag.retrieve(query, top_k)
        }


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("RAG Retriever Test")
    print("=" * 60)
    
    # 创建RAG检索器
    rag = RAGRetriever()
    
    # 添加文档
    print("\nAdding documents...")
    rag.add_document("Python is a programming language", {"category": "programming"})
    rag.add_document("Machine learning uses algorithms", {"category": "AI"})
    rag.add_document("RAG combines retrieval and generation", {"category": "AI"})
    
    # 检索
    print("\nRetrieving for query: 'What is Python?'")
    results = rag.retrieve("What is Python?", top_k=2)
    for r in results:
        print(f"  - Score: {r['score']:.3f}, Content: {r['content']}")
    
    # 获取上下文
    print("\nGetting context for: 'Tell me about AI'")
    context = rag.get_context_for_query("Tell me about AI", top_k=2)
    print(f"  Context:\n{context}")
    
    # 获取统计
    print("\nRAG Stats:")
    stats = rag.get_stats()
    print(f"  Total documents: {stats['total_documents']}")
    
    print("\nTest completed!")
