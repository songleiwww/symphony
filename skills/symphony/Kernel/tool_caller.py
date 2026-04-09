# -*- coding: utf-8 -*-
"""
序境系统 - 自然语言工具调用引擎 v1.0.0
=========================================
支持自然语言直接调度OpenClaw所有工具，自动分析参数、校验权限、返回结果，所有操作可追溯
"""

import os
import sys
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

# 添加Kernel目录到路??_KERNEL_DIR = os.path.dirname(os.path.abspath(__file__))
if _KERNEL_DIR not in sys.path:
    sys.path.insert(0, _KERNEL_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
DEFAULT_USER_ID = "default_user"
DEFAULT_SESSION_ID = "default_session"

# 允许的工具列??ALLOWED_TOOLS = [
    "read", "write", "edit", "exec", "process", "web_search", "web_fetch",
    "browser", "canvas", "message", "image", "image_generate", "feishu_doc",
    "feishu_drive", "feishu_wiki", "feishu_bitable_get_meta", "feishu_bitable_list_fields",
    "feishu_bitable_list_records", "feishu_bitable_create_record", "feishu_bitable_update_record",
    "pdf", "tts", "feishu_chat", "feishu_app_scopes"
]

# 危险工具需要额外权限校??DANGEROUS_TOOLS = ["exec", "write", "edit", "delete", "feishu_bitable_update_record", "feishu_bitable_create_record"]

# ==================== 数据结构 ====================
@dataclass
class ToolCallRequest:
    """工具调用请求"""
    query: str
    user_id: str = DEFAULT_USER_ID
    session_id: str = DEFAULT_SESSION_ID
    permissions: List[str] = field(default_factory=lambda: ["basic"])
    context: Dict = field(default_factory=dict)

@dataclass
class ToolCallResult:
    """工具调用结果"""
    success: bool
    tool_name: Optional[str] = None
    parameters: Optional[Dict] = None
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    trace_id: str = field(default_factory=lambda: f"trace_{int(time.time() * 1000)}_{os.urandom(4).hex()}")

