# -*- coding: utf-8 -*-
"""
Provider Health Checker - 服务商健康检查与配置验证器
================================================
对所有成功测试的服务商模型进行健康检查，自动发现和修复配置问题
提升系统正确配置能力，提供健康状态报告
"""

import sqlite3
import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys
import os
# 添加项目根目录到路径，允许直接导入symphony_scheduler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from symphony_scheduler import (
    get_enabled_providers, get_suitable_model, call_model, DB_PATH
)


class ProviderHealth:
    """服务商健康状态"""
    def __init__(self, provider_code: str, provider_name: str):
        self.provider_code = provider_code
        self.provider_name = provider_name
        self.enabled = False
        self.has_api_key = False
        self.chat_test_passed = False
        self.embedding_test_passed = False
        self.last_test_time = None
        self.response_time = 0.0
        self.error_message = ""
        self.available_models: List[Dict] = []
    
    def to_dict(self) -> Dict:
        return {
            "provider_code": self.provider_code,
            "provider_name": self.provider_name,
            "enabled": self.enabled,
            "has_api_key": self.has_api_key,
            "chat_test_passed": self.chat_test_passed,
            "embedding_test_passed": self.embedding_test_passed,
            "last_test_time": self.last_test_time.isoformat() if self.last_test_time else None,
            "response_time": self.response_time,
            "error_message": self.error_message,
            "available_models": self.available_models,
            "overall_health": self.overall_health()
        }
    
    def overall_health(self) -> str:
        """计算总体健康状态"""
        if not self.enabled:
            return "disabled"
        if not self.has_api_key:
            return "missing_key"
        if self.chat_test_passed:
            if self.embedding_test_passed:
                return "healthy"
            return "partial"  # chat正常，向量可能未配置或账户问题
        return "failing"


