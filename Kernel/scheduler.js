// 序境系统 - 统一决策层核心框架
// Agent 任务调度中枢

const { Database } = require('sqlite3');
const path = require('path');

class SchedulerCentral {
  constructor(dbPath) {
    this.dbPath = dbPath || path.join(__dirname, '../data/symphony.db');
    this.runningTasks = new Map();
    this.queue = [];
    this.concurrency = {
      sameProvider: 1,  // 同服务商顺序排队
      crossProvider: 4  // 不同服务商可并发
    };
  }

  // 从数据库读取最新模型配置
  async loadModelConfig() {
    return new Promise((resolve, reject) => {
      const db = new Database(this.dbPath);
      db.all('SELECT * FROM "模型配置表" WHERE "在线状态" = ?', ['online'], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
        db.close();
      });
    });
  }

  // 获取可用模型按服务商分组
  async getModelsByProvider() {
    const models = await this.loadModelConfig();
    const grouped = {};
    models.forEach(model => {
      const provider = model.服务商;
      if (!grouped[provider]) {
        grouped[provider] = [];
      }
      grouped[provider].push(model);
    });
    return grouped;
  }

  // 多模型调度协议 - 根据任务分配到不同模型
  async scheduleTask(task) {
    const { type, requiredModels } = task;
    const modelsByProvider = await this.getModelsByProvider();
    
    // 调度规则:
    // 1. 同服务商顺序执行，不同服务商可并发
    // 2. 根据模型类型匹配任务需求
    const executionPlan = [];
    
    requiredModels.forEach(req => {
      const provider = req.provider;
      const modelType = req.modelType;
      const availableModels = modelsByProvider[provider] || [];
      const matched = availableModels.find(m => m.模型类型 === modelType);
      if (matched) {
        executionPlan.push({
          model: matched,
          provider: provider
        });
      }
    });
    
    return this.planExecution(executionPlan);
  }

  // 规划执行顺序
  planExecution(executionPlan) {
    // 按服务商分组
    const byProvider = {};
    executionPlan.forEach(item => {
      if (!byProvider[item.provider]) {
        byProvider[item.provider] = [];
      }
      byProvider[item.provider].push(item);
    });
    
    // 同服务商顺序，不同服务商并发
    const batches = [];
    Object.values(byProvider).forEach(provItems => {
      provItems.forEach(item => {
        batches.push([item]); // 同服务商每个任务一个批次，顺序执行
      });
    });
    
    return {
      batches,
      total: executionPlan.length
    };
  }

  // 执行任务
  async executeTask(taskId, executionPlan, handler) {
    this.runningTasks.set(taskId, {
      status: 'running',
      startedAt: Date.now()
    });

    const results = [];
    for (const batch of executionPlan.batches) {
      // 每个批次执行（同服务商顺序）
      const batchResults = await Promise.all(
        batch.map(async item => {
          return await handler(item.model);
        })
      );
      results.push(...batchResults);
    }

    this.runningTasks.set(taskId, {
      status: 'completed',
      completedAt: Date.now(),
      results
    });

    return results;
  }

  // 获取健康状态
  async getHealthStatus() {
    return new Promise((resolve, reject) => {
      const db = new Database(this.dbPath);
      db.all('SELECT 服务商, 在线状态, COUNT(*) as count FROM "模型配置表" GROUP BY 服务商, 在线状态', (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
        db.close();
      });
    });
  }
}

module.exports = SchedulerCentral;
