# -*- coding: utf-8 -*-
"""
Tavily MCP搜索调度器 - 高级AI搜索工具
============================
通过 MCP 协议调用 Tavily AI 搜索服务，提供高质量的网页搜索、内容提取和研究能力
遵循序境内核设计规范，保持接口统一
"""

import json
import subprocess
from typing import List, Dict, Optional, Any, Union
from datetime import datetime


class TavilyMcpSearchScheduler:
    """Tavily MCP搜索调度器
    
    通过 mcporter CLI 调用 Tavily MCP 服务器，提供：
    - 网页搜索 (tavily_search)
    - URL内容提取 (tavily_extract)
    - 网站爬取 (tavily_crawl)
    - 综合研究 (tavily_research)
    - 技术文档搜索 (tavily_skill)
    """
    
    def __init__(self):
        self.name = "Tavily MCP搜索"
        self.type = "search"
        self.mcp_server = "tavily"
        self.api_url = "https://mcp.tavily.com/mcp/"
        self._connected = True  # 假设已连接，实际调用失败会返回错误
    
    def _check_connection(self) -> bool:
        """检查MCP服务器连接"""
        # mcporter 通常安装在 npm global 目录
        # 先假设配置正确，在实际调用时再处理错误
        self._connected = True
        return True
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    def search(self, 
               query: str, 
               max_results: int = 5, 
               search_depth: str = "fast",
               include_raw_content: bool = False,
               topic: str = "general") -> Dict[str, Any]:
        """
        执行Tavily网页搜索
        
        Args:
            query: 搜索查询
            max_results: 最大返回结果数 (默认5，范围1-20)
            search_depth: 搜索深度 - "basic", "advanced", "fast", "ultra-fast" (默认fast)
            include_raw_content: 是否包含原始网页内容 (默认False)
            topic: 搜索主题 - "general" or "news" (默认general)
        
        Returns:
            {
                'success': bool,
                'query': str,
                'results': list[{'title', 'url', 'content', 'score'}],
                'answer': Optional[str],  # AI合成答案（如果有）
                'follow_up_questions': list,
                'images': list,
                'response_time': float,
                'error': str
            }
        """
        result = {
            'success': False,
            'query': query,
            'results': [],
            'answer': None,
            'follow_up_questions': [],
            'images': [],
            'response_time': 0.0,
            'error': ''
        }
        
        if not self._connected:
            result['error'] = "MCP服务器未连接，请检查mcporter配置"
            return result
        
        try:
            # 构建mcporter调用命令
            cmd = [
                "mcporter", "call", 
                f"{self.mcp_server}.tavily_search",
                f"query={query}",
                f"max_results={max_results}",
                f"search_depth={search_depth}",
                f"topic={topic}",
                f"include_raw_content={json.dumps(include_raw_content).lower()}"
            ]
            
            start_time = datetime.now()
            # 在Windows上强制UTF-8解码
            proc = subprocess.run(cmd, capture_output=True, text=False, timeout=30, shell=True)
            end_time = datetime.now()
            result['response_time'] = (end_time - start_time).total_seconds()
            
            if proc.returncode != 0:
                stderr = proc.stderr.decode('utf-8', errors='replace')
                result['error'] = f"调用失败: {stderr[:200]}"
                return result
            
            # 解析JSON输出 - 强制UTF-8解码
            stdout = proc.stdout.decode('utf-8', errors='replace')
            try:
                response = json.loads(stdout)
            except json.JSONDecodeError:
                # 可能输出了其他信息，尝试提取最后一个JSON块
                lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
                for line in reversed(lines):
                    try:
                        response = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
                else:
                    result['error'] = f"无法解析响应: {stdout[:200]}..."
                    return result
            
            # 整理结果
            result['success'] = True
            result['results'] = response.get('results', [])
            result['answer'] = response.get('answer')
            result['follow_up_questions'] = response.get('follow_up_questions', [])
            result['images'] = response.get('images', [])
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def extract(self, 
                urls: List[str], 
                extract_depth: str = "basic",
                format: str = "markdown",
                query: str = "") -> Dict[str, Any]:
        """
        从URL提取网页内容
        
        Args:
            urls: 需要提取内容的URL列表
            extract_depth: 提取深度 - "basic" or "advanced" (默认basic)
            format: 输出格式 - "markdown" or "text" (默认markdown)
            query: 相关性重排查询（可选）
        
        Returns:
            {
                'success': bool,
                'results': list[{'url', 'content', 'extracted_at'}],
                'error': str
            }
        """
        result = {
            'success': False,
            'urls': urls,
            'results': [],
            'error': ''
        }
        
        if not self._connected:
            result['error'] = "MCP服务器未连接，请检查mcporter配置"
            return result
        
        if len(urls) == 0:
            result['error'] = "URL列表不能为空"
            return result
        
        try:
            # 使用JSON参数避免shell转义问题
            params = json.dumps({
                "urls": urls,
                "extract_depth": extract_depth,
                "format": format,
                "query": query
            })
            
            cmd = ["mcporter", "call", f"{self.mcp_server}.tavily_extract", f"--json={params}"]
            
            proc = subprocess.run(cmd, capture_output=True, text=False, timeout=60, shell=True)
            
            if proc.returncode != 0:
                stderr = proc.stderr.decode('utf-8', errors='replace')
                result['error'] = f"调用失败: {stderr[:200]}"
                return result
            
            stdout = proc.stdout.decode('utf-8', errors='replace')
            response = json.loads(stdout)
            
            result['success'] = True
            result['results'] = response.get('results', [])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def crawl(self,
              url: str,
              max_depth: int = 1,
              max_breadth: int = 20,
              limit: int = 50,
              instructions: str = "") -> Dict[str, Any]:
        """
        爬取网站
        
        Args:
            url: 起始URL
            max_depth: 最大爬取深度 (默认1)
            max_breadth: 每层最大链接数 (默认20)
            limit: 总处理链接限制 (默认50)
            instructions: 自然语言筛选说明（可选）
        
        Returns:
            {
                'success': bool,
                'root_url': str,
                'pages': list[{'url', 'title', 'content'}],
                'total_pages': int,
                'error': str
            }
        """
        result = {
            'success': False,
            'root_url': url,
            'pages': [],
            'total_pages': 0,
            'error': ''
        }
        
        if not self._connected:
            result['error'] = "MCP服务器未连接，请检查mcporter配置"
            return result
        
        try:
            params = json.dumps({
                "url": url,
                "max_depth": max_depth,
                "max_breadth": max_breadth,
                "limit": limit,
                "instructions": instructions
            })
            
            cmd = ["mcporter", "call", f"{self.mcp_server}.tavily_crawl", f"--json={params}"]
            
            proc = subprocess.run(cmd, capture_output=True, text=False, timeout=120, shell=True)
            
            if proc.returncode != 0:
                stderr = proc.stderr.decode('utf-8', errors='replace')
                result['error'] = f"调用失败: {stderr[:200]}"
                return result
            
            stdout = proc.stdout.decode('utf-8', errors='replace')
            response = json.loads(stdout)
            
            result['success'] = True
            result['pages'] = response.get('pages', [])
            result['total_pages'] = len(result['pages'])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def research(self,
                 input: str,
                 model: str = "auto") -> Dict[str, Any]:
        """
        综合深度研究
        
        Args:
            input: 研究任务描述
            model: 深度 - "mini", "pro", "auto" (默认auto)
        
        Returns:
            {
                'success': bool,
                'input': str,
                'report': str,
                'sources': list,
                'error': str
            }
        """
        result = {
            'success': False,
            'input': input,
            'report': '',
            'sources': [],
            'error': ''
        }
        
        if not self._connected:
            result['error'] = "MCP服务器未连接，请检查mcporter配置"
            return result
        
        try:
            params = json.dumps({
                "input": input,
                "model": model
            })
            
            cmd = ["mcporter", "call", f"{self.mcp_server}.tavily_research", f"--json={params}"]
            
            proc = subprocess.run(cmd, capture_output=True, text=False, timeout=180, shell=True)
            
            if proc.returncode != 0:
                stderr = proc.stderr.decode('utf-8', errors='replace')
                result['error'] = f"调用失败: {stderr[:200]}"
                return result
            
            stdout = proc.stdout.decode('utf-8', errors='replace')
            response = json.loads(stdout)
            
            result['success'] = True
            result['report'] = response.get('report', response.get('content', ''))
            result['sources'] = response.get('sources', [])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def search_docs(self,
                    query: str,
                    library: str = "",
                    language: str = "",
                    task: Optional[str] = None,
                    context: str = "") -> Dict[str, Any]:
        """
        搜索技术文档/API/库
        
        Args:
            query: 查询问题
            library: 目标库/包名（可选，例如 "fastapi", "react"）
            language: 编程语言（可选）
            task: 任务类型 - "integrate", "configure", "debug", "migrate", "understand" (可选)
            context: 项目上下文描述（可选）
        
        Returns:
            {
                'success': bool,
                'query': str,
                'results': list[{'title', 'content', 'url', 'score'}],
                'error': str
            }
        """
        result = {
            'success': False,
            'query': query,
            'results': [],
            'error': ''
        }
        
        if not self._connected:
            result['error'] = "MCP服务器未连接，请检查mcporter配置"
            return result
        
        try:
            params: Dict[str, Any] = {
                "query": query
            }
            if library:
                params["library"] = library
            if language:
                params["language"] = language
            if task:
                params["task"] = task
            if context:
                params["context"] = context
            
            cmd = ["mcporter", "call", f"{self.mcp_server}.tavily_skill", f"--json={json.dumps(params)}"]
            
            proc = subprocess.run(cmd, capture_output=True, text=False, timeout=60, shell=True)
            
            if proc.returncode != 0:
                stderr = proc.stderr.decode('utf-8', errors='replace')
                result['error'] = f"调用失败: {stderr[:200]}"
                return result
            
            stdout = proc.stdout.decode('utf-8', errors='replace')
            response = json.loads(stdout)
            
            result['success'] = True
            result['results'] = response.get('results', [])
            result['answer'] = response.get('answer')
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            'online': self._connected,
            'name': self.name,
            'type': self.type,
            'server': self.mcp_server,
            'api_url': self.api_url,
            'last_check': datetime.now().isoformat(),
            'available_tools': [
                'search', 'extract', 'crawl', 'research', 'search_docs'
            ]
        }