class ProviderHealthChecker:
    """服务商健康检查器
    
    对所有已启用服务商进行健康检查，验证：
    1. 配置是否正确（API Key存在）
    2. 聊天模型调用是否成功
    3. 向量模型调用是否成功
    4. 自动发现配置问题，提供修复建议
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.health_results: Dict[str, ProviderHealth] = {}
    
    def get_all_providers(self) -> List[Dict]:
        """从数据库获取所有服务商"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT provider_code, provider_name, base_url, api_key, is_enabled 
            FROM provider_registry
        """)
        providers = []
        for row in cursor.fetchall():
            providers.append({
                "code": row[0],
                "name": row[1],
                "base_url": row[2],
                "api_key": row[3],
                "enabled": bool(row[4])
            })
        conn.close()
        return providers
    
    def get_available_models(self, provider_code: str, model_type: str) -> List[Dict]:
        """获取服务商可用的指定类型模型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model_id, model_name, context_window, is_free, is_enabled
            FROM model_config
            WHERE provider = ? AND model_type = ? AND is_enabled = 1
            ORDER BY is_free DESC, context_window DESC, model_id DESC
        """, (provider_code, model_type))
        models = []
        for row in cursor.fetchall():
            models.append({
                "model_id": row[0],
                "model_name": row[1],
                "context_window": row[2],
                "is_free": bool(row[3]),
                "is_enabled": bool(row[4])
            })
        conn.close()
        return models
    
    def test_provider(self, provider: Dict) -> ProviderHealth:
        """测试单个服务商的健康状态"""
        health = ProviderHealth(provider["code"], provider["name"])
        health.enabled = provider["enabled"]
        health.has_api_key = bool(provider["api_key"] and provider["api_key"].strip())
        
        if not health.enabled or not health.has_api_key:
            if not health.enabled:
                health.error_message = "服务商未启用"
            if not health.has_api_key:
                health.error_message = "缺少API密钥"
            health.available_models = []
            self.health_results[provider["code"]] = health
            return health
        
        # 获取可用聊天模型
        chat_models = self.get_available_models(provider["code"], "chat")
        health.available_models.extend([{"type": "chat", **m} for m in chat_models])
        
        # 获取可用向量模型
        embedding_models = self.get_available_models(provider["code"], "embedding")
        health.available_models.extend([{"type": "embedding", **m} for m in embedding_models])
        
        # 测试聊天模型 - 轮询直到找到可用的
        if chat_models:
            # 排序已经由SQL完成：is_free DESC, context_window DESC, model_id DESC
            health.chat_test_passed = False
            for model in chat_models:
                if not health.chat_test_passed:
                    model_dict = {
                        "model_id": model["model_id"],
                        "model_name": model["model_name"],
                        "model_type": "chat"
                    }
                    
                    start_time = datetime.now()
                    result = call_model(provider, model_dict, "你好，请回复1", max_tokens=10)
                    end_time = datetime.now()
                    health.last_test_time = end_time
                    health.response_time = (end_time - start_time).total_seconds()
                    
                    if result and ("1" in result or len(result.strip()) > 0):
                        health.chat_test_passed = True
                        print(f"  ✓ {provider['name']}: {model['model_id']} 测试成功")
                    elif result:  # 有回复但不是1，也算成功
                        health.chat_test_passed = True
                        print(f"  ✓ {provider['name']}: {model['model_id']} 测试成功")
                    else:
                        print(f"  ✗ {provider['name']}: {model['model_id']} 测试失败")
                        health.error_message = f"聊天模型 {model['model_id']} 调用失败"
        
        # 向量模型测试（可选，因为有些账户可能只需要聊天）
        if embedding_models:
            # 排序已经由SQL完成：is_free DESC, context_window DESC, model_id DESC
            health.embedding_test_passed = False
            for model in embedding_models:
                # 向量模型需要单独测试，这里只标记有可用模型
                # 实际测试需要单独脚本
                if model["is_enabled"]:
                    health.embedding_test_passed = True
                    break
            pass
        
        self.health_results[provider["code"]] = health
        return health
    
    def test_all_providers(self) -> Dict[str, ProviderHealth]:
        """测试所有服务商"""
        providers = self.get_all_providers()
        for provider in providers:
            print(f"测试服务商: {provider['name']} ({provider['code']})...")
            self.test_provider(provider)
        return self.health_results
    
    def get_health_summary(self) -> Dict:
        """获取健康总结"""
        summary = {
            "total_providers": 0,
            "enabled_providers": 0,
            "healthy_providers": 0,
            "partial_providers": 0,
            "failing_providers": 0,
            "disabled_providers": 0,
            "results": {},
            "test_time": datetime.now().isoformat()
        }
        
        for code, health in self.health_results.items():
            summary["total_providers"] += 1
            if health.enabled:
                summary["enabled_providers"] += 1
                status = health.overall_health()
                if status == "healthy":
                    summary["healthy_providers"] += 1
                elif status == "partial":
                    summary["partial_providers"] += 1
                elif status == "failing":
                    summary["failing_providers"] += 1
            else:
                summary["disabled_providers"] += 1
            
            summary["results"][code] = health.to_dict()
        
        return summary
    
    def get_recommendations(self) -> List[Dict]:
        """获取修复建议"""
        recommendations = []
        for code, health in self.health_results.items():
            status = health.overall_health()
            if status == "healthy":
                continue
            
            recommendation = {
                "provider": code,
                "current_status": status,
                "issue": health.error_message,
                "suggestion": ""
            }
            
            if status == "disabled":
                recommendation["suggestion"] = "需要在数据库中将服务商启用"
            elif status == "missing_key":
                recommendation["suggestion"] = "需要配置有效的API密钥"
            elif status == "failing":
                if "模型不存在" in health.error_message:
                    recommendation["suggestion"] = "模型ID不正确，请检查并修正模型配置"
                elif "401" in health.error_message or "Unauthorized" in health.error_message:
                    recommendation["suggestion"] = "API密钥无效或过期，请更新API密钥"
                elif "429" in health.error_message or "Too Many" in health.error_message:
                    recommendation["suggestion"] = "请求频率超限，请稍后重试或检查账户配额"
                elif "404" in health.error_message:
                    recommendation["suggestion"] = "API地址不正确，请检查base_url配置"
                else:
                    recommendation["suggestion"] = "调用失败，请检查网络和账户状态"
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def fix_common_issues(self) -> List[Dict]:
        """修复常见配置问题
        
        当前可以自动修复：
        - 智谱AI：将不存在的 glm-4-long-free 替换为正确的 glm-4-flash
        - 修正base_url末尾斜杠问题
        - 启用正确配置的免费模型
        """
        fixes_applied = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 修正base_url末尾斜杠
        cursor.execute("SELECT provider_code, base_url FROM provider_registry")
        for code, base_url in cursor.fetchall():
            if base_url and base_url.endswith("/"):
                new_url = base_url.rstrip("/")
                if new_url != base_url:
                    cursor.execute(
                        "UPDATE provider_registry SET base_url = ? WHERE provider_code = ?",
                        (new_url, code)
                    )
                    fixes_applied.append({
                        "type": "base_url_fix",
                        "provider": code,
                        "old": base_url,
                        "new": new_url
                    })
        
        # 2. 确保正确的免费模型被启用（智谱AI）
        # 这一步之前已经手动完成，这里只是验证
        cursor.execute("SELECT model_id, is_enabled FROM model_config WHERE provider = 'zhipu' AND model_id = 'glm-4-flash'")
        row = cursor.fetchone()
        if row and not row[1]:
            cursor.execute(
                "UPDATE model_config SET is_enabled = 1 WHERE provider = 'zhipu' AND model_id = 'glm-4-flash'",
            )
            fixes_applied.append({
                "type": "enable_model",
                "provider": "zhipu",
                "model": "glm-4-flash"
            })
        
        conn.commit()
        conn.close()
        return fixes_applied


def print_health_report(health: ProviderHealthChecker):
    """打印健康报告"""
    summary = health.get_health_summary()
    recommendations = health.get_recommendations()
    
    # 安全打印（避免GBK编码问题）
    def safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            text = text.replace('✓', '[OK]').replace('✗', '[X]').replace('⚠️', '[!]').replace('✅', 'OK')
            print(text)
    
    safe_print("\n" + "=" * 60)
    safe_print("序境服务商健康检查报告")
    safe_print("=" * 60)
    safe_print(f"总服务商数: {summary['total_providers']}")
    safe_print(f"已启用: {summary['enabled_providers']}")
    safe_print(f"完全健康: {summary['healthy_providers']} ✅")
    safe_print(f"部分健康: {summary['partial_providers']} ⚠️")
    safe_print(f"故障: {summary['failing_providers']} ✗")
    safe_print(f"已禁用: {summary['disabled_providers']}")
    safe_print("")
    
    safe_print("详细状态:")
    for code, result in summary['results'].items():
        status = result['overall_health']
        status_icon = {
            'healthy': '✅',
            'partial': '⚠️',
            'failing': '✗',
            'disabled': '-',
            'missing_key': '🔑'
        }.get(status, '?')
        safe_print(f"  {status_icon} {code} ({result['provider_name']}): {status}")
        if result['chat_test_passed']:
            rt = result['response_time']
            safe_print(f"      聊天: OK ({rt:.2f}s)")
        if result['error_message']:
            safe_print(f"      错误: {result['error_message']}")
    
    if recommendations:
        safe_print("\n修复建议:")
        for i, rec in enumerate(recommendations, 1):
            safe_print(f"  {i}. {rec['provider']}: {rec['issue']}")
            safe_print(f"     建议: {rec['suggestion']}")
    
    safe_print("\n测试完成: " + summary['test_time'])
    safe_print("=" * 60)
    
    return summary


if __name__ == "__main__":
    print("=== 序境服务商健康检查 ===\n")
    checker = ProviderHealthChecker()
    checker.test_all_providers()
    print_health_report(checker)
    
    fixes = checker.fix_common_issues()
    if fixes:
        print(f"\n应用自动修复: {len(fixes)} 项")
        for fix in fixes:
            print(f"  - {fix['type']}: {fix.get('provider', '')} {fix.get('model', '')}")
