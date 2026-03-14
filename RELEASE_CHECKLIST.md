# Symphony Release Checklist - 交响发布检查清单

## Before Every Release - 每次发布前

### Quality Checks - 质量检查

- [ ] **All tests pass** - 所有测试通过
  - Run: `python simple_test.py`
  - Run: `python symphony_self_test.py`
  - Run: `python test_phase1.py`

- [ ] **No sensitive data in commits** - 提交中没有敏感数据
  - Check: config.py has placeholder keys
  - Check: No API keys, passwords, tokens in any file
  - Check: OpenClaw config not committed

- [ ] **Documentation updated** - 文档已更新
  - Check: README.md is current
  - Check: QUICKSTART.md is current
  - Check: examples/README.md is current

- [ ] **Model reporting works** - 模型报告正常工作
  - Check: All examples show model usage
  - Check: Detailed model reports are included

- [ ] **Memory system functions** - 记忆系统正常工作
  - Check: memory_system.py loads
  - Check: Long-term memory is created/loaded

### Automation Checks - 自动化检查

- [ ] **Run self-tests on every change** - 每次更改运行自测试
  - Run: `python symphony_self_test.py`

- [ ] **Check for sensitive data pre-commit** - 提交前检查敏感数据
  - Verify: No real keys in config.py
  - Verify: No personal data in files

- [ ] **Validate model configuration** - 验证模型配置
  - Check: 17 models loaded
  - Check: Priority order correct

- [ ] **Verify memory system integrity** - 验证记忆系统完整性
  - Check: Memory files are valid JSON
  - Check: No corruption

---

## Quality Standards - 质量标准

1. **100% test pass rate target** - 目标 100% 测试通过率
2. **Zero sensitive data leakage** - 零敏感数据泄露
3. **Clear documentation for all features** - 所有功能都有清晰文档
4. **Graceful error handling** - 优雅的错误处理

---

## How to Use - 如何使用

1. Copy this checklist before release
2. Check each item as you complete it
3. Only release when ALL boxes are checked
4. Keep a record of checked checklists

---

*智韵交响，共创华章*
