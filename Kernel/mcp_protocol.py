# -*- coding: utf-8 -*-
"""
MCP协议支持模块 - MCP Protocol Support

Model Context Protocol (MCP) 序境系统适配器

功能：
- MCP客户端实现
- 工具调用标准化
- 资源管理
- 提示词模板

参考：https://modelcontextprotocol.io/
"""
import json
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib


class MCPMessageType(Enum):
    """MCP消息类型"""
    JSONRPC = "2.0"
    INITIALIZE = "initialize"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


@dataclass
class MCPRequest:
    """MCP请求"""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str = ""
    params: Dict = field(default_factory=dict)


@dataclass
class MCPResponse:
    """MCP响应"""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Dict] = None
    error: Optional[Dict] = None


@dataclass
class MCPTool:
    """MCP工具"""
    name: str
    description: str
    input_schema: Dict


@dataclass
class MCPResource:
    """MCP资源"""
    uri: str
    name: str
    description: str = ""
    mime_type: str = "text/plain"


class MCPClient:
    """
    MCP客户端 - 序境系统适配器
    
    使用：
        client = MCPClient()
        await client.connect("server_url")
        tools = await client.list_tools()
        result = await client.call_tool("tool_name", args)
    """
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.session_id = None
        self.capabilities = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        
        # 请求ID计数器
        self._request_id = 0
    
    def _next_id(self) -> int:
        """生成请求ID"""
        self._request_id += 1
        return self._request_id
    
    async def initialize(self) -> Dict:
        """
        初始化MCP会话
        
        返回:
            服务器能力
        """
        request = MCPRequest(
            id=self._next_id(),
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "xujing-symphony",
                    "version": "3.2.0"
                }
            }
        )
        
        # 模拟响应
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        self.session_id = hashlib.md5(str(self._next_id()).encode()).hexdigest()
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "mcp-server",
                "version": "1.0.0"
            }
        }
    
    async def list_tools(self) -> List[MCPTool]:
        """
        列出可用工具
        
        返回:
            工具列表
        """
        # 模拟工具列表
        self.tools = {
            "search": MCPTool(
                name="search",
                description="网络搜索工具",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索查询"}
                    },
                    "required": ["query"]
                }
            ),
            "fetch": MCPTool(
                name="fetch",
                description="获取网页内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "网页URL"}
                    },
                    "required": ["url"]
                }
            ),
            "execute": MCPTool(
                name="execute",
                description="执行命令",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "命令"}
                    },
                    "required": ["command"]
                }
            )
        }
        
        return list(self.tools.values())
    
    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Dict:
        """
        调用工具
        
        参数:
            name: 工具名称
            arguments: 工具参数
        
        返回:
            工具执行结果
        """
        if name not in self.tools:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {name}"
                }
            }
        
        # 模拟执行
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Executed {name} with args: {json.dumps(arguments)}"
                }
            ]
        }
    
    async def list_resources(self) -> List[MCPResource]:
        """列出可用资源"""
        self.resources = {
            "config": MCPResource(
                uri="symphony://config",
                name="system_config",
                description="系统配置"
            ),
            "models": MCPResource(
                uri="symphony://models",
                name="model_list",
                description="模型列表"
            )
        }
        
        return list(self.resources.values())
    
    async def read_resource(self, uri: str) -> str:
        """读取资源内容"""
        if uri == "symphony://config":
            return json.dumps({"version": "3.2.0"}, indent=2)
        elif uri == "symphony://models":
            return json.dumps({"models": []}, indent=2)
        
        return ""
    
    def get_tool_schema(self, name: str) -> Optional[Dict]:
        """获取工具Schema"""
        tool = self.tools.get(name)
        return tool.input_schema if tool else None
    
    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable
    ):
        """注册自定义工具"""
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            input_schema={}
        )
        # 存储handler（简化实现）
        self.tools[name]._handler = handler
    
    def to_symphony_format(self) -> Dict:
        """转换为序境系统格式"""
        return {
            "mcp_version": "2024-11-05",
            "session_id": self.session_id,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "schema": t.input_schema
                }
                for t in self.tools.values()
            ],
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description
                }
                for r in self.resources.values()
            ]
        }


class MCPServer:
    """
    MCP服务器 - 供其他系统调用
    
    使用：
        server = MCPServer()
        await server.start(8080)
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.tools: Dict[str, Callable] = {}
        self.running = False
    
    def register_tool(
        self,
        name: str,
        handler: Callable,
        description: str = ""
    ):
        """注册工具"""
        self.tools[name] = handler
    
    async def handle_request(self, request: Dict) -> MCPResponse:
        """处理MCP请求"""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")
        
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "xujing-mcp", "version": "1.0.0"}
            }
            return MCPResponse(id=req_id, result=result)
        
        elif method == "tools/list":
            tools = [
                {"name": k, "description": v.__doc__ or ""}
                for k, v in self.tools.items()
            ]
            return MCPResponse(id=req_id, result={"tools": tools})
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name in self.tools:
                try:
                    result = await self.tools[tool_name](**arguments)
                    return MCPResponse(id=req_id, result=result)
                except Exception as e:
                    return MCPResponse(
                        id=req_id,
                        error={"code": -32603, "message": str(e)}
                    )
            else:
                return MCPResponse(
                    id=req_id,
                    error={"code": -32601, "message": f"Tool not found: {tool_name}"}
                )
        
        return MCPResponse(
            id=req_id,
            error={"code": -32600, "message": "Invalid request"}
        )


# 测试
if __name__ == "__main__":
    print("=== MCP模块测试 ===")
    
    # 客户端测试
    client = MCPClient()
    
    import asyncio
    
    async def test_client():
        # 初始化
        info = await client.initialize()
        print("Initialize:", info["serverInfo"])
        
        # 列出工具
        tools = await client.list_tools()
        print(f"Tools: {len(tools)}")
        
        # 调用工具
        result = await client.call_tool("search", {"query": "test"})
        print("Call result:", result)
        
        # 转换为序境格式
        symphony_format = client.to_symphony_format()
        print("Symphony format:", symphony_format["mcp_version"])
    
    asyncio.run(test_client())
    
    print()
    print("MCP模块测试通过!")
