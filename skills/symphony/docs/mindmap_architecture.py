# -*- coding: utf-8 -*-
"""
============================================================================
序境系统架构思维导图
============================================================================
生成架构图：SVG + ASCII 两种格式

使用方式�?  python docs/mindmap_architecture.py

输出�?  docs/mindmap_architecture.svg  (浏览器可打开)
  docs/mindmap_architecture.txt  (控制台查�?
============================================================================
"""
import os

SYMPHONY_ROOT = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
if not SYMPHONY_ROOT.endswith('/symphony/docs'):
    SYMPHONY_ROOT = os.path.dirname(SYMPHONY_ROOT) + '/docs'
OUTPUT_DIR = os.path.dirname(SYMPHONY_ROOT)
SVG_PATH = os.path.join(OUTPUT_DIR, 'mindmap_architecture.svg')
TXT_PATH = os.path.join(OUTPUT_DIR, 'mindmap_architecture.txt')

# ============================================================================
# ASCII 思维导图
# ============================================================================
ASCII_MAP = """
================================================================================
                    序境系统 (Xujing) v4.3.0 架构思维导图
================================================================================

                                    ┌─────────────────�?                                    �?  序境系统 v4.3  �?                                    �?  多脑协作引擎   �?                                    └────────┬────────�?                                             �?         ┌───────────────┬───────────────────┼───────────────────┬───────────────�?         �?              �?                  �?                  �?              �?    ┌────▼───�?    ┌─────▼─────�?    ┌──────▼──────�?    ┌─────▼─────�?    ┌────▼───�?    �?Kernel �?    �?providers �?    �? strategy   �?    �? config   �?    �? test  �?    �? 内核   �?    �? 服务�?  �?    �?  策略      �?    �?  配置    �?    �? 测试  �?    └────┬───�?    └─────┬─────�?    └──────┬──────�?    └─────┬─────�?    └────┬───�?         �?              �?                  �?                  �?              �?    ┌────▼───────────────▼─────�?    ┌──────▼──────�?    ┌─────▼─────�?    ┌────▼───�?    �? 核心模块 (10文件)       �?    │dual_engine  �?    �?7配置     �?    │integra-�?    �? evolution_kernel       �?    �?_scheduler   �?    �?          �?    │tion_test�?    �? intelligent_strategy   �?    �?蜂蚁双引�?  �?    �?tokens,db  �?    �?       �?    �? _scheduler             �?    �?             �?    �?api,rule  �?    �?       �?    �? model_federation       �?    └──────────────�?    └───────────�?    └────────�?    �? wisdom_engine          �?    �? swarm_intelligence     �?    �? adaptive_algorithm     �?    �? _coordinator           �?    └────┬──────────┬─────────�?         �?         �?    ┌────▼────�?┌───▼──────�?    │evolution�?│multi_    �?    │进化系�?�?│agent     �?    �?8文件   �?│多智能�? �?    └────┬────�?�? 2文件   �?         �?     └──────────�?    ┌────▼────────────────────▼────�?    �? 进化核心 (V2)                �?    �? self_evolution_v2           �?    �? agent_memory_layer          �?    �? lifecycle_manager           �?    └──────────────────────────────�?
================================================================================
                              核心调度流程
================================================================================

   ┌──────────�?    ┌───────────────────�?    ┌────────────────────�?   �? 任务    �?──�?�? 复杂度评�?      �?──�?�? 多脑激�?         �?   �? 输入    �?    �? (1/2/3/5/7�?   �?    �? (自适应N�?       �?   └──────────�?    └───────────────────�?    └─────────┬─────────�?                                                        �?         ┌───────────────────────────────────────────────┼───────────────�?         �?                  �?                  �?              �?          �?    ┌────▼────�?       ┌─────▼─────�?     ┌─────▼────�?  ┌────▼────�? ┌───▼────�?    �?算法�? �?       �?  秘书    �?     �? 战略�? �?  �? 档案�?�? �?测试�?�?    �?ACO/   �?       �? 记录     �?     �? 决策    �?  �? 记忆   �? �?验证   �?    �?BCO    �?       �?          �?     �?         �?  �?        �? �?       �?    └────┬────�?       └─────┬─────�?     └─────┬────�?  └────┬────�? └───┬────�?         �?                  �?                  �?              �?           �?         └───────────────────┴───────────────────┴───────────────┴────────────�?                                    �?                              ┌─────▼─────�?                              �? 结果聚合 �?                              �? 涌现智慧 �?                              └───────────�?
================================================================================
                              模型服务�?(938+)
================================================================================

   ┌──────────�? ┌──────────�? ┌──────────�? ┌──────────�? ┌──────────�?   �? 智谱AI  �? �? 英伟�? �? �?硅基流动 �? │阿里百�? �? �?火山引擎 �?   �? 6模型  �? �?192模型  �? �?108模型  �? �?360模型  �? �? 限流�? �?   �? ✅可�?�? �? ✅可�? �? �? ✅可�? �? �? ✅可�? �? �?  �?   �?   └──────────�? └──────────�? └──────────�? └──────────�? └──────────�?
================================================================================
                              调度策略
================================================================================

   ┌──────────────────────────────────────────────────────────────�?   �? 智能策略选择 (7种策略自动切�?                              �?   ├──────────────────────────────────────────────────────────────�?   �? random �?round_robin �?least_loaded �?predictive           �?   �? ──── �?──── �?──── �?──── �?                              �?   �? aco_routing �?bco_allocation �?dual_engine               �?   └──────────────────────────────────────────────────────────────�?
================================================================================
                              关键文件索引
================================================================================

   �?核心文件:
   Kernel/evolution_kernel.py           # 进化内核主入�?   Kernel/intelligent_strategy_scheduler.py  # 智能策略调度�?   Kernel/model_federation.py           # 模型联邦
   providers/pool.py                     # ProviderPool (938模型)
   strategy/dual_engine_scheduler.py     # 蜂蚁双引�?   test/integration_test.py              # 集成测试

   �?配置:
   config/tokens_config.py               # API密钥
   config/database.py                    # 数据库配�?   config/providers.json                 # 服务商配�?
   �?规则:
   rules/compliance_engine.py            # 合规引擎

================================================================================
"""

