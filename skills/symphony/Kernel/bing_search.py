# -*- coding: utf-8 -*-
"""
Bing搜索调度�?- 信息索引工具
将Bing搜索封装成统一的搜索接�?"""
import json
import re
from datetime import datetime
from urllib.parse import quote

# 尝试导入httpx，如果不可用则使用web_fetch
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class BingSearchScheduler:
    """Bing搜索调度�?""
    
    def __init__(self):
        self.name = "Bing搜索"
        self.type = "search"
        
    def search(self, query: str, num_results: int = 10) -> dict:
        """
        执行Bing搜索
        
        Args:
            query: 搜索关键�?            num_results: 返回结果数量 (默认10)
        
        Returns:
            dict: {
                'success': bool,
                'results': list of {'title', 'url', 'snippet'},
                'error': str
            }
        """
        result = {
            'success': False,
            'results': [],
            'error': ''
        }
        
        try:
            # 使用Bing搜索
            encoded_query = quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}"
            
            if HAS_HTTPX:
                response = httpx.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
            else:
                # 如果没有httpx，返回提�?                result['error'] = "需要httpx库支�?
                return result
            
            if response.status_code == 200:
                # 简单解析搜索结�?                html = response.text
                results = self._parse_results(html, num_results)
                result['results'] = results
                result['success'] = True
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _parse_results(self, html: str, num_results: int) -> list:
        """解析Bing搜索结果HTML"""
        results = []
        
        # 简单的正则匹配搜索结果
        # Bing搜索结果通常�?li class="sa_item">�?h2>�?        patterns = [
            r'<h2[^>]*><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a></h2><p>([^<]*)</p>',
            r'<li class="sa_item"[^>]*>.*?<a href="([^"]*)"[^>]*>([^<]*)</a>.*?<p>([^<]*)</p>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for url, title, snippet in matches[:num_results]:
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', title)
                snippet = re.sub(r'<[^>]+>', '', snippet)
                results.append({
                    'title': title.strip(),
                    'url': url.strip(),
                    'snippet': snippet.strip()[:200]
                })
                if len(results) >= num_results:
                    return results
        
        return results
    
    def get_status(self) -> dict:
        """获取状�?""
        return {
            'online': True,
            'name': self.name,
            'type': 'search',
            'last_check': datetime.now().isoformat()
        }


# 快速搜索函�?def quick_search(query: str, num_results: int = 5) -> list:
    """快速搜索接�?""
    scheduler = BingSearchScheduler()
    result = scheduler.search(query, num_results)
    if result['success']:
        return result['results']
    return []


if __name__ == "__main__":
    # 测试
    print("=== Bing搜索测试 ===")
    scheduler = BingSearchScheduler()
    r = scheduler.search("千问AI", 3)
    print(f"Success: {r['success']}")
    for item in r['results'][:3]:
        print(f"  - {item['title']}")
        print(f"    {item['url']}")

