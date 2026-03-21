// 序境系统 - 多模型协作协议
// 遵循多模型协作原则：任何任务优先多模型组合完成

class MultiModelCollaboration {
  constructor(scheduler) {
    this.scheduler = scheduler;
    this.contextStore = new Map();
  }

  // 上下文共享
  shareContext(taskId, modelId, context) {
    if (!this.contextStore.has(taskId)) {
      this.contextStore.set(taskId, new Map());
    }
    this.contextStore.get(taskId).set(modelId, context);
  }

  // 获取共享上下文
  getSharedContext(taskId) {
    if (!this.contextStore.has(taskId)) {
      return {};
    }
    const contexts = {};
    this.contextStore.get(taskId).forEach((ctx, modelId) => {
      contexts[modelId] = ctx;
    });
    return contexts;
  }

  // 分割任务为多个子任务
  splitTask(mainTask) {
    const { content, requirements } = mainTask;
    const subtasks = [];

    // 根据需求分割
    // 1. 推理任务 -> 推理模型
    // 2. 代码 -> 代码模型  
    // 3. 对话 -> 对话模型
    // 4. 图像 -> 视觉模型

    if (requirements.reasoning) {
      subtasks.push({
        name: '深度推理',
        type: '数学推理',
        provider: requirements.reasoning.provider || '魔力方舟',
        role: 'reasoning'
      });
    }

    if (requirements.code) {
      subtasks.push({
        name: '代码生成',
        type: '代码生成',
        provider: requirements.code.provider || '火山引擎',
        role: 'coding'
      });
    }

    if (requirements.chat) {
      subtasks.push({
        name: '对话整合',
        type: '对话',
        provider: requirements.chat.provider || '火山引擎',
        role: 'synthesis'
      });
    }

    if (requirements.vision) {
      subtasks.push({
        name: '视觉理解',
        type: '视觉理解',
        provider: requirements.vision.provider || '硅基流动',
        role: 'vision'
      });
    }

    return subtasks;
  }

  // 合并多个模型的结果
  combineResults(subtaskResults) {
    // 根据子任务角色合并结果
    const combined = {
      reasoning: null,
      code: null,
      synthesis: null,
      vision: null,
      finalOutput: ''
    };

    subtaskResults.forEach(result => {
      combined[result.role] = result.output;
    });

    // 最终整合由对话模型完成
    if (combined.synthesis) {
      combined.finalOutput = combined.synthesis;
    } else {
      // 手动合并
      combined.finalOutput = Object.values(subtaskResults)
        .map(r => r.output)
        .join('\n\n');
    }

    return combined;
  }

  // 执行完整多模型协作流程
  async execute(mainTask) {
    const subtasks = this.splitTask(mainTask);
    const executionPlan = await this.scheduler.scheduleTask({
      requiredModels: subtasks.map(st => ({
        provider: st.provider,
        modelType: st.type
      }))
    });

    const results = await this.scheduler.executeTask(
      mainTask.taskId,
      executionPlan,
      async (modelConfig) => {
        // 这里执行实际模型调用
        // 返回结果和角色
        const subtask = subtasks.find(st => st.provider === modelConfig.服务商 && st.type === modelConfig.模型类型);
        const context = this.getSharedContext(mainTask.taskId);
        
        // 调用模型
        const output = await this.callModel(modelConfig, mainTask.content, context);
        
        // 保存结果到上下文
        this.shareContext(mainTask.taskId, modelConfig.模型标识符, output);
        
        return {
          role: subtask.role,
          model: modelConfig.模型名称,
          provider: modelConfig.服务商,
          output
        };
      }
    );

    return this.combineResults(results);
  }

  // 调用模型API (占位, 实际实现由具体模块完成)
  async callModel(modelConfig, content, context) {
    // 实际实现会使用 modelConfig.API地址 和 modelConfig.API密钥 调用
    throw new Error('Model call implementation must be provided by API module');
  }
}

module.exports = MultiModelCollaboration;
