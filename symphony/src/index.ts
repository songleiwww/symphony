/**
 * 序境 Symphony AI 内核
 * 入口文件
 */

import { SymphonyKernel } from './core/kernel';
import { ModelScheduler } from './scheduler/scheduler';
import { GatewayServer } from './gateway/server';
import { Logger } from './core/logger';
import { seedTestModels } from './examples/seed-models';

export class Symphony {
  private kernel: SymphonyKernel;
  private scheduler: ModelScheduler;
  private gateway: GatewayServer;
  private logger: Logger;

  constructor() {
    this.logger = new Logger();
    this.kernel = new SymphonyKernel(this.logger);
    this.scheduler = new ModelScheduler(this.logger);
    this.gateway = new GatewayServer(this.scheduler, this.logger);
    
    // 开发模式加载测试模型（多脑合作测试）
    if (process.env.NODE_ENV === 'development') {
      seedTestModels(this.scheduler);
    }
  }

  async start(port: number): Promise<void> {
    this.logger.info('🎻 序境 Symphony AI 内核启动中...');
    this.logger.info(`🔧 环境: ${process.env.NODE_ENV || 'development'}`);
    this.logger.info(`🚪 端口: ${port}`);

    await this.kernel.initialize();
    await this.scheduler.initialize();
    await this.gateway.start(port);

    this.logger.info('✅ 序境 Symphony AI 内核启动完成');
  }

  async stop(): Promise<void> {
    this.logger.info('🛑 序境 Symphony AI 内核停止中...');
    await this.gateway.stop();
    await this.scheduler.shutdown();
    await this.kernel.shutdown();
    this.logger.info('✅ 序境 Symphony AI 内核已停止');
  }
}

export default Symphony;

// 直接启动
if (require.main === module) {
  const port = parseInt(process.env.PORT || '18901', 10);
  const symphony = new Symphony();
  symphony.start(port).catch(err => {
    console.error('内核启动失败:', err);
    process.exit(1);
  });
}
