"""
序境系统数据规范实时提醒引擎
功能：将120条总则转化为可检测的规范规则，实时拦截AI操作并提醒
"""
import sqlite3
import re
import sys
from datetime import datetime
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db"

# ============== 规则分类解析 ==============
RULE_CATEGORIES = {
    "路径访问": {
        "rule_ids": [1, 2, 3, 4],
        "severity": "WARN",
        "check_type": "path"
    },
    "表结构操作": {
        "rule_ids": [5, 9, 10, 31],
        "severity": "CRITICAL",
        "check_type": "sql_ddl"
    },
    "API密钥安全": {
        "rule_ids": [17, 18, 45, 46, 88],
        "severity": "CRITICAL",
        "check_type": "security"
    },
    "模型配置管控": {
        "rule_ids": [16, 19, 20, 21, 22, 23, 24, 110, 115, 116],
        "severity": "WARN",
        "check_type": "model_config"
    },
    "数据库优先": {
        "rule_ids": [26, 27, 28, 29, 30, 65, 101],
        "severity": "INFO",
        "check_type": "memory_sync"
    },
    "多模型协作": {
        "rule_ids": [11, 12, 13, 66, 97, 102],
        "severity": "INFO",
        "check_type": "multi_model"
    },
    "调度汇报": {
        "rule_ids": [14, 15, 25, 117],
        "severity": "WARN",
        "check_type": "reporting"
    },
    "会话尾标": {
        "rule_ids": [118, 119, 120],
        "severity": "INFO",
        "check_type": "session_tag"
    },
    "子代理规范": {
        "rule_ids": [90, 91, 92, 93, 94, 95, 114],
        "severity": "WARN",
        "check_type": "subagent"
    },
    "接管模式": {
        "rule_ids": [68, 69, 70, 71, 83, 86, 87, 89, 112, 113],
        "severity": "INFO",
        "check_type": "xujing_mode"
    }
}

# ============== 危险操作模式 ==============
DANGEROUS_PATTERNS = {
    "CRITICAL": [
        (r"CREATE\s+TABLE", "禁止创建新表（规则5: 禁止修改表结构）"),
        (r"ALTER\s+TABLE", "禁止修改表结构（规则5: 禁止修改表结构）"),
        (r"DROP\s+TABLE", "禁止删除表（规则5: 禁止修改表结构）"),
        (r"DROP\s+INDEX", "禁止删除索引"),
        (r"INSERT\s+INTO\s+model_config", "禁止自行创建模型配置（规则21）"),
        (r"DELETE\s+FROM\s+model_config", "禁止删除模型配置（规则22）"),
        (r"openclaw\s+gateway\s+restart", "禁止重启Gateway（用户约定）"),
        (r"openclaw\s+gateway\s+stop", "禁止停止Gateway（用户约定）"),
        (r"DELETE\s+FROM\s+\w+", "危险删除操作，请确认是否必要"),
        (r"TRUNCATE", "禁止清空表数据"),
        (r"(api_key|api-?key|secret)\s*=\s*['\"][^'\"]{8,}['\"]", 
         "检测到API密钥泄露风险（规则17-18: 密钥保密）"),
    ],
    "WARN": [
        (r"UPDATE\s+model_config", "修改模型配置需谨慎（规则22）"),
        (r"UPDATE\s+\w+\s+SET.*WHERE", "数据库更新操作，请确认影响范围（规则31）"),
        (r"SELECT\s+.*\s+FROM\s+model_config\s+WHERE", "读取模型配置正确（规则24）"),
        (r"INSERT\s+INTO\s+官署角色表", "添加官署角色，请确认角色配置正确（规则37-39）"),
        (r"INSERT\s+INTO\s+序境系统总则", "添加系统规则，请确认规则不与现有冲突"),
        (r"memory.*update.*MEMORY\.md", "更新记忆文件，请确保与数据库同步（规则26-30）"),
        (r"spawn.*subagent", "启动子代理，请确认授权（规则94）"),
        (r"会话尾标|尾标|【.*】", "检测到尾标规范（规则118-119）"),
    ],
    "INFO": [
        (r"多模型|multi.*model|并行|并发", "多模型协作建议（规则11）"),
        (r"token.*消耗|prompt.*token|completion.*token", "Tokens统计（规则14,25,117）"),
        (r"汇报|report", "汇报规范（规则14-15）"),
        (r"健康检查|health.*check|在线状态", "健康检查规则（规则73,75,104）"),
    ]
}

