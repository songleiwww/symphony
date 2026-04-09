# -*- coding: utf-8 -*-
"""
豆包引擎 (DoubaoEngine) - 序境系统外部推理引擎
================================================
集成豆包对话能力到序境系统作为可选推理引??
核心功能:
1. 浏览器自动化 - 通过Playwright控制豆包浏览??2. API封装 - 封装豆包对话为标准化API调用
3. 流式输出 - 支持SSE流式响应解析
4. Symphony集成 - 适配EvolutionKernel.execute()标准格式

使用方法:
    from DoubaoEngine import DoubaoEngine, SymphonyDoubaoAdapter
    
    # 直接使用
    engine = DoubaoEngine()
    result = engine.send_message("你好")
    
    # 通过Symphony适配器使??    adapter = SymphonyDoubaoAdapter()
    result = adapter.execute("你的任务")
"""
import asyncio
import json
import time
import threading
import os
import sys
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import logging

# 设置UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='strict')
os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
KERNEL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'
os.makedirs(DATA_DIR, exist_ok=True)

COOKIE_PATH = os.path.join(KERNEL_DIR, 'doubao_cookies.json')


@dataclass
class DoubaoConfig:
    """豆包引擎配置"""
    # Playwright配置
    headless: bool = True
    
    # 认证配置
    cookie_path: str = COOKIE_PATH
    
    # 模型配置
    model_name: str = "doubao-seed-2.0-pro"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # 调度配置
    priority: int = 3  # 与model_federation配置一??    max_concurrent: int = 2
    QPS_limit: float = 2.0
    timeout: int = 60


class DoubaoResponse:
    """豆包响应格式"""
    def __init__(self):
        self.success: bool = False
        self.content: str = ""
        self.error: Optional[str] = None
        self.model_used: str = "doubao-seed-2.0-pro"
        self.latency: float = 0.0
        self.conversation_id: Optional[str] = None
        self.message_id: Optional[str] = None


