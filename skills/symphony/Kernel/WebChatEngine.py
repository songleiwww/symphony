# -*- coding: utf-8 -*-
"""
统一WebChat引擎 (WebChatEngine)
================================
同时支持豆包、千问、DeepSeek三大平台的浏览器自动??
策略说明:
- 使用OpenClaw browser工具或Playwright自动??- Cookie认证
- QPS限流保护
- 适配EvolutionKernel标准接口

使用方法:
    from WebChatEngine import WebChatEngine, create_engine
    
    # 创建引擎
    engine = create_engine('doubao')  # ??'qianwen', 'deepseek'
    
    # 发送消??    result = engine.send_message("你好")
    
    # 批量发??    results = engine.batch_send(["消息1", "消息2"])
"""
import asyncio
import json
import time
import threading
import os
import sys
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# UTF-8编码设置
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='strict')
os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
KERNEL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'
DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'
os.makedirs(DATA_DIR, exist_ok=True)


class Platform(Enum):
    """支持的平??"""
    DOUBÃO = "doubao"
    QIĄNWEN = "qianwen"
    DEEPSEEK = "deepseek"


@dataclass
class PlatformConfig:
    """平台配置"""
    name: str
    display_name: str
    chat_url: str
    cookie_path: str
    input_placeholder: str  # 输入框placeholder关键??    response_selector: str   # 响应元素选择??    model_name: str
    priority: int = 3


# 平台配置??PLATFORM_CONFIGS = {
    Platform.DOUBÃO: PlatformConfig(
        name="doubao",
        display_name="豆包",
        chat_url="https://www.doubao.com/chat/",
        cookie_path=os.path.join(KERNEL_DIR, "doubao_cookies.json"),
        input_placeholder="发消??,
        response_selector='div[class*="browse-"]',
        model_name="doubao-seed-2.0-pro",
        priority=3
    ),
    Platform.QIĄNWEN: PlatformConfig(
        name="qianwen",
        display_name="千问",
        chat_url="https://qianwen.com/",  # 需确认
        cookie_path=os.path.join(KERNEL_DIR, "qianwen_cookies.json"),
        input_placeholder="向千问提??,
        response_selector='div[class*="message"]',
        model_name="qwen-max",
        priority=2
    ),
    Platform.DEEPSEEK: PlatformConfig(
        name="deepseek",
        display_name="DeepSeek",
        chat_url="https://chat.deepseek.com/",
        cookie_path=os.path.join(KERNEL_DIR, "deepseek_cookies.json"),
        input_placeholder="输入",
        response_selector='div[class*="markdown"]',
        model_name="deepseek-chat",
        priority=2
    ),
}


@dataclass
class WebChatResponse:
    """统一响应格式"""
    success: bool = False
    content: str = ""
    error: Optional[str] = None
    platform: str = ""
    model_used: str = ""
    latency: float = 0.0
    conversation_id: Optional[str] = None


# ==================== 统一WebChat引擎 ====================

