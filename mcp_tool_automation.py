#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Symphony MCP工具适配自动化系统 v1.0
============================================================================
根据讨论决议实现：
1. MCP工具自动发现和连接
2. 统一适配层
3. 动态加载和热插拔
4. 失败降级和恢复
5. OpenClaw SubAgent协调
============================================================================
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


# ==================== 工具类型定义 ====================

class ToolType(Enum):
    """工具类型"""
    MCP = "mcp"           # MCP协议工具
    HTTP = "http"         # HTTP API工具
    FUNCTION = "function" # 函数工具
    CLI = "cli"           # 命令行工具


class ToolStatus(Enum):
    """工具状态"""
    DISCOVERED = "discovered"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"
    ERROR = "error"
    DISCONNECTED = "disconnected"


# ==================== 工具定义 ====================

@dataclass
class Tool:
    """工具定义"""
    tool_id: str
    name: str
    tool_type: ToolType
    endpoint: str = ""              # 连接地址
    capabilities: List[str] = field(default_factory=list)
    schema: Dict = field(default_factory=dict)  # 接口定义
    status: ToolStatus = ToolStatus.DISCOVERED
    health_check_interval: int = 30  # 健康检查间隔（秒）
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    metadata: Dict = field(default_factory=dict)


# ==================== 工具注册中心 ====================

class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._mcp_servers = {
            'awesun': 'http://127.0.0.1:8080/mcp',  # 向日葵MCP
            'tavily': 'https://mcp.tavily.com',       # Tavily MCP
        }
    
    def discover_mcp_tools(self) -> List[Tool]:
        """自动发现MCP工具"""
        discovered = []
        
        # 扫描预配置的MCP服务器
        for name, endpoint in self._mcp_servers.items():
            tool = Tool(
                tool_id=f"mcp_{name}",
                name=f"MCP {name}",
                tool_type=ToolType.MCP,
                endpoint=endpoint,
                capabilities=['execute', 'query'],
                status=ToolStatus.DISCOVERED
            )
            self.tools[tool.tool_id] = tool
            discovered.append(tool)
        
        return discovered
    
    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.tool_id] = tool
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(tool_id)
    
    def list_tools(self, status: ToolStatus = None, tool_type: ToolType = None) -> List[Tool]:
        """列出工具"""
        result = list(self.tools.values())
        
        if status:
            result = [t for t in result if t.status == status]
        if tool_type:
            result = [t for t in result if t.tool_type == tool_type]
        
        return result


# ==================== 适配器层 ====================

class ToolAdapter(ABC):
    """工具适配器基类"""
    
    @abstractmethod
    def execute(self, tool: Tool, action: str, params: Dict) -> Dict:
        """执行工具操作"""
        pass
    
    @abstractmethod
    def health_check(self, tool: Tool) -> bool:
        """健康检查"""
        pass