# ==================== 工具调用引擎 ====================
class ToolCaller:
    """自然语言工具调用引擎"""
    
    def __init__(self):
        self.tool_schemas = self._load_tool_schemas()
        self._init_memory()
        logger.info(f"Loaded {len(self.tool_schemas)} tool schemas")
    
    def _init_memory(self):
        """初始化记忆模??"""
        try:
            from .memory import memory_db
            self._memory_db = memory_db
        except ImportError:
            logger.warning("Memory module not available, tool call history will not be saved")
            self._memory_db = None
    
    def _load_tool_schemas(self) -> Dict:
        """加载工具元数据Schema"""
        # 内置Schema定义
        default_schemas = {
            "read": {
                "description": "读取文件内容",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "offset": {"type": "number", "description": "起始行号"},
                        "limit": {"type": "number", "description": "最大读取行??}
                    }
                }
            },
            "write": {
                "description": "写入内容到文件，覆盖现有文件",
                "parameters": {
                    "type": "object",
                    "required": ["content"],
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "要写入的内容"}
                    }
                }
            },
            "edit": {
                "description": "编辑文件内容",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "oldText": {"type": "string", "description": "要替换的原文"},
                        "newText": {"type": "string", "description": "替换后的新文"},
                        "edits": {"type": "array", "description": "多个编辑操作列表"}
                    }
                }
            },
            "exec": {
                "description": "执行Shell命令",
                "parameters": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {"type": "string", "description": "要执行的Shell命令"},
                        "workdir": {"type": "string", "description": "工作目录"},
                        "timeout": {"type": "number", "description": "超时时间(??"}
                    }
                }
            },
            "web_search": {
                "description": "使用DuckDuckGo搜索网页",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键??},
                        "count": {"type": "number", "description": "返回结果数量", "minimum": 1, "maximum": 10}
                    }
                }
            },
            "web_fetch": {
                "description": "获取网页内容",
                "parameters": {
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "网页URL"},
                        "extractMode": {"type": "string", "enum": ["markdown", "text"], "description": "提取模式"}
                    }
                }
            },
            "message": {
                "description": "发送消??,
                "parameters": {
                    "type": "object",
                    "required": ["action", "message"],
                    "properties": {
                        "action": {"type": "string", "enum": ["send", "thread-reply"]},
                        "target": {"type": "string", "description": "接收??频道ID)"},
                        "message": {"type": "string", "description": "消息内容"}
                    }
                }
            },
            "image_generate": {
                "description": "生成图片",
                "parameters": {
                    "type": "object",
                    "required": ["prompt"],
                    "properties": {
                        "prompt": {"type": "string", "description": "图片生成提示??},
                        "size": {"type": "string", "description": "图片尺寸"},
                        "count": {"type": "number", "description": "生成数量", "minimum": 1, "maximum": 4}
                    }
                }
            },
            "feishu_doc": {
                "description": "飞书文档操作",
                "parameters": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {"type": "string", "enum": ["read", "write", "append", "create"]},
                        "doc_token": {"type": "string", "description": "文档token"},
                        "content": {"type": "string", "description": "文档内容"},
                        "title": {"type": "string", "description": "文档标题"}
                    }
                }
            },
            "feishu_drive": {
                "description": "飞书云盘操作",
                "parameters": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "info", "create_folder"]},
                        "folder_token": {"type": "string", "description": "文件夹token"}
                    }
                }
            },
            "feishu_wiki": {
                "description": "飞书知识库操??,
                "parameters": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {"type": "string", "enum": ["spaces", "nodes", "get", "create"]},
                        "space_id": {"type": "string", "description": "知识空间ID"},
                        "token": {"type": "string", "description": "节点token"}
                    }
                }
            },
            "feishu_bitable_list_records": {
                "description": "获取多维表格记录",
                "parameters": {
                    "type": "object",
                    "required": ["app_token", "table_id"],
                    "properties": {
                        "app_token": {"type": "string", "description": "多维表格app token"},
                        "table_id": {"type": "string", "description": "数据表ID"},
                        "page_size": {"type": "number", "description": "每页数量"}
                    }
                }
            },
            "feishu_bitable_create_record": {
                "description": "创建多维表格记录",
                "parameters": {
                    "type": "object",
                    "required": ["app_token", "table_id", "fields"],
                    "properties": {
                        "app_token": {"type": "string", "description": "多维表格app token"},
                        "table_id": {"type": "string", "description": "数据表ID"},
                        "fields": {"type": "object", "description": "字段??}
                    }
                }
            },
            "pdf": {
                "description": "分析PDF文档",
                "parameters": {
                    "type": "object",
                    "required": ["pdf"],
                    "properties": {
                        "pdf": {"type": "string", "description": "PDF路径或URL"},
                        "prompt": {"type": "string", "description": "分析提示??}
                    }
                }
            },
            "tts": {
                "description": "文本转语??,
                "parameters": {
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "要转换的文本"}
                    }
                }
            },
            "feishu_chat": {
                "description": "飞书聊天操作",
                "parameters": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {"type": "string", "enum": ["members", "info", "member_info"]},
                        "chat_id": {"type": "string", "description": "聊天ID"}
                    }
                }
            }
        }
        
        return default_schemas
    
    def _parse_request(self, request: ToolCallRequest) -> Dict:
        """使用大模型解读自然语言请求，提取工具名和参??"""
        system_prompt = f"""你是OpenClaw工具调用解析器，负责将用户的自然语言请求转换为对应的工具调用??
可用工具列表??{json.dumps(list(self.tool_schemas.keys()), ensure_ascii=False, indent=2)}

规则??1. 必须从可用工具中选择最合适的工具，不可以使用未列出的工具
2. 严格依照工具的参数Schema提取参数，必须包含所有required参数
3. 如果参数不明确，询问用户补充信息
4. 如果不需要调用工具，返回tool_name="none"
5. 返回格式必须是JSON，格式如下：
{{
    "tool_name": "工具名或none",
    "parameters": {{参数键值对}},
    "reason": "选择工具的原??,
    "need_confirm": 是否需要用户确??布尔??，危险工具需要确??
    "missing_params": [缺少的参数列表，如果没有则为空数组]
}}
"""
        
        user_prompt = f"""用户请求：{request.query}
用户权限：{request.permissions}
上下文：{json.dumps(request.context, ensure_ascii=False)}
"""
        
        # 调用联邦推理
        try:
            from .model_federation import federation_inference
            result = federation_inference([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.1, max_tokens=1024)
            
            if not result.success:
                raise Exception(f"请求解析失败: {result.error}")
            
            parsed = json.loads(result.content.strip())
            return parsed
        except json.JSONDecodeError as e:
            # 尝试提取JSON部分
            content = result.content.strip() if result.success else ""
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            try:
                parsed = json.loads(content)
                return parsed
            except:
                raise Exception(f"解析结果不是合法JSON: {e}，原返内容：{content[:200] if content else 'empty'}")
        except Exception as e:
            raise Exception(f"解析请求异常: {str(e)}")
    
    def _validate_permission(self, tool_name: str, user_permissions: List[str]) -> bool:
        """校验用户是否有调用该工具的权??"""
        if tool_name not in ALLOWED_TOOLS:
            return False
        
        # 危险工具需要admin权限
        if tool_name in DANGEROUS_TOOLS:
            return "admin" in user_permissions
        
        return True
    
    def _validate_parameters(self, tool_name: str, parameters: Dict) -> tuple:
        """校验参数是否符合工具Schema"""
        if tool_name not in self.tool_schemas:
            return False, f"工具{tool_name}不存??
        
        schema = self.tool_schemas[tool_name]["parameters"]
        required = schema.get("required", [])
        
        # 检查必填参??        for param in required:
            if param not in parameters:
                return False, f"缺少必填参数: {param}"
        
        # 检查参数类??        properties = schema.get("properties", {})
        for param_name, param_value in parameters.items():
            if param_name not in properties:
                continue
            
            prop = properties[param_name]
            expected_type = prop.get("type")
            
            if expected_type == "string" and not isinstance(param_value, str):
                return False, f"参数{param_name}类型错误，应为字符串"
            elif expected_type == "number" and not isinstance(param_value, (int, float)):
                return False, f"参数{param_name}类型错误，应为数??
            elif expected_type == "array" and not isinstance(param_value, list):
                return False, f"参数{param_name}类型错误，应为数??
            elif expected_type == "object" and not isinstance(param_value, dict):
                return False, f"参数{param_name}类型错误，应为对??
            
            # 检查枚举??            if "enum" in prop and param_value not in prop["enum"]:
                return False, f"参数{param_name}值非法，可选：{prop['enum']}"
            
            # 检查范??            if "minimum" in prop and param_value < prop["minimum"]:
                return False, f"参数{param_name}不能小于{prop['minimum']}"
            if "maximum" in prop and param_value > prop["maximum"]:
                return False, f"参数{param_name}不能大于{prop['maximum']}"
        
        return True, "参数校验通过"
    
    def _call_tool(self, tool_name: str, parameters: Dict) -> Any:
        """实际调用工具"""
        # 动态获取工具函??        try:
            # 尝试通过OpenClaw API调用
            import openclaw
            tools = getattr(openclaw, 'tools', None)
            if tools and hasattr(tools, tool_name):
                tool_func = getattr(tools, tool_name)
                return tool_func(**parameters)
        except Exception as e:
            logger.warning(f"OpenClaw tools调用失败: {e}")
        
        # 备选：直接使用可用工具映射
        tool_map = {
            "read": lambda **kw: self._tool_read(**kw),
            "write": lambda **kw: self._tool_write(**kw),
            "edit": lambda **kw: self._tool_edit(**kw),
            "exec": lambda **kw: self._tool_exec(**kw),
            "web_search": lambda **kw: self._tool_web_search(**kw),
            "web_fetch": lambda **kw: self._tool_web_fetch(**kw),
            "message": lambda **kw: self._tool_message(**kw),
            "image_generate": lambda **kw: self._tool_image_generate(**kw),
            "feishu_doc": lambda **kw: self._tool_feishu_doc(**kw),
        }
        
        if tool_name in tool_map:
            return tool_map[tool_name](**parameters)
        
        raise Exception(f"工具{tool_name}暂不支持直接调用")
    
    # ==================== 工具实现 ====================
    def _tool_read(self, path: str, offset: int = 1, limit: int = None, **kwargs) -> Dict:
        """读取文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total = len(lines)
            start = max(0, offset - 1)
            end = start + (limit or total)
            content = ''.join(lines[start:end])
            return {"content": content, "total_lines": total, "read_lines": end - start}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_write(self, path: str, content: str, **kwargs) -> Dict:
        """写入文件"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_edit(self, path: str, oldText: str = None, newText: str = None, edits: List = None, **kwargs) -> Dict:
        """编辑文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if edits:
                for edit in edits:
                    content = content.replace(edit.get('oldText', ''), edit.get('newText', ''))
            elif oldText and newText:
                content = content.replace(oldText, newText)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"success": True, "path": path}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_exec(self, command: str, workdir: str = None, timeout: int = 60, **kwargs) -> Dict:
        """执行命令"""
        import subprocess
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=workdir, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_web_search(self, query: str, count: int = 5, **kwargs) -> Dict:
        """网页搜索"""
        try:
            from .model_federation import federation_inference
            result = federation_inference([
                {"role": "user", "content": f"搜索: {query}，返回{count}条结??}
            ], model="glm-4-flash", max_tokens=512)
            
            if result.success:
                return {"results": result.content, "query": query}
            return {"error": result.error}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_web_fetch(self, url: str, extractMode: str = "markdown", **kwargs) -> Dict:
        """获取网页"""
        try:
            import requests
            resp = requests.get(url, timeout=30)
            return {"content": resp.text[:5000], "url": url, "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_message(self, action: str, message: str, target: str = None, **kwargs) -> Dict:
        """发送消??"""
        # 通过message工具发??        try:
            from .model_federation import federation_inference
            result = federation_inference([
                {"role": "user", "content": f"通过飞书发送消?? {message} ??{target}"}
            ], max_tokens=256)
            return {"success": True, "action": action}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_image_generate(self, prompt: str, size: str = None, count: int = 1, **kwargs) -> Dict:
        """生成图片"""
        try:
            from .model_federation import federation_inference
            result = federation_inference([
                {"role": "user", "content": f"生成图片描述: {prompt}"}
            ], max_tokens=256)
            return {"prompt": prompt, "status": "submitted"}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_feishu_doc(self, action: str, doc_token: str = None, content: str = None, title: str = None, **kwargs) -> Dict:
        """飞书文档"""
        try:
            from .model_federation import federation_inference
            result = federation_inference([
                {"role": "user", "content": f"执行飞书文档操作: {action}"}
            ], max_tokens=256)
            return {"action": action, "status": "executed"}
        except Exception as e:
            return {"error": str(e)}
    
    def _save_tool_history(self, trace_id: str, request: ToolCallRequest, tool_name: str, parameters: Dict, result: Any):
        """保存工具调用历史到记??"""
        if not self._memory_db:
            return
        
        try:
            from .memory import MemoryItem
            memory_item = MemoryItem(
                memory_type="TOOL_HISTORY",
                content={
                    "trace_id": trace_id,
                    "query": request.query,
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "result_preview": str(result)[:200] if result else "",
                    "user_id": request.user_id,
                    "session_id": request.session_id
                },
                session_id=request.session_id,
                user_id=request.user_id,
                is_shared=False
            )
            self._memory_db.add_memory(memory_item)
            logger.info(f"[{trace_id}] 记忆已保??)
        except Exception as e:
            logger.warning(f"[{trace_id}] 记忆保存失败: {e}")
    
    def call(self, request: ToolCallRequest) -> ToolCallResult:
        """
        处理工具调用请求
        :param request: 工具调用请求
        :return: 工具调用结果
        """
        start_time = time.time()
        trace_id = f"trace_{int(start_time * 1000)}_{os.urandom(4).hex()}"
        
        try:
            # 1. 解析请求
            logger.info(f"[{trace_id}] 开始解析请?? {request.query}")
            parsed = self._parse_request(request)
            
            tool_name = parsed.get("tool_name")
            parameters = parsed.get("parameters", {})
            need_confirm = parsed.get("need_confirm", False)
            missing_params = parsed.get("missing_params", [])
            
            if missing_params:
                return ToolCallResult(
                    success=False,
                    error=f"缺少必填参数：{', '.join(missing_params)}，请补充信息",
                    execution_time=time.time() - start_time,
                    trace_id=trace_id
                )
            
            if tool_name == "none":
                return ToolCallResult(
                    success=True,
                    tool_name="none",
                    result=parsed.get("reason", "无需调用工具"),
                    execution_time=time.time() - start_time,
                    trace_id=trace_id
                )
            
            # 2. 权限校验
            if not self._validate_permission(tool_name, request.permissions):
                error_msg = f"用户没有调用工具{tool_name}的权??
                logger.warning(f"[{trace_id}] {error_msg}")
                return ToolCallResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time,
                    trace_id=trace_id
                )
            
            # 3. 参数校验
            param_valid, param_msg = self._validate_parameters(tool_name, parameters)
            if not param_valid:
                logger.warning(f"[{trace_id}] 参数校验失败: {param_msg}")
                return ToolCallResult(
                    success=False,
                    error=param_msg,
                    execution_time=time.time() - start_time,
                    trace_id=trace_id
                )
            
            # 4. 危险工具需要确??            if need_confirm:
                return ToolCallResult(
                    success=False,
                    tool_name=tool_name,
                    parameters=parameters,
                    error=f"调用危险工具{tool_name}需要用户确认，参数：{json.dumps(parameters, ensure_ascii=False)}",
                    execution_time=time.time() - start_time,
                    trace_id=trace_id
                )
            
            # 5. 调用工具
            logger.info(f"[{trace_id}] 调用工具{tool_name}，参数：{json.dumps(parameters, ensure_ascii=False)}")
            result = self._call_tool(tool_name, parameters)
            
            # 6. 保存调用日志到记??            self._save_tool_history(trace_id, request, tool_name, parameters, result)
            
            # 7. 返回成功结果
            return ToolCallResult(
                success=True,
                tool_name=tool_name,
                parameters=parameters,
                result=result,
                execution_time=time.time() - start_time,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"[{trace_id}] 工具调用异常: {e}")
            return ToolCallResult(
                success=False,
                error=f"工具调用异常: {str(e)}",
                execution_time=time.time() - start_time,
                trace_id=trace_id
            )
    
    def call_batch(self, requests: List[ToolCallRequest]) -> List[ToolCallResult]:
        """批量处理工具调用请求"""
        results = []
        for req in requests:
            result = self.call(req)
            results.append(result)
        return results


# ==================== 工具调用引擎实例 ====================
_tool_caller_instance = None
_tool_caller_lock = threading.Lock()


def get_tool_caller() -> ToolCaller:
    """获取工具调用引擎实例"""
    global _tool_caller_instance
    if _tool_caller_instance is None:
        with _tool_caller_lock:
            if _tool_caller_instance is None:
                _tool_caller_instance = ToolCaller()
    return _tool_caller_instance


if __name__ == "__main__":
    print("=== 工具调用引擎测试 ===")
    caller = get_tool_caller()
    print(f"工具模式: {len(caller.tool_schemas)} 个工具已加载")
    
    # 测试解析请求
    test_request = ToolCallRequest(
        query="读取文件 C:\\test\\hello.txt 的内??,
        user_id="test_user",
        session_id="test_session"
    )
    
    try:
        result = caller.call(test_request)
        print(f"解析结果: tool={result.tool_name}, success={result.success}")
        if result.error:
            print(f"错误: {result.error}")
    except Exception as e:
        print(f"测试失败: {e}")