class DoubaoEngine:
    """
    豆包引擎
    
    通过Playwright控制已登录的豆包浏览器进行对话，
    并封装为序境系统的外部推理引擎接??    
    Features:
    - 自动Cookie管理
    - 异步消息发??    - 流式输出支持（预留）
    - QPS限流保护
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, config: DoubaoConfig = None):
        self.config = config or DoubaoConfig()
        self._cookies = None
        self._request_lock = threading.Lock()
        self._last_request_time = 0
        self._conversation_history: List[Dict] = []
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0
        }
        
        logger.info(f"DoubaoEngine initialized (headless={self.config.headless})")
    
    @classmethod
    def get_instance(cls, config: DoubaoConfig = None) -> 'DoubaoEngine':
        """单例获取引擎实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance
    
    # ==================== Cookie管理 ====================
    
    def _load_cookies(self) -> List[Dict]:
        """加载认证Cookies"""
        if self._cookies is not None:
            return self._cookies
        
        cookies = []
        if os.path.exists(self.config.cookie_path):
            try:
                with open(self.config.cookie_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    # 支持列表和dict格式
                    cookie_list = data if isinstance(data, list) else data.get('cookies', [])
                    
                    for c in cookie_list:
                        cookie = {
                            'name': c['name'],
                            'value': c['value'],
                            'domain': c.get('domain', '.doubao.com'),
                            'path': c.get('path', '/'),
                        }
                        if c.get('expires', -1) > 0:
                            cookie['expires'] = c['expires']
                        cookies.append(cookie)
                    
                    self._cookies = cookies
                    logger.info(f"Loaded {len(cookies)} cookies from {self.config.cookie_path}")
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
                self._cookies = []
        return self._cookies or []
    
    def _check_cookie_valid(self) -> tuple:
        """检查Cookie有效??"""
        cookies = self._load_cookies()
        if not cookies:
            return False, "无Cookie"
        
        # 检查关键会话Cookie
        session = next((c for c in cookies if c['name'] in ['ttwid', 'sessionid', 'sid_tt']), None)
        if not session:
            return False, "会话Cookie缺失"
        
        return True, "Cookie有效"
    
    # ==================== 核心功能 ====================
    
    async def _send_message_impl(self, prompt: str, conversation_id: str = None) -> DoubaoResponse:
        """异步发送消息实??"""
        response = DoubaoResponse()
        start_time = time.time()
        
        # Cookie检??        valid, msg = self._check_cookie_valid()
        if not valid:
            response.error = f"认证失败: {msg}"
            return response
        
        # QPS限流
        with self._request_lock:
            now = time.time()
            min_interval = 1.0 / self.config.QPS_limit
            if now - self._last_request_time < min_interval:
                await asyncio.sleep(min_interval - (now - self._last_request_time))
            self._last_request_time = time.time()
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                # 启动浏览??                browser = await p.chromium.launch(
                    headless=self.config.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )
                
                # 添加认证cookies
                for cookie in self._load_cookies():
                    await context.add_cookies([cookie])
                
                page = await context.new_page()
                
                # 访问豆包聊天页面
                await page.goto("https://www.doubao.com/chat/", timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                
                # 如果有conversation_id，使用历史对??                if conversation_id:
                    await page.goto(f"https://www.doubao.com/chat/{conversation_id}", timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                
                # 等待并找到输入框
                input_box = await page.wait_for_selector(
                    'textarea[placeholder*="发消??], textarea[placeholder*="技??]',
                    timeout=10000
                )
                
                # 填入消息
                await input_box.fill(prompt)
                await asyncio.sleep(0.3)
                
                # 按Enter发??                await page.keyboard.press("Enter")
                
                # 等待响应
                response_selector = 'div[class*="browse-"], div[class*="message"]'
                try:
                    await page.wait_for_selector(response_selector, timeout=60000)
                    await asyncio.sleep(3)  # 等待完整响应
                    
                    # 提取响应内容
                    msg_elements = await page.query_selector_all(response_selector)
                    for elem in msg_elements[-5:]:
                        text = await elem.inner_text()
                        # 过滤：排除太短的、包??你好"的（可能是欢迎语）、包含用户输入的
                        if (len(text) > 20 and 
                            "你好" not in text[:5] and 
                            prompt[:10] not in text[:20]):
                            response.content = text
                            response.success = True
                            break
                    
                    if not response.success:
                        response.error = "无法提取有效响应"
                        
                except asyncio.TimeoutError:
                    response.error = "等待响应超时"
                
                await browser.close()
        
        except Exception as e:
            response.error = str(e)
            logger.error(f"Doubao request error: {e}")
        
        response.latency = time.time() - start_time
        self._update_stats(response)
        
        return response
    
    def send_message(self, prompt: str, conversation_id: str = None) -> DoubaoResponse:
        """同步发送消??"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._send_message_impl(prompt, conversation_id))
    
    async def send_message_async(self, prompt: str, conversation_id: str = None) -> DoubaoResponse:
        """异步发送消息（供外部协程调用）"""
        return await self._send_message_impl(prompt, conversation_id)
    
    def _update_stats(self, response: DoubaoResponse):
        """更新统计信息"""
        self.stats["total_requests"] += 1
        if response.success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        self.stats["total_latency"] += response.latency
    
    # ==================== 状态查??====================
    
    def get_status(self) -> Dict:
        """获取引擎状??"""
        valid, msg = self._check_cookie_valid()
        return {
            "engine": "DoubaoEngine",
            "online": valid,
            "status": msg,
            "model": self.config.model_name,
            "priority": self.config.priority,
            "headless": self.config.headless,
            "cookies_loaded": len(self._load_cookies()),
            "stats": {
                "total": self.stats["total_requests"],
                "success": self.stats["successful_requests"],
                "failed": self.stats["failed_requests"],
                "avg_latency": self.stats["total_latency"] / max(1, self.stats["total_requests"])
            }
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "doubao-seed-2.0-pro",
            "doubao-seed-2.5-pro-250315",
            "doubao-4.0-pro-32k-250115",
            "doubao-lite-4k-240828"
        ]
    
    def reset_conversation(self):
        """重置对话历史"""
        self._conversation_history.clear()
        logger.info("Conversation history reset")
    
    @property
    def name(self) -> str:
        return "DoubaoEngine"
    
    @property
    def provider(self) -> str:
        return "字节豆包"


# ==================== Symphony集成适配??====================

class SymphonyDoubaoAdapter:
    """
    序境系统适配??    
    将DoubaoEngine适配到EvolutionKernel的标准接口，
    实现零改动集成到序境系统
    """
    
    def __init__(self, engine: DoubaoEngine = None):
        self.engine = engine or DoubaoEngine.get_instance()
    
    def execute(self, prompt: str, **kwargs) -> Dict:
        """
        执行任务 - 兼容EvolutionKernel.execute()格式
        
        Args:
            prompt: 任务描述/用户输入
            **kwargs: 可选参??(stream, callback??
        
        Returns:
            Dict: {
                "success": bool,
                "result": str,  # 兼容KernelTask.result
                "error": str,
                "model_used": str,
                "latency": float
            }
        """
        start_time = time.time()
        
        response = self.engine.send_message(prompt)
        
        return {
            "success": response.success,
            "result": response.content,  # KernelTask.result格式
            "error": response.error,
            "model_used": response.model_used,
            "latency": response.latency,
            "total_time": time.time() - start_time
        }
    
    async def execute_async(self, prompt: str, **kwargs) -> Dict:
        """异步执行"""
        start_time = time.time()
        
        response = await self.engine.send_message_async(prompt)
        
        return {
            "success": response.success,
            "result": response.content,
            "error": response.error,
            "model_used": response.model_used,
            "latency": response.latency,
            "total_time": time.time() - start_time
        }
    
    def get_status(self) -> Dict:
        """获取适配器状??"""
        return self.engine.get_status()
    
    def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return self.engine.get_available_models()
    
    def register_to_federation(self, federation) -> bool:
        """
        注册到ModelFederation
        
        让序境系统可以通过federation调用豆包引擎
        """
        try:
            if hasattr(federation, 'provider_pools'):
                from model_federation import ProviderPool
                
                pool = ProviderPool(
                    name="字节豆包",
                    priority=self.engine.config.priority,
                    max_concurrent=self.engine.config.max_concurrent,
                    timeout=self.engine.config.timeout,
                    retry=2
                )
                
                federation.provider_pools["字节豆包"] = pool
                logger.info("DoubaoEngine registered to ModelFederation")
                return True
        except Exception as e:
            logger.error(f"Failed to register to federation: {e}")
        
        return False


# ==================== 快速测??====================

if __name__ == "__main__":
    print("=" * 60)
    print("豆包引擎 (DoubaoEngine) - 序境系统外部推理引擎")
    print("=" * 60)
    
    engine = DoubaoEngine.get_instance()
    adapter = SymphonyDoubaoAdapter(engine)
    
    print("\n[引擎状态]")
    status = adapter.get_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    
    print("\n[可用模型]")
    for model in adapter.get_available_models():
        print(f"  - {model}")
    
    print("\n[执行测试]")
    print("发送测试消??..")
    
    result = adapter.execute("请简单介绍一下你自己，回??测试成功'")
    
    print(f"\n[执行结果]")
    print(f"  Success: {result['success']}")
    print(f"  Result: {result['result'][:200] if result['result'] else 'N/A'}...")
    print(f"  Latency: {result['latency']:.3f}s")
    print(f"  Total Time: {result['total_time']:.3f}s")
    if result.get('error'):
        print(f"  Error: {result['error']}")
    
    print("\n[引擎统计]")
    print(json.dumps(engine.stats, indent=2))
