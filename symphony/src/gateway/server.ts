/**
 * API网关服务器
 * 提供REST API接口访问内核能力
 */

import express from 'express';
import cors from 'cors';
import { ModelScheduler } from '../scheduler/scheduler';
import { Logger } from '../core/logger';
import { CompletionRequest, CompletionResponse } from '../scheduler/types';

export class GatewayServer {
  private app: express.Application;
  private scheduler: ModelScheduler;
  private logger: Logger;
  private server: any;

  constructor(scheduler: ModelScheduler, logger: Logger) {
    this.scheduler = scheduler;
    this.logger = logger;
    this.app = this.setupRoutes();
  }

  private setupRoutes(): express.Application {
    const app = express();

    app.use(cors());
    app.use(express.json());

    // 健康检查
    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development',
      });
    });

    // 获取所有可用模型
    app.get('/models', (req, res) => {
      const models = this.scheduler.getAvailableModels();
      res.json({ models });
    });

    // 获取模型状态
    app.get('/models/:id', (req, res) => {
      const status = this.scheduler.getModelStatus(req.params.id);
      if (!status) {
        return res.status(404).json({ error: 'Model not found' });
      }
      res.json(status);
    });

    // 文本补全
    app.post('/completion', async (req, res) => {
      const request: CompletionRequest = req.body;

      const model = this.scheduler.selectModel(request);
      if (!model) {
        return res.status(503).json({ error: 'No available model' });
      }

      try {
        // TODO: 实际调用模型提供商API
        const startTime = Date.now();
        const response: CompletionResponse = {
          text: `[${model.provider}:${model.modelName}] Received: ${request.prompt}`,
          modelId: model.id,
          provider: model.provider,
          usage: {
            promptTokens: request.prompt.length / 4,
            completionTokens: 10,
            totalTokens: request.prompt.length / 4 + 10,
          },
          latencyMs: Date.now() - startTime,
        };

        res.json(response);
      } catch (err) {
        this.logger.error('Completion failed', err);
        res.status(500).json({ error: 'Completion failed' });
      }
    });

    // 系统信息
    app.get('/info', (req, res) => {
      res.json({
        name: 'symphony-ai-kernel',
        version: '0.1.0',
        description: '序境Symphony AI 内核',
        environment: process.env.NODE_ENV || 'development',
        port: process.env.PORT,
      });
    });

    return app;
  }

  async start(port: number): Promise<void> {
    this.logger.debug(`启动API网关，端口: ${port}`);

    return new Promise((resolve) => {
      this.server = this.app.listen(port, () => {
        this.logger.info(`API网关已启动: http://localhost:${port}`);
        resolve();
      });
    });
  }

  async stop(): Promise<void> {
    if (this.server) {
      return new Promise((resolve) => {
        this.server.close(() => {
          this.logger.debug('API网关已停止');
          resolve();
        });
      });
    }
  }

  getApp(): express.Application {
    return this.app;
  }
}
