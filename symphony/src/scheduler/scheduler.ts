/**
 * 多模型调度器
 * 负责调度所有配置的AI模型，支持负载均衡和故障转移
 */

import { Logger } from '../core/logger';
import { ModelConfig, ModelStatus, CompletionRequest, CompletionResponse } from './types';

export class ModelScheduler {
  private logger: Logger;
  private models: Map<string, ModelConfig> = new Map();
  private initialized: boolean = false;

  constructor(logger: Logger) {
    this.logger = logger;
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      this.logger.warn('模型调度器已经初始化');
      return;
    }

    this.logger.debug('初始化多模型调度器');

    // 从配置加载所有模型
    // 这里预留扩展点，后续从配置文件/数据库加载

    this.initialized = true;
    this.logger.debug(`多模型调度器初始化完成，已加载 ${this.models.size} 个模型`);
  }

  /**
   * 注册一个模型
   */
  registerModel(config: ModelConfig): void {
    this.models.set(config.id, config);
    this.logger.debug(`注册模型: ${config.id} (${config.provider}/${config.modelName})`);
  }

  /**
   * 注销一个模型
   */
  unregisterModel(modelId: string): void {
    if (this.models.delete(modelId)) {
      this.logger.debug(`注销模型: ${modelId}`);
    }
  }

  /**
   * 获取所有可用模型
   */
  getAvailableModels(): ModelConfig[] {
    return Array.from(this.models.values()).filter((m) => m.enabled);
  }

  /**
   * 根据环境获取模型列表
   * 生产环境只返回生产模式模型
   */
  getModelsForCurrentEnvironment(): ModelConfig[] {
    const isProd = process.env.NODE_ENV === 'production';
    return this.getAvailableModels().filter((m) => m.isProduction === isProd);
  }

  /**
   * 获取模型状态
   */
  getModelStatus(modelId: string): ModelStatus | null {
    const config = this.models.get(modelId);
    if (!config) return null;

    // 这里简化，实际需要统计健康状况
    return {
      id: modelId,
      config,
      healthy: true,
      totalRequests: 0,
      averageLatencyMs: 0,
      lastUsed: null,
    };
  }

  /**
   * 获取所有模型状态
   */
  getAllModelStatus(): ModelStatus[] {
    return Array.from(this.models.keys()).map((id) => this.getModelStatus(id)!);
  }

  /**
   * 选择一个模型执行推理
   * 简单策略：轮询/加权选择
   */
  selectModel(request: CompletionRequest): ModelConfig | null {
    const available = this.getModelsForCurrentEnvironment();

    if (request.modelId) {
      return this.models.get(request.modelId) || null;
    }

    // 默认返回第一个可用模型
    // 实际可以实现更复杂的调度策略：
    // - 基于负载的选择
    // - 基于模型能力的匹配
    // - 故障转移
    return available.length > 0 ? available[0] : null;
  }

  async shutdown(): Promise<void> {
    if (!this.initialized) return;

    this.logger.debug('关闭模型调度器');
    this.initialized = false;
    this.logger.debug('模型调度器已关闭');
  }
}
