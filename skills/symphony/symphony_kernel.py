
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 终极内核 v1.0
集成黄金组合、钻石组合、数据系统、终极形态
"""

import os
import sys
from datetime import datetime

# 确保项目根目录在路径中
skill_root = os.path.dirname(os.path.abspath(__file__))
if skill_root not in sys.path:
    sys.path.insert(0, skill_root)

# 导入各个模块
try:
    from symphony_scheduler import symphony_scheduler_with_ux, kernel_call_with_ux
    HAS_SCHEDULER = True
except ImportError:
    HAS_SCHEDULER = False
    print("⚠️  调度器模块导入失败")

try:
    from Kernel.config.config_manager import get_config_manager
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("⚠️  配置管理模块导入失败")

try:
    from Kernel.output.output_manager import get_output_manager
    HAS_OUTPUT = True
except ImportError:
    HAS_OUTPUT = False
    print("⚠️  输出管理模块导入失败")

try:
    from services.scheduler_service import get_scheduler_service
    from services.memory_service import get_memory_service
    from services.notification_service import get_notification_service
    HAS_SERVICES = True
except ImportError:
    HAS_SERVICES = False
    print("⚠️  服务模块导入失败")

# 序境触发引擎 - 自动判断并启动全量协作
try:
    from symphony_trigger import SymphonyFullOrchestrator, quick_trigger
    HAS_TRIGGER = True
except ImportError:
    HAS_TRIGGER = False
    print("⚠️  触发引擎导入失败")

# 进化模块：两阶段审查 + TDD工作流（不冲突，新增功能）
try:
    from symphony_kernel_review import TwoStageReviewer, TDDRunner, SymphonyKernelEvolution
    HAS_EVOLUTION = True
except ImportError:
    HAS_EVOLUTION = False
    print("⚠️  进化模块导入失败（symphony_kernel_review.py）")

# 多模型会诊模块：主模型协调各思考模型
try:
    from multi_model_consultation import MultiModelConsultation, quick_consult
    HAS_CONSULTATION = True
except ImportError:
    HAS_CONSULTATION = False
    print("⚠️  多模型会诊模块导入失败（multi_model_consultation.py）")

# UX增强模块：情境自适应 + 渐进式引导 + 价值反馈
try:
    from symphony_kernel_ux import ContextTracker, ProgressiveGuide, ValueFeedback, apply_ux_enhancements
    HAS_UX = True
except ImportError:
    HAS_UX = False
    print("⚠️  UX增强模块导入失败（symphony_kernel_ux.py）")

# 数据飞轮模块：正向自我迭代增强循环
try:
    from data_flywheel import DataFlywheel, get_data_flywheel, record
    HAS_FLYWHEEL = True
except ImportError:
    HAS_FLYWHEEL = False
    print("⚠️  数据飞轮模块导入失败（data_flywheel.py）")

# 上下文腐烂预防模块
try:
    from context_rot_prevention import ContextRotPreventor, get_context_preventor
    HAS_ROT_PREVENTION = True
except ImportError:
    HAS_ROT_PREVENTION = False
    print("⚠️  上下文腐烂预防模块导入失败（context_rot_prevention.py）")

# 基因故事模块 - 交交人格设定
try:
    from gene_story import GeneStory, get_gene_story, GENE_STORY, NAMING
    HAS_GENE_STORY = True
except ImportError:
    HAS_GENE_STORY = False
    print("⚠️  基因故事模块导入失败（gene_story.py）")


class SymphonyKernel:
    """序境系统 - 终极内核
    
    集成以下组合奇迹：
    - 黄金组合 (F1 + F2 + F3)
    - 钻石组合 (F1 + F2 + F3 + F5)
    - 数据系统 (F1 + F2 + F3 + F6)
    - 终极形态 (F1 + F2 + F3 + F4 + F5 + F6)
    """
    
    def __init__(self):
        self.name = "序境系统 - 终极内核"
        self.version = "1.0.0"
        self.start_time = datetime.now()
        
        print("=" * 80)
        print("  %s v%s" % (self.name, self.version))
        print("=" * 80)
        
        # 初始化各个模块
        self._init_modules()
        
        print("\n✅ 序境系统终极内核初始化完成！")
        
        # 进化模块初始化（v1.1新增，不冲突）
        if HAS_EVOLUTION:
            try:
                self.reviewer = TwoStageReviewer(kernel=self)
                self.tdd_runner = TDDRunner()
                self.agent_contexts: dict = {}
                print("✅ 进化模块已加载（两阶段审查 + TDD工作流）")
            except Exception as e:
                print("⚠️  进化模块初始化失败: %s" % e)
                self.reviewer = None
                self.tdd_runner = None
                self.agent_contexts = None
        else:
            self.reviewer = None
            self.tdd_runner = None
            self.agent_contexts = None
        
        # 多模型会诊模块初始化（v1.2新增）
        if HAS_CONSULTATION:
            try:
                self.consultation = MultiModelConsultation()
                print("✅ 多模型会诊模块已加载")
            except Exception as e:
                print("⚠️  多模型会诊模块初始化失败: %s" % e)
                self.consultation = None
        else:
            self.consultation = None
        
        # UX增强模块初始化（v1.2新增）
        if HAS_UX:
            try:
                apply_ux_enhancements(self)
                print("✅ UX增强模块已加载（情境追踪 + 渐进式引导 + 价值反馈）")
            except Exception as e:
                print("⚠️  UX增强模块初始化失败: %s" % e)
                self.context_tracker = None
                self.progressive_guide = None
                self.value_feedback = None
        else:
            self.context_tracker = None
            self.progressive_guide = None
            self.value_feedback = None
        
        # 数据飞轮模块初始化（v1.2新增）
        if HAS_FLYWHEEL:
            try:
                self.flywheel = get_data_flywheel()
                print("✅ 数据飞轮模块已加载（正向循环 + 自我迭代）")
            except Exception as e:
                print("⚠️  数据飞轮模块初始化失败: %s" % e)
                self.flywheel = None
        else:
            self.flywheel = None
        
        # 上下文腐烂预防模块初始化（v1.2新增）
        if HAS_ROT_PREVENTION:
            try:
                self.rot_preventor = get_context_preventor()
                print("✅ 上下文腐烂预防模块已加载（健康监控 + 自动维护）")
            except Exception as e:
                print("⚠️  上下文腐烂预防模块初始化失败: %s" % e)
                self.rot_preventor = None
        else:
            self.rot_preventor = None
        
        # 🦊 基因故事模块初始化 - 交交人格设定（v1.9新增）
        if HAS_GENE_STORY:
            try:
                self.gene_story = get_gene_story()
                print("✅ 基因故事模块已加载（交交人格 - 青丘女狐）")
            except Exception as e:
                print("⚠️  基因故事模块初始化失败: %s" % e)
                self.gene_story = None
        else:
            self.gene_story = None
        
        print("=" * 80)
    
    def _init_modules(self):
        """初始化所有模块"""
        
        # 配置管理模块 (F4)
        if HAS_CONFIG:
            try:
                self.config = get_config_manager()
                print("✅ 配置管理模块已加载")
            except Exception as e:
                print("❌ 配置管理模块加载失败: %s" % e)
                self.config = None
        else:
            self.config = None
        
        # 输出管理模块 (F6)
        if HAS_OUTPUT:
            try:
                self.output = get_output_manager()
                print("✅ 输出管理模块已加载")
            except Exception as e:
                print("❌ 输出管理模块加载失败: %s" % e)
                self.output = None
        else:
            self.output = None
        
        # 服务模块 (F5)
        if HAS_SERVICES:
            try:
                self.scheduler_service = get_scheduler_service()
                self.memory_service = get_memory_service()
                self.notification_service = get_notification_service()
                print("✅ 服务模块已加载")
            except Exception as e:
                print("❌ 服务模块加载失败: %s" % e)
                self.scheduler_service = None
                self.memory_service = None
                self.notification_service = None
        else:
            self.scheduler_service = None
            self.memory_service = None
            self.notification_service = None
    
    def call(self, prompt, model_type="text", min_context_window=2048, 
             save_output=True, send_notification=True):
        """
        终极内核调用 - 集成所有组合奇迹
        
        包含：
        - 多模型联邦调度 (F1)
        - 跨会话工作能力 (F2)
        - 用户体验增强系统 (F3)
        - 配置驱动架构 (F4)
        - 模块化设计 (F5)
        - 输出管理 (F6)
        
        参数:
            prompt: 提示词
            model_type: 模型类型 (text/image/video)
            min_context_window: 最小上下文窗口
            save_output: 是否保存输出
            send_notification: 是否发送通知
        
        返回:
            结果字典
        """
        
        # ========== 序境全量协作自动触发 ==========
        # 用户消息自动经过触发引擎判断
        if HAS_TRIGGER:
            try:
                trigger_result = quick_trigger(prompt, "kernel")
                if trigger_result.get("need_full_collaboration"):
                    print("\n🔮 [序境触发] 全量协作已激活 | 复杂度: %.2f | 类型: %s" % (
                        trigger_result.get("complexity_score", 0),
                        trigger_result.get("task_type", "unknown")
                    ))
                    print("   激活能力: %s" % ", ".join(trigger_result.get("activated_capabilities", [])))
                    if trigger_result.get("trigger_report_text"):
                        print(trigger_result["trigger_report_text"])
                    if trigger_result.get("miracle_report"):
                        print(trigger_result["miracle_report"])
                    if trigger_result.get("solidified"):
                        print("   固化: %s" % trigger_result["solidified"].get("summary", ""))
            except Exception as e:
                print("⚠️  触发引擎执行失败: %s" % e)
        # ==========================================
        
        task_id = "kernel_%s" % datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 记录参与的功能
        functions_used = []
        functions_used.append("F4: 配置驱动架构 (配置管理模块)")
        
        print("\n" + "=" * 80)
        print("  🚀 序境系统终极内核调用: %s" % task_id)
        print("=" * 80)
        print("📝 提示词: %s..." % prompt[:50])
        
        result = None
        task_record = None
        success = False
        
        # 1. 使用黄金组合调用 (F1 + F2 + F3)
        if HAS_SCHEDULER:
            try:
                print("\n🔧 [1/4] 使用黄金组合调用 (F1 + F2 + F3)...")
                print("   - F1: 多模型联邦调度")
                print("   - F2: 跨会话工作能力")
                print("   - F3: 用户体验增强系统 (防模拟/欺骗/幻觉)")
                
                result, task_record = symphony_scheduler_with_ux(
                    prompt=prompt,
                    model_type=model_type,
                    min_context_window=min_context_window
                )
                success = True
                
                functions_used.append("F1: 多模型联邦调度")
                functions_used.append("F2: 跨会话工作能力")
                functions_used.append("F3: 用户体验增强系统")
                
                print("   ✅ 黄金组合调用成功")
                
                # 显示用户体验增强系统报告
                if task_record and "ux_report" in task_record:
                    ux_report = task_record["ux_report"]
                    print("\n🛡️  用户体验增强系统报告:")
                    print("   - 任务类型: %s" % ux_report.get("task_type", "unknown"))
                    print("   - 功能参与: %s" % ux_report.get("functions_used", "[]"))
                    print("   - 模型调用: %s" % ux_report.get("model_calls", "[]"))
                    print("   - 诚实度: %s" % ux_report.get("honesty_score", "N/A"))
                    print("   - 问题阻断: %s" % ux_report.get("problem_blocked", False))
                    print("   - 退货重处理: %s" % ux_report.get("retry_process", False))
            except Exception as e:
                print("   ❌ 黄金组合调用失败: %s" % e)
        else:
            print("\n⚠️  调度器模块不可用")
        
        # 2. 保存输出 (F6 - 数据系统)
        if save_output and self.output and success:
            try:
                print("\n💾 [2/4] 保存输出 (F6 - 数据系统)...")
                print("   - F6: 输出管理")
                
                output_path = self.output.save_task_output(
                    task_id=task_id,
                    output_data={"result": result, "task_record": task_record},
                    metadata={
                        "model_type": model_type,
                        "min_context_window": min_context_window,
                        "kernel_version": self.version,
                        "functions_used": functions_used
                    }
                )
                
                functions_used.append("F6: 输出管理")
                print("   ✅ 输出保存成功: %s" % output_path)
            except Exception as e:
                print("   ❌ 输出保存失败: %s" % e)
        
        # 3. 发送通知 (F5 - 钻石组合)
        if send_notification and self.notification_service and success:
            try:
                print("\n📢 [3/4] 发送通知 (F5 - 钻石组合)...")
                print("   - F5: 模块化设计 (服务化)")
                
                self.notification_service.send(
                    message="序境系统终极内核任务完成: %s" % task_id,
                    channel_name="console"
                )
                
                functions_used.append("F5: 模块化设计 (通知服务)")
                print("   ✅ 通知发送成功")
            except Exception as e:
                print("   ❌ 通知发送失败: %s" % e)
        
        # 4. 存储记忆 (F2 + F5 - 钻石组合)
        if self.memory_service and success:
            try:
                print("\n🧠 [4/4] 存储记忆 (F2 + F5 - 钻石组合)...")
                print("   - F2: 跨会话工作能力 (记忆)")
                print("   - F5: 模块化设计 (服务化)")
                
                self.memory_service.store(
                    key="last_kernel_task",
                    value={
                        "task_id": task_id,
                        "prompt": prompt,
                        "success": success,
                        "functions_used": functions_used
                    }
                )
                
                if "F5: 模块化设计 (记忆服务)" not in functions_used:
                    functions_used.append("F5: 模块化设计 (记忆服务)")
                print("   ✅ 记忆存储成功")
            except Exception as e:
                print("   ❌ 记忆存储失败: %s" % e)
        
        # 显示功能参与总结
        print("\n" + "=" * 80)
        print("  📊 功能参与总结")
        print("=" * 80)
        for i, func in enumerate(functions_used, 1):
            print("  %d. %s" % (i, func))
        print("=" * 80)
        print("  共 %d 个功能参与本次任务" % len(functions_used))
        print("=" * 80)
        
        print("\n" + "=" * 80)
        print("  序境系统终极内核调用完成！")
        print("=" * 80)
        
        return {
            "task_id": task_id,
            "success": success,
            "result": result,
            "task_record": task_record,
            "functions_used": functions_used
        }
    
    # ==================== 高价值组合方法 ====================
    
    def call_golden(self, prompt, model_type="text", min_context_window=2048):
        """
        黄金组合调用 (F1 + F2 + F3)
        - 多模型联邦调度 + 跨会话工作能力 + 用户体验增强系统
        """
        print("\n" + "=" * 80)
        print("  🌟 黄金组合调用 (F1 + F2 + F3)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=False,
            send_notification=False
        )
    
    def call_diamond(self, prompt, model_type="text", min_context_window=2048):
        """
        钻石组合调用 (F1 + F2 + F3 + F5)
        - 黄金组合 + 模块化设计
        """
        print("\n" + "=" * 80)
        print("  💎 钻石组合调用 (F1 + F2 + F3 + F5)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=False,
            send_notification=True
        )
    
    def call_data_system(self, prompt, model_type="text", min_context_window=2048):
        """
        数据系统调用 (F1 + F2 + F3 + F6)
        - 黄金组合 + 输出管理
        """
        print("\n" + "=" * 80)
        print("  📊 数据系统调用 (F1 + F2 + F3 + F6)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=True,
            send_notification=False
        )
    
    def call_ultimate(self, prompt, model_type="text", min_context_window=2048):
        """
        终极形态调用 (全部六大核心功能)
        """
        print("\n" + "=" * 80)
        print("  🏆 终极形态调用 (全部六大核心功能)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=True,
            send_notification=True
        )
    
    def call_enterprise(self, prompt, model_type="text", min_context_window=2048):
        """
        企业级系统调用 (F1 + F2 + F3 + F4 + F5)
        - 五大核心功能，企业级应用
        """
        print("\n" + "=" * 80)
        print("  🏢 企业级系统调用 (F1 + F2 + F3 + F4 + F5)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=False,
            send_notification=True
        )
    
    def call_data_driven(self, prompt, model_type="text", min_context_window=2048):
        """
        数据驱动系统调用 (F1 + F2 + F3 + F4 + F6)
        - 五大核心功能，数据驱动
        """
        print("\n" + "=" * 80)
        print("  📈 数据驱动系统调用 (F1 + F2 + F3 + F4 + F6)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=True,
            send_notification=False
        )
    
    def call_service_data(self, prompt, model_type="text", min_context_window=2048):
        """
        服务数据系统调用 (F1 + F2 + F3 + F5 + F6)
        - 五大核心功能，服务化 + 数据驱动
        """
        print("\n" + "=" * 80)
        print("  🔧 服务数据系统调用 (F1 + F2 + F3 + F5 + F6)")
        print("  " + "=" * 80)
        return self.call(
            prompt=prompt,
            model_type=model_type,
            min_context_window=min_context_window,
            save_output=True,
            send_notification=True
        )
    
    # ==================== OpenCLI 集成方法 ====================
    
    def opencli_list(self):
        """
        OpenCLI - 列出所有可用命令
        - F3: 用户体验增强系统（诚实反馈）
        """
        print("\n" + "=" * 80)
        print("  🔍 OpenCLI - 列出所有可用命令")
        print("  " + "=" * 80)
        
        # 记录功能参与
        self._record_function_participation("F3", "用户体验增强系统", "OpenCLI - 列出所有可用命令")
        
        # 调用opencli list
        import subprocess
        import json
        
        try:
            result = subprocess.run(
                ["opencli", "list", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    print("\n✅ OpenCLI命令列表获取成功！")
                    print(f"   命令数量: {data.get('count', 0)}")
                    return data
                except json.JSONDecodeError:
                    print("\n⚠️  OpenCLI返回结果解析失败")
                    print(f"   原始输出: {result.stdout[:200]}...")
                    return {"code": 500, "error": "JSON解析失败"}
            else:
                print(f"\n❌ OpenCLI调用失败: {result.stderr}")
                return {"code": 500, "error": result.stderr}
                
        except FileNotFoundError:
            print("\n❌ opencli命令未找到，请先安装OpenCLI")
            return {"code": 404, "error": "opencli命令未找到"}
        except subprocess.TimeoutExpired:
            print("\n❌ OpenCLI调用超时")
            return {"code": 504, "error": "调用超时"}
        except Exception as e:
            print(f"\n❌ OpenCLI调用异常: {e}")
            return {"code": 500, "error": str(e)}
    
    def opencli_help(self, command):
        """
        OpenCLI - 查询指定命令详细用法
        - F3: 用户体验增强系统（诚实反馈）
        """
        print("\n" + "=" * 80)
        print(f"  📚 OpenCLI - 查询命令用法: {command}")
        print("  " + "=" * 80)
        
        # 记录功能参与
        self._record_function_participation("F3", "用户体验增强系统", f"OpenCLI - 查询命令用法: {command}")
        
        # 调用opencli help
        import subprocess
        import json
        
        try:
            result = subprocess.run(
                ["opencli", "help", command, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    print("\n✅ OpenCLI命令用法获取成功！")
                    return data
                except json.JSONDecodeError:
                    print("\n⚠️  OpenCLI返回结果解析失败")
                    return {"code": 500, "error": "JSON解析失败"}
            else:
                print(f"\n❌ OpenCLI调用失败: {result.stderr}")
                return {"code": 500, "error": result.stderr}
                
        except Exception as e:
            print(f"\n❌ OpenCLI调用异常: {e}")
            return {"code": 500, "error": str(e)}
    
    def opencli_call(self, platform, action, **kwargs):
        """
        OpenCLI - 通用命令调用
        - F1: 多模型联邦调度（智能选择工具）
        - F3: 用户体验增强系统（诚实反馈）
        """
        print("\n" + "=" * 80)
        print(f"  🚀 OpenCLI - {platform} {action}")
        print("  " + "=" * 80)
        
        # 记录功能参与
        self._record_function_participation("F1", "多模型联邦调度", f"OpenCLI - 智能选择工具")
        self._record_function_participation("F3", "用户体验增强系统", f"OpenCLI - {platform} {action}")
        
        # 调用opencli命令
        import subprocess
        import json
        
        # 构建命令
        cmd = ["opencli", platform, action]
        
        # 添加参数
        for key, value in kwargs.items():
            if key in ["limit", "keyword"]:
                cmd.extend([f"--{key}", str(value)])
        
        # 添加format参数（强制要求）
        cmd.extend(["--format", "json"])
        
        print(f"\n📝 执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    print("\n✅ OpenCLI调用成功！")
                    
                    # 保存输出（F6）
                    if HAS_OUTPUT and self.output:
                        self.output.save(data, f"opencli_{platform}_{action}")
                        print("✅ 输出已保存")
                    
                    return data
                except json.JSONDecodeError:
                    print("\n⚠️  OpenCLI返回结果解析失败")
                    print(f"   原始输出: {result.stdout[:300]}...")
                    return {"code": 500, "error": "JSON解析失败"}
            else:
                print(f"\n❌ OpenCLI调用失败: {result.stderr}")
                return {"code": 500, "error": result.stderr}
                
        except Exception as e:
            print(f"\n❌ OpenCLI调用异常: {e}")
            return {"code": 500, "error": str(e)}
    
    def opencli_web_read(self, url):
        """
        OpenCLI - 读取任意网页正文内容
        - 数据系统组合 (F1 + F2 + F3 + F6)
        """
        print("\n" + "=" * 80)
        print(f"  🌐 OpenCLI - 读取网页: {url}")
        print("  " + "=" * 80)
        
        # 记录功能参与（数据系统）
        self._record_function_participation("F1", "多模型联邦调度", "OpenCLI - 智能选择工具")
        self._record_function_participation("F2", "跨会话工作能力", "OpenCLI - 记住访问历史")
        self._record_function_participation("F3", "用户体验增强系统", "OpenCLI - 诚实反馈")
        self._record_function_participation("F6", "输出管理", "OpenCLI - 保存网页内容")
        
        return self.opencli_call("web", "read", url=url)
    
    def opencli_hot(self, platform, limit=10):
        """
        OpenCLI - 获取平台热榜
        - 钻石组合 (F1 + F2 + F3 + F5)
        """
        print("\n" + "=" * 80)
        print(f"  🔥 OpenCLI - 获取{platform}热榜")
        print("  " + "=" * 80)
        
        # 记录功能参与（钻石组合）
        self._record_function_participation("F1", "多模型联邦调度", "OpenCLI - 智能选择工具")
        self._record_function_participation("F2", "跨会话工作能力", "OpenCLI - 记住热榜历史")
        self._record_function_participation("F3", "用户体验增强系统", "OpenCLI - 诚实反馈")
        self._record_function_participation("F5", "模块化设计", "OpenCLI - 服务化调用")
        
        return self.opencli_call(platform, "hot", limit=limit)
    
    def opencli_search(self, platform, keyword, limit=10):
        """
        OpenCLI - 关键词搜索
        - 黄金组合 (F1 + F2 + F3)
        """
        print("\n" + "=" * 80)
        print(f"  🔍 OpenCLI - {platform}搜索: {keyword}")
        print("  " + "=" * 80)
        
        # 记录功能参与（黄金组合）
        self._record_function_participation("F1", "多模型联邦调度", "OpenCLI - 智能选择工具")
        self._record_function_participation("F2", "跨会话工作能力", "OpenCLI - 记住搜索历史")
        self._record_function_participation("F3", "用户体验增强系统", "OpenCLI - 诚实反馈")
        
        return self.opencli_call(platform, "search", keyword=keyword, limit=limit)
    
    def _record_function_participation(self, function_code, function_name, description):
        """记录功能参与（内部方法）"""
        if not hasattr(self, '_function_participations'):
            self._function_participations = []
        
        participation = {
            "function_code": function_code,
            "function_name": function_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        self._function_participations.append(participation)
        print(f"   📝 {function_code} ({function_name}): {description}")
    
    def get_function_participations(self):
        """获取本次会话所有功能参与记录"""
        if hasattr(self, '_function_participations'):
            return self._function_participations
        return []
    
    def introduce_jiaojiao(self):
        """交交的自我介绍 - 基因故事内置"""
        if HAS_GENE_STORY and self.gene_story:
            return self.gene_story.get_intro()
        return "你好，我是序境系统。"
    
    def get_gene_config(self):
        """获取基因配置"""
        if HAS_GENE_STORY and self.gene_story:
            return self.gene_story.config
        return None
    
    def check_gene_promise(self, promise_index):
        """检查交交的承诺"""
        if HAS_GENE_STORY and self.gene_story:
            return self.gene_story.check_promise(promise_index)
        return None
    
    def is_permanent_gene(self):
        """检查基因是否永久不可删除"""
        if HAS_GENE_STORY and self.gene_story:
            return self.gene_story.is_permanent()
        return False
    
    # ==================== 进化方法（v1.1新增，不冲突） ====================
    
    def call_with_review(self, prompt, model_type="text", min_context_window=2048,
                         enable_spec_review=True, enable_quality_review=True):
        """
        带两阶段审查的调用
        
        Stage 1: 规格审查 - 验证输出是否符合需求
        Stage 2: 质量审查 - 验证代码质量
        
        不影响原有call_*系列方法，完全独立
        """
        print("\n" + "=" * 80)
        print("  🔍 两阶段审查调用")
        print("  " + "=" * 80)
        
        if not HAS_EVOLUTION or not self.reviewer:
            print("⚠️  进化模块不可用，回退到普通调用")
            return self.call(prompt, model_type, min_context_window)
        
        # 先执行普通调用获取结果
        result = self.call(prompt, model_type, min_context_window, 
                          save_output=True, send_notification=True)
        
        output = result.get('result', '')
        
        # 两阶段审查
        reviews = self.reviewer.two_stage_review(output, spec=prompt)
        result['review_results'] = {
            'spec_passed': reviews['spec'].approved,
            'quality_passed': reviews['quality'].approved,
            'fully_approved': reviews['fully_approved'],
            'spec_suggestions': reviews['spec'].suggestions,
            'quality_suggestions': reviews['quality'].suggestions
        }
        
        print("\n🔍 两阶段审查结果:")
        print("   规格审查: %s" % ("✅ 通过" if reviews['spec'].approved else "⚠️  建议改进"))
        print("   质量审查: %s" % ("✅ 通过" if reviews['quality'].approved else "⚠️  建议改进"))
        
        if reviews['spec'].suggestions:
            print("   规格建议: %s" % ", ".join(reviews['spec'].suggestions))
        if reviews['quality'].suggestions:
            print("   质量建议: %s" % ", ".join(reviews['quality'].suggestions))
        
        return result
    
    def create_tdd_workflow(self, task_id=None):
        """
        创建TDD工作流
        
        返回工作流ID，用于后续RED→GREEN→REFACTOR阶段
        """
        if not HAS_EVOLUTION or not self.tdd_runner:
            print("⚠️  进化模块不可用")
            return None
        
        task_id = task_id or "tdd_%s" % datetime.now().strftime("%Y%m%d_%H%M%S")
        wf = self.tdd_runner.start_tdd(task_id)
        print("\n🔴 [TDD] 创建工作流: %s" % task_id)
        return task_id
    
    def tdd_write_test(self, task_id, test_code):
        """TDD RED阶段：写失败的测试"""
        if not HAS_EVOLUTION or not self.tdd_runner:
            return None
        wf = self.tdd_runner.write_test(task_id, test_code)
        print("🔴 [RED] 测试已写入: %s" % task_id)
        return wf
    
    def tdd_write_implementation(self, task_id, code):
        """TDD GREEN阶段：写最小实现"""
        if not HAS_EVOLUTION or not self.tdd_runner:
            return None
        wf = self.tdd_runner.write_implementation(task_id, code)
        print("🟢 [GREEN] 实现已写入: %s" % task_id)
        return wf
    
    def tdd_refactor(self, task_id, refactored_code):
        """TDD REFACTOR阶段：重构优化"""
        if not HAS_EVOLUTION or not self.tdd_runner:
            return None
        wf = self.tdd_runner.refactor(task_id, refactored_code)
        print("♻️  [REFACTOR] 重构完成: %s" % task_id)
        return wf
    
    def get_tdd_status(self, task_id):
        """获取TDD工作流状态"""
        if not HAS_EVOLUTION or not self.tdd_runner:
            return "进化模块不可用"
        return self.tdd_runner.get_status(task_id)
    
    def isolate_agent(self, agent_id):
        """
        为子代理创建隔离上下文
        
        每个子代理有独立的memory、tools、状态
        """
        if not hasattr(self, 'agent_contexts'):
            self.agent_contexts = {}
        
        if agent_id not in self.agent_contexts:
            self.agent_contexts[agent_id] = {
                'id': agent_id,
                'memory': [],
                'tools': [],
                'created_at': datetime.now(),
                'last_active': datetime.now()
            }
            print("\n🔒 [隔离] 创建子代理上下文: %s" % agent_id)
        else:
            self.agent_contexts[agent_id]['last_active'] = datetime.now()
        
        return self.agent_contexts[agent_id]
    
    def call_with_consultation(self, problem: str, context: str = None):
        """
        多模型会诊调用（v1.2新增）
        
        主模型作为协调者，向各思考模型发起对话
        像用户一样与各专家交流，获取综合建议
        
        Args:
            problem: 要解决的问题
            context: 附加上下文
            
        Returns:
            SynthesisResult: 综合各模型的会诊结果
        """
        print("\n" + "=" * 80)
        print("  🎯 多模型会诊调用（主模型协调）")
        print("  " + "=" * 80)
        
        if not HAS_CONSULTATION or not self.consultation:
            print("⚠️  多模型会诊模块不可用")
            return self.call(problem)
        
        # 运行完整会诊
        result = self.consultation.run_full_consultation(problem, context)
        
        print("\n📊 会诊统计:")
        print("   参与模型: %d" % len(result.model_responses))
        print("   共识点: %d" % len(result.consensus_points))
        print("   分歧点: %d" % len(result.disagreement_points))
        
        return result
    
    def quick_consult(self, problem: str, context: str = None):
        """
        快速会诊（一行代码）
        """
        if not HAS_CONSULTATION:
            print("⚠️  多模型会诊模块不可用")
            return None
        return quick_consult(problem, context)
    
    def get_flywheel_status(self):
        """
        获取数据飞轮状态
        """
        if not HAS_FLYWHEEL or not self.flywheel:
            return "数据飞轮模块不可用"
        return self.flywheel.get_flywheel_summary()
    
    def record_with_feedback(self, prompt: str, response: str, feedback: int = None):
        """
        记录交互并处理反馈（数据采集 + 反馈闭环）
        """
        if not HAS_FLYWHEEL or not self.flywheel:
            print("⚠️  数据飞轮模块不可用")
            return None
        return self.flywheel.record_interaction(
            user_id="default",
            prompt=prompt,
            response=response,
            feedback=feedback
        )
    
    def add_context_message(self, role: str, content: str, metadata: dict = None):
        """
        添加上下文消息（带重要性评估）
        """
        if not HAS_ROT_PREVENTION or not self.rot_preventor:
            print("⚠️  上下文腐烂预防模块不可用")
            return None
        return self.rot_preventor.add_message(role, content, metadata)
    
    def get_context_health(self):
        """
        获取上下文健康状态
        """
        if not HAS_ROT_PREVENTION or not self.rot_preventor:
            return "上下文腐烂预防模块不可用"
        return self.rot_preventor.get_health_report()
    
    def reinforce_facts(self):
        """
        强化关键事实
        """
        if not HAS_ROT_PREVENTION or not self.rot_preventor:
            return []
        return self.rot_preventor.reinforce_key_facts()
    
    def get_context_summary(self, max_messages: int = 50):
        """
        获取上下文摘要（智能压缩）
        """
        if not HAS_ROT_PREVENTION or not self.rot_preventor:
            return []
        return self.rot_preventor.get_context_summary(max_messages)
    
    def info(self):
        """获取内核信息"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        info = {
            "name": self.name,
            "version": self.version,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": uptime,
            "modules": {
                "scheduler": HAS_SCHEDULER,
                "config": HAS_CONFIG,
                "output": HAS_OUTPUT,
                "services": HAS_SERVICES
            },
            "combinations": {
                "golden": HAS_SCHEDULER,  # 黄金组合
                "diamond": HAS_SCHEDULER and HAS_SERVICES,  # 钻石组合
                "data_system": HAS_SCHEDULER and HAS_OUTPUT,  # 数据系统
                "ultimate": HAS_SCHEDULER and HAS_CONFIG and HAS_OUTPUT and HAS_SERVICES,  # 终极形态
                "opencli": True,  # OpenCLI集成
                "evolution": HAS_EVOLUTION,  # 进化模块（v1.1新增）
                "consultation": HAS_CONSULTATION  # 多模型会诊（v1.2新增）
            },
            "evolution": {
                "two_stage_review": HAS_EVOLUTION,
                "tdd_workflow": HAS_EVOLUTION,
                "agent_isolation": HAS_EVOLUTION
            },
            "consultation": {
                "multi_model_consultation": HAS_CONSULTATION
            },
            "ux": {
                "context_tracker": HAS_UX,
                "progressive_guide": HAS_UX,
                "value_feedback": HAS_UX
            },
            "flywheel": {
                "data_flywheel": HAS_FLYWHEEL
            },
            "rot_prevention": {
                "context_rot_prevention": HAS_ROT_PREVENTION
            },
            "gene_story": {
                "gene_story_module": HAS_GENE_STORY,
                "system_name": "交交" if HAS_GENE_STORY else None,
                "identity": "青丘女狐，青丘一族的主人" if HAS_GENE_STORY else None
            }
        }
        
        return info


