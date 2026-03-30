/**
 * 多模型示例数据 - 用于多脑合作测试
 */

import { ModelScheduler } from '../scheduler/scheduler';
import { ModelConfig, ModelProvider, ModelMode } from '../scheduler/types';

export function seedTestModels(scheduler: ModelScheduler): void {
  const testModels: ModelConfig[] = [
    {
      id: 'volcengine-ark-code-latest',
      provider: ModelProvider.Volcengine,
      modelName: 'ark-code-latest',
      mode: ModelMode.Chat,
      maxTokens: 4096,
      temperature: 0.7,
      enabled: true,
      isProduction: true,
    },
    {
      id: 'openai-gpt-4o',
      provider: ModelProvider.OpenAI,
      modelName: 'gpt-4o',
      mode: ModelMode.Chat,
      maxTokens: 4096,
      temperature: 0.7,
      enabled: true,
      isProduction: true,
    },
    {
      id: 'anthropic-claude-3-5-sonnet',
      provider: ModelProvider.Anthropic,
      modelName: 'claude-3-5-sonnet-20240620',
      mode: ModelMode.Chat,
      maxTokens: 200000,
      temperature: 0.5,
      enabled: true,
      isProduction: true,
    },
    {
      id: 'deepseek-chat-dev',
      provider: ModelProvider.DeepSeek,
      modelName: 'deepseek-chat',
      mode: ModelMode.Chat,
      maxTokens: 4096,
      temperature: 0.7,
      enabled: true,
      isProduction: false,
    },
    {
      id: 'ollama-llama3',
      provider: ModelProvider.Ollama,
      modelName: 'llama3:8b',
      mode: ModelMode.Chat,
      maxTokens: 4096,
      temperature: 0.7,
      enabled: true,
      isProduction: false,
    },
  ];

  testModels.forEach((model) => scheduler.registerModel(model));
}