class WebChatEngine:
    """
    统一WebChat引擎
    
    支持豆包、千问、DeepSeek三大平台的浏览器自动??    """
    
    _instances: Dict[Platform, 'WebChatEngine'] = {}
    _lock = threading.Lock()
    
    def __init__(self, platform: Platform):
        self.platform = platform
        self.config = PLATFORM_CONFIGS[platform]
        self._cookies = None
        self._request_lock = threading.Lock()
        self._last_request_time = 0
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0
        }
        
        logger.info(f"WebChatEngine initialized for {self.config.display_name}")
    
    @classmethod
    def get_instance(cls, platform: Platform) -> 'WebChatEngine':
        """获取指定平台的引擎实??"""
        with cls._lock:
            if platform not in cls._instances:
                cls._instances[platform] = cls(platform)
            return cls._instances[platform]
    
    @classmethod
    def create(cls, platform_name: str) -> 'WebChatEngine':
        """根据名称创建引擎"""
        try:
            platform = Platform(platform_name.lower().replace(" ", ""))
        except ValueError:
            raise ValueError(f"Unknown platform: {platform_name}, supported: doubao, qianwen, deepseek")
        return cls.get_instance(platform)
    
    # ==================== Cookie管理 ====================
    
    def _load_cookies(self) -> List[Dict]:
        """加载认证Cookies"""
        if self._cookies is not None:
            return self._cookies
        
        cookies = []
        cookie_path = self.config.cookie_path
        
        # 尝试多个可能的路??        if not os.path.exists(cookie_path):
            # 千问可能是raw格式
            raw_path = cookie_path.replace(".json", "_raw.json")
            if os.path.exists(raw_path):
                cookie_path = raw_path
        
        if os.path.exists(cookie_path):
            try:
                with open(cookie_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    
                    # 处理不同格式
                    if isinstance(data, list):
                        cookie_list = data
                    elif isinstance(data, dict):
                        if "cookies" in data:
                            cookie_list = data["cookies"]
                        elif "result" in data and "cookies" in data["result"]:
                            cookie_list = data["result"]["cookies"]
                        else:
                            cookie_list = [data]
                    else:
                        cookie_list = []
                    
                    for c in cookie_list:
                        if not isinstance(c, dict):
                            continue
                        cookie = {
                            'name': c.get('name', ''),
                            'value': c.get('value', ''),
                            'domain': c.get('domain', f'.{self.config.name}.com'),
                            'path': c.get('path', '/'),
                        }
                        if c.get('expires', -1) > 0:
                            cookie['expires'] = c['expires']
                        cookies.append(cookie)
                    
                    self._cookies = cookies
                    logger.info(f"Loaded {len(cookies)} cookies for {self.config.display_name}")
            except Exception as e:
                logger.warning(f"Failed to load cookies for {self.config.display_name}: {e}")
                self._cookies = []
        
        return self._cookies or []
    
    def _check_cookie_valid(self) -> tuple:
        """检查Cookie有效??"""
        cookies = self._load_cookies()
        if not cookies:
            return False, "无Cookie"
        
        # 检查关键Cookie（不同平台不同）
        key_cookies = {
            Platform.DOUBÃO: ['ttwid', 'sessionid', 'sid_tt'],
            Platform.QIĄNWEN: ['isg', 'b-user-id'],
            Platform.DEEPSEEK: ['ds_session_id', 'smidV2']
        }
        
        required = key_cookies.get(self.platform, [])
        missing = [c for c in required if not any(cookie['name'] == c for cookie in cookies)]
        
        if missing:
            return False, f"缺少关键Cookie: {missing}"
        
        return True, "Cookie有效"
    
    # ==================== 核心功能 ====================
    
    async def _send_message_impl(self, prompt: str) -> WebChatResponse:
        """异步发送消息实??"""
        response = WebChatResponse(platform=self.config.name, model_used=self.config.model_name)
        start_time = time.time()
        
        # Cookie检??        valid, msg = self._check_cookie_valid()
        if not valid:
            response.error = f"认证失败: {msg}"
            return response
        
        # QPS限流
        with self._request_lock:
            now = time.time()
            min_interval = 1.0 / 2.0  # 2 QPS
            if now - self._last_request_time < min_interval:
                await asyncio.sleep(min_interval - (now - self._last_request_time))
            self._last_request_time = time.time()
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )
                
                # 添加认证cookies
                for cookie in self._load_cookies():
                    await context.add_cookies([cookie])
                
                page = await context.new_page()
                
                # 访问聊天页面
                # 注意：不使用networkidle，因为豆包有持续的WebSocket连接
                await page.goto(self.config.chat_url, timeout=30000)
                await page.wait_for_load_state("domcontentloaded", timeout=15000)
                await asyncio.sleep(2)  # 额外等待确保页面完全渲染
                
                # 等待输入??                input_box = await page.wait_for_selector(
                    f'textarea[placeholder*="{self.config.input_placeholder}"], '
                    f'textarea[placeholder*="技??]',
                    timeout=10000
                )
                
                # 填入消息
                await input_box.fill(prompt)
                await asyncio.sleep(0.3)
                
                # 发??                await page.keyboard.press("Enter")
                
                # 等待响应
                try:
                    await page.wait_for_selector(self.config.response_selector, timeout=60000)
                    await asyncio.sleep(3)  # 等待完整响应
                    
                    # 提取响应
                    elements = await page.query_selector_all(self.config.response_selector)
                    for elem in elements[-5:]:
                        text = await elem.inner_text()
                        if len(text) > 20 and prompt[:10] not in text[:20]:
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
            logger.error(f"{self.config.display_name} request error: {e}")
        
        response.latency = time.time() - start_time
        self._update_stats(response)
        
        return response
    
    def send_message(self, prompt: str) -> WebChatResponse:
        """同步发送消??"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._send_message_impl(prompt))
    
    def _update_stats(self, response: WebChatResponse):
        """更新统计"""
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
            "platform": self.config.name,
            "display_name": self.config.display_name,
            "online": valid,
            "status": msg,
            "model": self.config.model_name,
            "priority": self.config.priority,
            "cookies_loaded": len(self._load_cookies()),
            "stats": {
                "total": self.stats["total_requests"],
                "success": self.stats["successful_requests"],
                "failed": self.stats["failed_requests"],
                "avg_latency": self.stats["total_latency"] / max(1, self.stats["total_requests"])
            }
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return [self.config.model_name]
    
    @property
    def name(self) -> str:
        return f"WebChat-{self.config.display_name}"


# ==================== 工厂函数 ====================

def create_engine(platform: str) -> WebChatEngine:
    """创建WebChat引擎"""
    return WebChatEngine.create(platform)


def get_all_platforms_status() -> Dict[str, Dict]:
    """获取所有平台状??"""
    return {
        platform.value: WebChatEngine.get_instance(platform).get_status()
        for platform in Platform
    }


# ==================== Symphony适配??====================

class SymphonyWebChatAdapter:
    """序境系统统一适配??"""
    
    def __init__(self, platform: str = "doubao"):
        self.engine = WebChatEngine.create(platform)
        self.platform = platform
    
    def execute(self, prompt: str, **kwargs) -> Dict:
        """执行任务 - 兼容EvolutionKernel格式"""
        start_time = time.time()
        response = self.engine.send_message(prompt)
        
        return {
            "success": response.success,
            "result": response.content,
            "error": response.error,
            "model_used": response.model_used,
            "latency": response.latency,
            "total_time": time.time() - start_time,
            "platform": response.platform
        }
    
    def get_status(self) -> Dict:
        return self.engine.get_status()


# ==================== 快速测??====================

if __name__ == "__main__":
    print("=" * 60)
    print("统一WebChat引擎 - 序境系统外部推理引擎")
    print("=" * 60)
    
    print("\n[平台状态]")
    all_status = get_all_platforms_status()
    for name, status in all_status.items():
        online = "?? if status["online"] else "??
        print(f"  {online} {status['display_name']}: {status['status']}")
    
    print("\n[测试豆包]")
    engine = WebChatEngine.get_instance(Platform.DOUBÃO)
    adapter = SymphonyWebChatAdapter("doubao")
    
    print("发送测试消??..")
    result = adapter.execute("你好，请回复'测试成功'")
    
    print(f"\n[执行结果]")
    print(f"  Success: {result['success']}")
    print(f"  Result: {result['result'][:200] if result['result'] else 'N/A'}...")
    print(f"  Latency: {result['latency']:.3f}s")
    if result.get('error'):
        print(f"  Error: {result['error']}")
    
    print("\n[引擎统计]")
    print(json.dumps(engine.stats, indent=2))