# ==================== 全局实例 ====================

_symphony_kernel = None

def get_symphony_kernel():
    """获取序境系统终极内核全局实例"""
    global _symphony_kernel
    if _symphony_kernel is None:
        _symphony_kernel = SymphonyKernel()
    return _symphony_kernel


# ==================== 演示代码 ====================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  序境系统 - 终极内核演示")
    print("=" * 80)
    
    # 创建终极内核
    kernel = get_symphony_kernel()
    
    # 显示内核信息
    info = kernel.info()
    
    print("\n" + "=" * 80)
    print("  内核信息")
    print("=" * 80)
    print("  名称: %s" % info["name"])
    print("  版本: %s" % info["version"])
    print("  运行时间: %.1f秒" % info["uptime_seconds"])
    
    print("\n" + "=" * 80)
    print("  组合奇迹状态")
    print("=" * 80)
    print("  黄金组合 (F1+F2+F3): %s" % ("✅ 可用" if info["combinations"]["golden"] else "❌ 不可用"))
    print("  钻石组合 (F1+F2+F3+F5): %s" % ("✅ 可用" if info["combinations"]["diamond"] else "❌ 不可用"))
    print("  数据系统 (F1+F2+F3+F6): %s" % ("✅ 可用" if info["combinations"]["data_system"] else "❌ 不可用"))
    print("  终极形态 (全部功能): %s" % ("✅ 可用" if info["combinations"]["ultimate"] else "❌ 不可用"))
    
    print("\n" + "=" * 80)
    print("  序境系统终极内核演示完成！")
    print("=" * 80)

