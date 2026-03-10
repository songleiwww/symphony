# symphony

#### 介绍
Symphony（交响）是史上最强多模型协作调度系统！支持多模型并行调用、故障转移、任务调度等功能。

#### 软件架构
- 任务调度：智能分配任务，提升效率
- 模型管理：支持23+模型（智谱、火山、NVIDIA、ModelScope等）
- 容错系统：自动故障转移，确保服务永续
- 记忆系统：短期/长期/工作/情景四种记忆
- 协作编排：多模型协同工作

#### 安装教程

1. 安装最新版本
```bash
pip install symphony-ai
```

2. 安装指定版本
```bash
pip install symphony-ai==1.0.0
```

3. 从源码安装
```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
pip install -r requirements.txt
cp config.template.py config.py
# 编辑 config.py 填入你的API密钥
```

#### 使用说明

```python
from symphony import SymphonyCore

# 创建交响实例
symphony = SymphonyCore()

# 发起协作任务
result = symphony.dispatch("帮我安排一个6人团队讨论会")

# 获取系统状态
status = symphony.get_status()
print(status)
```

#### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

#### 特技

1. 多模型并行：同时调用多个AI模型，协同工作
2. 智能容错：自动故障转移，确保服务永续
3. 任务调度：智能分配任务，提升效率
4. 模型热插拔：运行时动态切换模型
5. 负载均衡：合理分配计算资源
6. 跨平台支持：Windows/Linux/Mac全面兼容

#### 联系方式

- 邮箱: songlei_www@qq.com
- 问题反馈: GitHub Issues

---

*智韵交响，共创华章*