# 快速搜索接口
def quick_search(query: str, max_results: int = 5) -> List[Dict]:
    """快速搜索 - 简化接口
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数
    
    Returns:
        list: 搜索结果列表，每个元素 {'title', 'url', 'content', 'score'}
    """
    scheduler = TavilyMcpSearchScheduler()
    result = scheduler.search(query, max_results=max_results, search_depth="fast")
    if result['success']:
        return result['results']
    return []


# 快速提取接口
def quick_extract(url: str) -> Optional[str]:
    """快速提取单个URL内容
    
    Args:
        url: URL地址
    
    Returns:
        str: 提取的markdown内容，失败返回None
    """
    scheduler = TavilyMcpSearchScheduler()
    result = scheduler.extract([url])
    if result['success'] and len(result['results']) > 0:
        return result['results'][0].get('content', '')
    return None


if __name__ == "__main__":
    # 测试
    print("=== Tavily MCP搜索测试 ===")
    scheduler = TavilyMcpSearchScheduler()
    status = "OK 已连接" if scheduler.is_connected() else "X 未连接"
    print(f"连接状态: {status}")
    
    if scheduler.is_connected():
        print("\n测试搜索: 智谱AI glm-4-flash 免费政策")
        r = scheduler.search("智谱AI glm-4-flash 官方免费政策", max_results=3, search_depth="fast")
        print(f"成功: {r['success']}")
        if r['success']:
            print(f"响应时间: {r['response_time']:.2f}s")
            print(f"结果数: {len(r['results'])}")
            for i, item in enumerate(r['results'][:3]):
                title = item.get('title', 'No title')
                url = item.get('url', 'No url')
                score = item.get('score', 0)
                content = item.get('content', '')
                print(f"\n{i+1}. {title}")
                print(f"   URL: {url}")
                print(f"   得分: {score:.4f}")
                if content:
                    print(f"   摘要: {content[:150]}...")
    
        print("\n状态:")
        print(json.dumps(scheduler.get_status(), indent=2, ensure_ascii=False))
