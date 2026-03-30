/**
 * 生产模式启动脚本
 * 端口: 18789
 */

require('dotenv').config({ path: '.env.production' });
const Symphony = require('../dist/index').default;

const port = parseInt(process.env.PORT || '18789', 10);
const symphony = new Symphony();

symphony.start(port).catch(err => {
  console.error('生产模式启动失败:', err);
  process.exit(1);
});

// 处理退出信号
process.on('SIGINT', async () => {
  await symphony.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await symphony.stop();
  process.exit(0);
});
