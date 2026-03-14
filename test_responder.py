# -*- coding: utf-8 -*-
import xuyuan_responder

# 测试架构
arch = xuyuan_responder.SystemArchitecture()
print('架构父级:', arch.parent)
print('成员数:', len(arch.members))

# 测试主动响应器
active = xuyuan_responder.ActiveResponder()
print('父级响应:', active.handle_parent_call())
print('同级响应:', active.handle_peer_call())
print('即时执行:', active.immediate_execute('测试任务'))

# 测试被动响应器
passive = xuyuan_responder.PassiveResponder()
print('被动父级:', passive.handle_parent_call())

# 测试规则引擎
rule = xuyuan_responder.RuleEngine()
print('被动规则:', rule.apply_passive_rules('测试消息'))

# 测试调度器
scheduler = xuyuan_responder.Scheduler()
print('任务分类:', scheduler.classify_task('开发代码'))

# 测试执行器
executor = xuyuan_responder.Executor()
print('任务解析:', executor.parse_task('执行开发'))

print('\n=== 所有测试通过 ===')
