/**
 * 日志模块
 * 统一日志输出，支持不同级别
 */

import winston from 'winston';

const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

export class Logger {
  private logger: winston.Logger;

  constructor() {
    const level = process.env.LOG_LEVEL || 'info';
    
    this.logger = winston.createLogger({
      level,
      levels: logLevels,
      format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message }) => {
          return `[${timestamp}] ${level}: ${message}`;
        })
      ),
      transports: [
        new winston.transports.Console(),
      ],
    });
  }

  error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }

  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }

  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }
}
