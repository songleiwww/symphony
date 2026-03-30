/**
 * 模型调度器类型定义
 */

export enum ModelProvider {
  OpenAI = 'openai',
  Anthropic = 'anthropic',
  Volcengine = 'volcengine',
  DeepSeek = 'deepseek',
  Moonshot = 'moonshot',
  Ollama = 'ollama',
  OpenRouter = 'openrouter',
}

export enum ModelMode {
  Chat = 'chat',
  Completion = 'completion',
  Embedding = 'embedding',
}

export interface ModelConfig {
  id: string;
  provider: ModelProvider;
  modelName: string;
  apiKey?: string;
  endpoint?: string;
  mode: ModelMode;
  maxTokens: number;
  temperature: number;
  enabled: boolean;
  isProduction: boolean;
}

export interface CompletionRequest {
  prompt: string;
  modelId?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface CompletionResponse {
  text: string;
  modelId: string;
  provider: ModelProvider;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  latencyMs: number;
}

export interface ModelStatus {
  id: string;
  config: ModelConfig;
  healthy: boolean;
  totalRequests: number;
  averageLatencyMs: number;
  lastUsed: Date | null;
}