class MCPAdapter(ToolAdapter):
    """MCP协议适配器"""
    
    def __init__(self):
        self.session_id: Optional[str] = None
    
    def execute(self, tool: Tool, action: str, params: Dict) -> Dict:
        """执行MCP工具调用"""
        import requests
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.session_id:
                headers['Mcp-Session-Id'] = self.session_id
            
            payload = {
                'jsonrpc': '2.0',
                'id': int(time.time() * 1000),
                'method': action,
                'params': params
            }
            
            response = requests.post(
                tool.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 保存session_id
            if 'mcp-session-id' in response.headers:
                self.session_id = response.headers['mcp-session-id']
            
            if response.status_code == 200:
                result = response.json()
                return {'success': True, 'result': result}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def health_check(self, tool: Tool) -> bool:
        """MCP健康检查"""
        result = self.execute(tool, 'ping', {})
        return result.get('success', False)


class HTTPAdapter(ToolAdapter):
    """HTTP API适配器"""
    
    def execute(self, tool: Tool, action: str, params: Dict) -> Dict:
        """执行HTTP调用"""
        import requests
        
        try:
            response = requests.post(
                tool.endpoint,
                json=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return {'success': True, 'result': response.json()}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def health_check(self, tool: Tool) -> bool:
        """HTTP健康检查"""
        try:
            import requests
            response = requests.get(tool.endpoint, timeout=5)
            return response.status_code < 500
        except:
            return False


# ==================== 适配器管理器 ====================

class AdapterManager:
    """适配器管理器"""
    
    def __init__(self):
        self.adapters: Dict[ToolType, ToolAdapter] = {
            ToolType.MCP: MCPAdapter(),
            ToolType.HTTP: HTTPAdapter(),
        }
    
    def get_adapter(self, tool_type: ToolType) -> Optional[ToolAdapter]:
        """获取适配器"""
        return self.adapters.get(tool_type)
    
    def register_adapter(self, tool_type: ToolType, adapter: ToolAdapter):
        """注册适配器"""
        self.adapters[tool_type] = adapter


# ==================== 熔断器 ====================

class CircuitBreaker:
    """工具熔断器"""
    
    def __init__(self):
        self.failure_threshold = 3
        self.recovery_timeout = 60
        self.state: Dict[str, str] = {}  # tool_id -> state
        self.failures: Dict[str, int] = {}
    
    def record_failure(self, tool_id: str) -> bool:
        """记录失败"""
        self.failures[tool_id] = self.failures.get(tool_id, 0) + 1
        
        if self.failures[tool_id] >= self.failure_threshold:
            self.state[tool_id] = 'open'
            return True
        return False
    
    def record_success(self, tool_id: str):
        """记录成功"""
        self.failures[tool_id] = 0
        self.state[tool_id] = 'closed'
    
    def can_execute(self, tool_id: str) -> bool:
        """检查是否可以执行"""
        state = self.state.get(tool_id, 'closed')
        
        if state == 'closed':
            return True
        
        if state == 'open':
            # 尝试半开
            self.state[tool_id] = 'half-open'
            return True
        
        return True


# ==================== 动态加载器 ====================

class ToolLoader:
    """工具动态加载器"""
    
    def __init__(self):
        self.loaded_tools: Dict[str, Any] = {}
    
    def load(self, tool: Tool) -> bool:
        """加载工具"""
        try:
            # 模拟工具加载
            self.loaded_tools[tool.tool_id] = {
                'tool': tool,
                'loaded_at': time.time(),
                'status': 'loaded'
            }
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False
    
    def unload(self, tool_id: str) -> bool:
        """卸载工具"""
        if tool_id in self.loaded_tools:
            del self.loaded_tools[tool_id]
            return True
        return False
    
    def is_loaded(self, tool_id: str) -> bool:
        """检查是否已加载"""
        return tool_id in self.loaded_tools


# ==================== MCP工具自动化系统 ====================

class MCPToolAutomationSystem:
    """MCP工具自动化系统"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.adapter_manager = AdapterManager()
        self.circuit_breaker = CircuitBreaker()
        self.loader = ToolLoader()
        self.call_history: List[Dict] = []
        self.subagent_tasks: List[Dict] = []
    
    def discover_tools(self) -> List[Tool]:
        """发现工具"""
        return self.registry.discover_mcp_tools()
    
    def connect_tool(self, tool_id: str) -> Dict:
        """连接工具"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        tool.status = ToolStatus.CONNECTING
        
        # 获取适配器
        adapter = self.adapter_manager.get_adapter(tool.tool_type)
        if not adapter:
            tool.status = ToolStatus.ERROR
            return {'success': False, 'error': 'No adapter'}
        
        # 健康检查
        if adapter.health_check(tool):
            tool.status = ToolStatus.CONNECTED
            self.circuit_breaker.record_success(tool_id)
            
            # 加载工具
            self.loader.load(tool)
            
            return {'success': True, 'tool_id': tool_id, 'status': 'connected'}
        else:
            tool.status = ToolStatus.ERROR
            return {'success': False, 'error': 'Health check failed'}
    
    def execute_tool(self, tool_id: str, action: str, params: Dict = None) -> Dict:
        """执行工具"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        # 检查熔断
        if not self.circuit_breaker.can_execute(tool_id):
            # 尝试备用工具
            return self._try_fallback(tool, action, params or {})
        
        # 获取适配器
        adapter = self.adapter_manager.get_adapter(tool.tool_type)
        if not adapter:
            return {'success': False, 'error': 'No adapter'}
        
        # 执行
        start_time = time.time()
        result = adapter.execute(tool, action, params or {})
        elapsed = (time.time() - start_time) * 1000
        
        # 更新熔断状态
        if result.get('success'):
            self.circuit_breaker.record_success(tool_id)
            tool.consecutive_failures = 0
        else:
            should_break = self.circuit_breaker.record_failure(tool_id)
            tool.consecutive_failures += 1
            
            if should_break:
                tool.status = ToolStatus.ERROR
        
        # 记录历史
        self.call_history.append({
            'tool_id': tool_id,
            'action': action,
            'params': params,
            'result': result,
            'elapsed_ms': elapsed,
            'timestamp': time.time()
        })
        
        return result
    
    def _try_fallback(self, tool: Tool, action: str, params: Dict) -> Dict:
        """尝试备用工具"""
        # 查找同类型其他可用工具
        similar_tools = self.registry.list_tools(
            status=ToolStatus.CONNECTED,
            tool_type=tool.tool_type
        )
        
        for fallback in similar_tools:
            if fallback.tool_id != tool.tool_id:
                return self.execute_tool(fallback.tool_id, action, params)
        
        return {'success': False, 'error': 'No fallback available'}
    
    def disconnect_tool(self, tool_id: str) -> Dict:
        """断开工具"""
        tool = self.registry.get_tool(tool_id)
        if tool:
            tool.status = ToolStatus.DISCONNECTED
            self.loader.unload(tool_id)
            return {'success': True}
        return {'success': False, 'error': 'Tool not found'}
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'total_tools': len(self.registry.tools),
            'connected': len(self.registry.list_tools(ToolStatus.CONNECTED)),
            'active': len(self.registry.list_tools(ToolStatus.ACTIVE)),
            'errors': len(self.registry.list_tools(ToolStatus.ERROR)),
            'loaded': len(self.loader.loaded_tools),
            'call_history': len(self.call_history)
        }


# ==================== SubAgent协作 ====================

class SubAgentToolCoordinator:
    """SubAgent工具协调器"""
    
    def __init__(self):
        self.tasks: List[Dict] = []
        self.agents = {
            'mcp-discover': {'capability': 'discover', 'status': 'idle'},
            'mcp-execute': {'capability': 'execute', 'status': 'idle'},
            'tool-monitor': {'capability': 'monitor', 'status': 'idle'},
            'tool-repair': {'capability': 'repair', 'status': 'idle'},
        }
    
    def coordinate(self, agent_type: str, task: Dict) -> Dict:
        """协调SubAgent"""
        if agent_type not in self.agents:
            return {'success': False, 'error': 'Unknown agent'}
        
        agent = self.agents[agent_type]
        agent['status'] = 'working'
        
        # 记录任务
        task_record = {
            'agent': agent_type,
            'task': task,
            'timestamp': time.time()
        }
        self.tasks.append(task_record)
        
        # 模拟执行
        result = {
            'success': True,
            'agent': agent_type,
            'task_id': len(self.tasks),
            'timestamp': time.time()
        }
        
        agent['status'] = 'idle'
        return result
    
    def get_agents_status(self) -> Dict:
        """获取Agent状态"""
        return self.agents.copy()


# ==================== 导出 ====================

def get_mcp_tool_system() -> MCPToolAutomationSystem:
    """获取MCP工具系统"""
    return MCPToolAutomationSystem()


def get_subagent_coordinator() -> SubAgentToolCoordinator:
    """获取SubAgent协调器"""
    return SubAgentToolCoordinator()


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("MCP Tool Automation System Test")
    print("="*60)
    
    # 创建系统
    system = get_mcp_tool_system()
    
    # 发现工具
    print("\n--- Discover Tools ---")
    tools = system.discover_tools()
    print(f"Found {len(tools)} tools")
    for t in tools:
        print(f"  - {t.name} ({t.tool_type.value})")
    
    # SubAgent协调
    print("\n--- SubAgent Coordination ---")
    coordinator = get_subagent_coordinator()
    agents = coordinator.get_agents_status()
    for agent_type, info in agents.items():
        print(f"  - {agent_type}: {info['status']}")
    
    # 测试任务分发
    print("\n--- Coordinate Task ---")
    result = coordinator.coordinate('mcp-discover', {'action': 'scan'})
    print(f"Result: {result}")
    
    # 系统状态
    print("\n--- System Status ---")
    status = system.get_status()
    print(f"Total Tools: {status['total_tools']}")
    print(f"Connected: {status['connected']}")
    print(f"Loaded: {status['loaded']}")