# ============================================================================
# SVG 思维导图
# ============================================================================
SVG_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- 背景 -->
  <rect width="1200" height="900" fill="url(#bg)" rx="12"/>

  <!-- 标题 -->
  <text x="600" y="45" text-anchor="middle" font-family="Arial" font-size="28" font-weight="bold" fill="#f0f0f0">序境系统 Xujing v4.3.0</text>
  <text x="600" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="#aaa">多脑协作调度引擎 · 938+ 模型 · 自主进化</text>

  <!-- 中心节点 -->
  <circle cx="600" cy="460" r="70" fill="#e94560" filter="url(#shadow)"/>
  <text x="600" y="455" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="white">序境系统</text>
  <text x="600" y="475" text-anchor="middle" font-family="Arial" font-size="12" fill="#eee">v4.3.0</text>

  <!-- 一级分�?-->
  <!-- Kernel -->
  <line x1="530" y1="460" x2="200" y2="200" stroke="#4ecca3" stroke-width="3"/>
  <rect x="100" y="170" width="200" height="60" rx="8" fill="#232931" stroke="#4ecca3" stroke-width="2"/>
  <text x="200" y="198" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#4ecca3">Kernel 内核核心</text>
  <text x="200" y="216" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">evolution_kernel</text>

  <!-- providers -->
  <line x1="530" y1="460" x2="200" y2="400" stroke="#ff6b6b" stroke-width="3"/>
  <rect x="100" y="370" width="200" height="60" rx="8" fill="#232931" stroke="#ff6b6b" stroke-width="2"/>
  <text x="200" y="398" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ff6b6b">providers 服务�?/text>
  <text x="200" y="416" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">pool.py · 938模型</text>

  <!-- strategy -->
  <line x1="600" y1="390" x2="600" y2="200" stroke="#ffd93d" stroke-width="3"/>
  <rect x="500" y="170" width="200" height="60" rx="8" fill="#232931" stroke="#ffd93d" stroke-width="2"/>
  <text x="600" y="198" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ffd93d">strategy 策略调度</text>
  <text x="600" y="216" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">dual_engine_scheduler</text>

  <!-- config -->
  <line x1="670" y1="460" x2="900" y2="200" stroke="#6bcbff" stroke-width="3"/>
  <rect x="800" y="170" width="200" height="60" rx="8" fill="#232931" stroke="#6bcbff" stroke-width="2"/>
  <text x="900" y="198" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#6bcbff">config 配置</text>
  <text x="900" y="216" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">tokens · database · providers</text>

  <!-- test -->
  <line x1="670" y1="460" x2="1000" y2="400" stroke="#c17fff" stroke-width="3"/>
  <rect x="900" y="370" width="200" height="60" rx="8" fill="#232931" stroke="#c17fff" stroke-width="2"/>
  <text x="1000" y="398" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#c17fff">test 测试</text>
  <text x="1000" y="416" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">integration_test.py</text>

  <!-- rules -->
  <line x1="670" y1="460" x2="1000" y2="200" stroke="#ff9f43" stroke-width="3"/>
  <rect x="900" y="170" width="200" height="60" rx="8" fill="#232931" stroke="#ff9f43" stroke-width="2"/>
  <text x="1000" y="198" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ff9f43">rules 规则引擎</text>
  <text x="1000" y="216" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">compliance_engine</text>

  <!-- feishu -->
  <line x1="530" y1="460" x2="200" y2="600" stroke="#ff79c6" stroke-width="3"/>
  <rect x="100" y="570" width="200" height="60" rx="8" fill="#232931" stroke="#ff79c6" stroke-width="2"/>
  <text x="200" y="598" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ff79c6">feishu 飞书</text>
  <text x="200" y="616" text-anchor="middle" font-family="Arial" font-size="10" fill="#aaa">8模块</text>

  <!-- Kernel 二级节点 -->
  <!-- evolution -->
  <line x1="100" y1="230" x2="60" y2="320" stroke="#4ecca3" stroke-width="2" stroke-dasharray="4"/>
  <rect x="20" y="320" width="120" height="50" rx="6" fill="#1a3a2a" stroke="#4ecca3" stroke-width="1"/>
  <text x="80" y="340" text-anchor="middle" font-family="Arial" font-size="10" fill="#4ecca3">evolution</text>
  <text x="80" y="356" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">8文件</text>

  <!-- multi_agent -->
  <line x1="300" y1="200" x2="350" y2="300" stroke="#4ecca3" stroke-width="2" stroke-dasharray="4"/>
  <rect x="300" y="300" width="130" height="50" rx="6" fill="#1a3a2a" stroke="#4ecca3" stroke-width="1"/>
  <text x="365" y="320" text-anchor="middle" font-family="Arial" font-size="10" fill="#4ecca3">multi_agent</text>
  <text x="365" y="336" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">2文件</text>

  <!-- wisdom -->
  <line x1="200" y1="200" x2="100" y2="130" stroke="#4ecca3" stroke-width="2" stroke-dasharray="4"/>
  <rect x="40" y="90" width="120" height="45" rx="6" fill="#1a3a2a" stroke="#4ecca3" stroke-width="1"/>
  <text x="100" y="110" text-anchor="middle" font-family="Arial" font-size="10" fill="#4ecca3">wisdom_engine</text>
  <text x="100" y="125" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">智慧涌现</text>

  <!-- SwarmIntelligence -->
  <line x1="200" y1="200" x2="300" y2="120" stroke="#4ecca3" stroke-width="2" stroke-dasharray="4"/>
  <rect x="240" y="85" width="130" height="45" rx="6" fill="#1a3a2a" stroke="#4ecca3" stroke-width="1"/>
  <text x="305" y="105" text-anchor="middle" font-family="Arial" font-size="10" fill="#4ecca3">swarm_intelligence</text>
  <text x="305" y="120" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">ACO+BCO</text>

  <!-- Scheduler -->
  <line x1="300" y1="200" x2="420" y2="130" stroke="#4ecca3" stroke-width="2" stroke-dasharray="4"/>
  <rect x="370" y="90" width="130" height="45" rx="6" fill="#1a3a2a" stroke="#4ecca3" stroke-width="1"/>
  <text x="435" y="110" text-anchor="middle" font-family="Arial" font-size="10" fill="#4ecca3">intelligent_scheduler</text>
  <text x="435" y="125" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">7种策�?/text>

  <!-- 多脑协作流程 -->
  <rect x="40" y="680" width="340" height="180" rx="10" fill="#1a2a3a" stroke="#4ecca3" stroke-width="2"/>
  <text x="210" y="705" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#4ecca3">多脑协作流程</text>
  <text x="210" y="725" text-anchor="middle" font-family="Arial" font-size="10" fill="#888">自适应N�?(1/2/3/5/7)</text>

  <text x="60" y="750" font-family="monospace" font-size="10" fill="#aaa">任务 �?复杂度评�?�?多脑激�?/text>
  <text x="60" y="768" font-family="monospace" font-size="10" fill="#4ecca3"> 算法�?+ 秘书 + 战略�?/text>
  <text x="60" y="786" font-family="monospace" font-size="10" fill="#ffd93d"> 档案�?+ 测试�?+ 扩展专家</text>
  <text x="60" y="804" font-family="monospace" font-size="10" fill="#ff6b6b"> 结果聚合 �?涌现智慧</text>
  <text x="60" y="822" font-family="monospace" font-size="10" fill="#6bcbff"> 记忆同步 �?知识蒸馏</text>
  <text x="60" y="840" font-family="monospace" font-size="10" fill="#c17fff"> 自进�?�?下一代序�?/text>

  <!-- 模型服务�?-->
  <rect x="420" y="680" width="360" height="180" rx="10" fill="#1a2a3a" stroke="#ff6b6b" stroke-width="2"/>
  <text x="600" y="705" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ff6b6b">模型服务�?(938+)</text>
  <text x="600" y="725" text-anchor="middle" font-family="Arial" font-size="10" fill="#888">ProviderPool 统一封装</text>

  <text x="450" y="750" font-family="Arial" font-size="11" fill="#aaa">智谱AI</text><text x="540" y="750" font-family="Arial" font-size="11" fill="#4ecca3">6模型</text><text x="590" y="750" font-family="Arial" font-size="10" fill="#4ecca3">�?/text>
  <text x="450" y="770" font-family="Arial" font-size="11" fill="#aaa">英伟�?/text><text x="540" y="770" font-family="Arial" font-size="11" fill="#4ecca3">192模型</text><text x="605" y="770" font-family="Arial" font-size="10" fill="#4ecca3">�?/text>
  <text x="450" y="790" font-family="Arial" font-size="11" fill="#aaa">硅基流动</text><text x="540" y="790" font-family="Arial" font-size="11" fill="#4ecca3">108模型</text><text x="605" y="790" font-family="Arial" font-size="10" fill="#4ecca3">�?/text>
  <text x="450" y="810" font-family="Arial" font-size="11" fill="#aaa">阿里百炼</text><text x="540" y="810" font-family="Arial" font-size="11" fill="#4ecca3">360模型</text><text x="605" y="810" font-family="Arial" font-size="10" fill="#4ecca3">�?/text>
  <text x="450" y="830" font-family="Arial" font-size="11" fill="#aaa">火山引擎</text><text x="540" y="830" font-family="Arial" font-size="11" fill="#ff6b6b">限流�?/text><text x="605" y="830" font-family="Arial" font-size="10" fill="#ff6b6b">�?/text>
  <text x="650" y="750" font-family="Arial" font-size="11" fill="#aaa">魔力方舟</text><text x="740" y="750" font-family="Arial" font-size="11" fill="#ff6b6b">离线</text>
  <text x="650" y="770" font-family="Arial" font-size="11" fill="#aaa">英伟达超�?/text><text x="740" y="770" font-family="Arial" font-size="11" fill="#6bcbff">225+</text>

  <!-- Benchmark -->
  <rect x="820" y="680" width="340" height="180" rx="10" fill="#1a2a3a" stroke="#ffd93d" stroke-width="2"/>
  <text x="990" y="705" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ffd93d">Benchmark 结果</text>
  <text x="990" y="725" text-anchor="middle" font-family="Arial" font-size="10" fill="#888">50�?× 10模型 实测</text>

  <text x="840" y="750" font-family="Arial" font-size="11" fill="#aaa">ACO 准确�?/text><text x="980" y="750" font-family="Arial" font-size="14" font-weight="bold" fill="#4ecca3">98%</text>
  <text x="840" y="775" font-family="Arial" font-size="11" fill="#aaa">BCO 准确�?/text><text x="980" y="775" font-family="Arial" font-size="14" font-weight="bold" fill="#4ecca3">96%</text>
  <text x="840" y="800" font-family="Arial" font-size="11" fill="#aaa">串行耗时</text><text x="980" y="800" font-family="Arial" font-size="11" fill="#ff6b6b">2141�?/text>
  <text x="840" y="825" font-family="Arial" font-size="11" fill="#aaa">并发耗时</text><text x="980" y="825" font-family="Arial" font-size="11" fill="#4ecca3">27.5�?/text>
  <text x="840" y="850" font-family="Arial" font-size="11" fill="#aaa">加速比</text><text x="980" y="850" font-family="Arial" font-size="14" font-weight="bold" fill="#ffd93d">77.9×</text>

  <!-- 路径规范 -->
  <rect x="40" y="470" width="340" height="100" rx="8" fill="#1a2a3a" stroke="#ff9f43" stroke-width="1"/>
  <text x="210" y="492" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#ff9f43">路径规范</text>
  <text x="55" y="515" font-family="monospace" font-size="10" fill="#4ecca3">�?skills/symphony/ (唯一正确路径)</text>
  <text x="55" y="535" font-family="monospace" font-size="10" fill="#ff6b6b">�?symphony-release/</text>
  <text x="55" y="555" font-family="monospace" font-size="10" fill="#ff6b6b">�?symphony_db_backup/</text>

  <!-- 底部信息 -->
  <text x="600" y="885" text-anchor="middle" font-family="Arial" font-size="11" fill="#555">最后更�? 2026-03-29 | 少府�?· 陆念�?/text>
</svg>
"""

# ============================================================================
# 写入文件
# ============================================================================
if __name__ == '__main__':
    print('Generating architecture mind map...')

    with open(SVG_PATH, 'w', encoding='utf-8') as f:
        f.write(SVG_CONTENT)
    print(f'  SVG: {SVG_PATH}')

    with open(TXT_PATH, 'w', encoding='utf-8') as f:
        f.write(ASCII_MAP)
    print(f'  TXT: {TXT_PATH}')

    print()
    print('Done! Open the SVG file in a browser to view.')

