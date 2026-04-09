# -*- coding: utf-8 -*-
"""
豆包引擎CDP版本 (DoubaoCDPEngine)
================================
通过CDP直接连接OpenClaw浏览器中的豆包标签页??利用已有登录会话进行对话，无需重新启动浏览??
优势??1. 使用已有登录会话 - 无需处理Cookie失效
2. 直接操作DOM - 通过 CDP 执行 JS
3. 网络流量捕获 - 监听 fetch/xhr 请求
4. 流式输出支持 - 捕获SSE事件
"""
import asyncio
import json
import time
import threading
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
CDP_URL = "http://127.0.0.1:18800"

@dataclass
class DoubaoCDPConfig:
    """CDP引擎配置"""
    cdp_url: str = CDP_URL
    doubao_url: str = "https://www.doubao.com/chat/"
    timeout: int = 60
    model_name: str = "doubao-seed-2.0-pro"
    enable_stream: bool = True
    priority: int = 3


class DoubaoCDPResponse:
    """CDP引擎响应格式"""
    def __init__(self):
        self.success: bool = False
        self.content: str = ""
        self.error: Optional[str] = None
        self.model_used: str = "doubao-seed-2.0-pro"
        self.latency: float = 0.0
        self.streaming: bool = False


class DoubaoCDPEngine:
    """
    豆包CDP引擎
    
    通过CDP连接到OpenClaw浏览器中的豆包标签页??    利用JavaScript执行自动化操??    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, config: DoubaoCDPConfig = None):
        self.config = config or DoubaoCDPConfig()
        self._client = None
        self._ws = None
        self._target_id = None
        self._request_lock = threading.Lock()
        self._last_request_time = 0
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_latency": 0
        }
        
        logger.info(f"DoubaoCDPEngine initialized, CDP={self.config.cdp_url}")
    
    @classmethod
    def get_instance(cls, config: DoubaoCDPConfig = None) -> 'DoubaoCDPEngine':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance
    
    async def _connect(self) -> bool:
        """连接到CDP并获取豆包标签页"""
        import httpx
        import websockets
        
        try:
            # 获取标签页列??            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.config.cdp_url}/json", timeout=5.0)
                if response.status_code != 200:
                    logger.error(f"CDP: Failed to get targets, status={response.status_code}")
                    return False
                
                targets = response.json()
                
                # 查找豆包标签??                doubao_target = None
                for t in targets:
                    url = t.get('url', '')
                    if 'doubao.com' in url:
                        doubao_target = t
                        logger.info(f"Found Doubao tab: {t.get('title', 'Unknown')}")
                        break
                
                if not doubao_target:
                    # 尝试第一个可用的标签??                    if targets:
                        doubao_target = targets[0]
                        logger.warning(f"No Doubao tab found, using: {doubao_target.get('title', 'Unknown')}")
                    else:
                        logger.error("No browser tabs found")
                        return False
                
                self._target_id = doubao_target.get('id')
                ws_url = doubao_target.get('webSocketDebuggerUrl')
                
                if not ws_url:
                    logger.error("No WebSocket URL available")
                    return False
                
                # 连接WebSocket
                self._ws = await websockets.connect(ws_url, ping_interval=None)
                logger.info(f"Connected to CDP WebSocket for target {self._target_id}")
                return True
                
        except Exception as e:
            logger.error(f"CDP connection error: {e}")
            return False
    
    async def _send_cdp(self, method: str, params: Dict = None) -> Dict:
        """发送CDP命令"""
        import uuid
        
        if not self._ws:
            raise Exception("Not connected to CDP")
        
        msg_id = str(uuid.uuid4())
        msg = {"id": msg_id, "method": method}
        if params:
            msg["params"] = params
        
        await self._ws.send(json.dumps(msg))
        
        # 等待响应
        while True:
            resp = await self._ws.recv()
            data = json.loads(resp)
            if data.get("id") == msg_id:
                if data.get("error"):
                    raise Exception(f"CDP error: {data['error']}")
                return data.get("result", {})
    
    async def _evaluate_js(self, script: str) -> Any:
        """在页面中执行JavaScript"""
        result = await self._send_cdp("Runtime.evaluate", {
            "expression": script,
            "returnByValue": True
        })
        return result.get("result", {}).get("value")
    
    async def send_message_stream(self, prompt: str, callback: Callable[[str], None] = None) -> DoubaoCDPResponse:
        """
        通过CDP发送消息到豆包
        
        使用JavaScript自动化：
        1. 找到输入??        2. 填入内容
        3. 发送消??        4. 等待并获取响??        """
        start_time = time.time()
        response = DoubaoCDPResponse()
        response.streaming = self.config.enable_stream
        
        # 限流
        with self._request_lock:
            now = time.time()
            if now - self._last_request_time < 0.5:
                await asyncio.sleep(0.5 - (now - self._last_request_time))
            self._last_request_time = time.time()
        
        try:
            # 确保已连??            if not self._ws:
                connected = await self._connect()
                if not connected:
                    response.error = "Failed to connect to browser"
                    return response
            
            # 确保在豆包页??            await self._send_cdp("Page.navigate", {"url": self.config.doubao_url})
            await asyncio.sleep(2)  # 等待页面加载
            
            # 方法1: 直接使用JavaScript操作页面
            js_script = f"""
            (async () => {{
                // 等待输入??                const textarea = await new Promise((resolve, reject) => {{
                    const check = () => {{
                        const el = document.querySelector('textarea[placeholder*="发消??], textarea[placeholder*="技??]');
                        if (el) resolve(el);
                        else setTimeout(check, 100);
                    }};
                    check();
                    setTimeout(() => reject(new Error('Input not found')), 10000);
                }});
                
                // 填入内容
                textarea.focus();
                textarea.value = {json.dumps(prompt)};
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // 等待一??                await new Promise(r => setTimeout(r, 300));
                
                // 按Enter发??                textarea.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                
                return 'message_sent';
            }})()
            """
            
            result = await self._evaluate_js(js_script)
            logger.info(f"JS execution result: {result}")
            
            # 等待响应
            await asyncio.sleep(5)  # 等待AI响应
            
            # 获取响应内容
            response_js = """
            (async () => {
                // 查找最新的AI响应
                const messages = document.querySelectorAll('div[class*="browse-"], div[class*="message"]');
                let lastResponse = '';
                
                for (let i = Math.max(0, messages.length - 3); i < messages.length; i++) {
                    const msg = messages[i];
                    const text = msg.innerText || '';
                    // 排除用户消息
                    if (text && !msg.className.includes('user') && text.length > 20 && !text.includes('发消??)) {
                        lastResponse = text;
                    }
                }
                
                return lastResponse;
            })()
            """
            
            content = await self._evaluate_js(response_js)
            
            if content and len(content) > 5:
                response.success = True
                response.content = content
                if callback:
                    callback(content)
            else:
                response.error = "No response content found"
            
        except Exception as e:
            response.error = str(e)
            logger.error(f"DoubaoCDP error: {e}")
        
        response.latency = time.time() - start_time
        self._update_stats(response)
        
        return response
    
    def send_message(self, prompt: str) -> DoubaoCDPResponse:
        """同步版本"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_message_stream(prompt))
    
    def _update_stats(self, response: DoubaoCDPResponse):
        self.stats["total_requests"] += 1
        if response.success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
    
    def get_status(self) -> Dict:
        return {
            "engine": "DoubaoCDP",
            "connected": self._ws is not None,
            "target_id": self._target_id,
            "cdp_url": self.config.cdp_url,
            "model": self.config.model_name,
            "priority": self.config.priority,
            "stats": self.stats
        }
    
    async def close(self):
        """关闭CDP连接"""
        if self._ws:
            await self._ws.close()
            self._ws = None
            logger.info("CDP connection closed")


# ==================== 依赖安装检??====================

def check_dependencies():
    """检查依赖是否满??"""
    deps = {
        "httpx": "httpx",
        "websockets": "websockets"
    }
    
    missing = []
    for pkg, import_name in deps.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        logger.warning(f"Missing dependencies: {missing}")
        logger.info("Install with: pip install " + " ".join(missing))
        return False
    return True


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("豆包CDP引擎 (DoubaoCDPEngine)")
    print("=" * 60)
    
    if not check_dependencies():
        print("Please install missing dependencies first")
        exit(1)
    
    engine = DoubaoCDPEngine.get_instance()
    status = engine.get_status()
    print(f"\n引擎状?? {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    print("\n测试发送消??..")
    response = engine.send_message("你好，请回复'CDP测试成功'")
    
    print(f"\n响应结果:")
    print(f"  Success: {response.success}")
    print(f"  Content: {response.content[:200] if response.content else 'N/A'}...")
    print(f"  Latency: {response.latency:.3f}s")
    if response.error:
        print(f"  Error: {response.error}")
    
    print("\n引擎统计:")
    print(f"  {json.dumps(engine.stats, indent=2)}")