# ============== 规范化检查函数 ==============
def load_rules_from_db():
    """从数据库加载120条总则"""
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute("SELECT id, 规则名称, 规则说明, 智能体操作规范 FROM 序境系统总则 ORDER BY id")
    rules = cur.fetchall()
    conn.close()
    return rules

def check_operation(operation_text: str, context: str = "") -> list:
    """
    检查操作是否违反规范
    返回: [(severity, rule_id, message)]
    """
    violations = []
    full_text = f"{operation_text} {context}"
    
    for severity, patterns in DANGEROUS_PATTERNS.items():
        for pattern, message in patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                violations.append((severity, message))
    
    return violations

def generate_reminder(violations: list, operation: str) -> str:
    """生成规范提醒"""
    if not violations:
        return ""
    
    lines = ["⚠️ **序境规范提醒**\n"]
    
    critical = [v for v in violations if v[0] == "CRITICAL"]
    warn = [v for v in violations if v[0] == "WARN"]
    info = [v for v in violations if v[0] == "INFO"]
    
    if critical:
        lines.append("🚨 **严重违规（立即停止）:**")
        for _, msg in critical:
            lines.append(f"  ❌ {msg}")
        lines.append("")
    
    if warn:
        lines.append("⚡ **警告（需确认）:**")
        for _, msg in warn:
            lines.append(f"  ⚠️ {msg}")
        lines.append("")
    
    if info:
        lines.append("💡 **建议:**")
        for _, msg in info:
            lines.append(f"  ℹ️ {msg}")
        lines.append("")
    
    lines.append(f"📋 操作: `{operation[:80]}{'...' if len(operation)>80 else ''}`")
    lines.append("🔗 详见: `memory/2026-03-28.md` 或 `symphony_working.db·序境系统总则`")
    
    return "\n".join(lines)

def get_compliance_summary() -> str:
    """获取规范摘要（用于初始化提醒）"""
    rules = load_rules_from_db()
    total = len(rules)
    
    summary = f"""📋 **序境系统数据规范已加载** ({total}条)

🚨 **CRITICAL（立即停止）:**
  • 禁止创建/修改/删除表结构
  • 禁止自行创建模型配置记录
  • 禁止删除模型配置记录
  • 禁止重启/停止Gateway
  • 禁止泄露API密钥

⚡ **WARN（需确认）:**
  • 模型配置修改需谨慎
  • 数据库更新需确认影响范围
  • 子代理启动需确认授权
  • 需遵守调度汇报规则

💡 **INFO（建议遵守）:**
  • 多模型协作优先
  • 数据库为唯一真实来源
  • 会话需显示尾标
  • 每次调度汇报Tokens消耗

🗄️ **数据库:** symphony_working.db
📌 **核心表:** model_config | 官署角色表 | 序境系统总则
"""
    return summary

# ============== CLI测试 ==============
if __name__ == "__main__":
    print("=" * 50)
    print("序境系统数据规范引擎 - 自检")
    print("=" * 50)
    
    # 显示规范摘要
    print(get_compliance_summary())
    
    # 测试用例
    test_ops = [
        "CREATE TABLE new_model (...)",
        "openclaw gateway restart",
        "UPDATE model_config SET 在线状态=0 WHERE id=1",
        "SELECT * FROM model_config WHERE 服务商='英伟达'",
        "多模型并行调度任务",
    ]
    
    print("\n" + "=" * 50)
    print("规范检测测试")
    print("=" * 50)
    for op in test_ops:
        violations = check_operation(op)
        reminder = generate_reminder(violations, op)
        if reminder:
            print(f"\n输入: {op}")
            print(reminder)
        else:
            print(f"\n✅ 无违规: {op}")
