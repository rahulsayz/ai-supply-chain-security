import { FastifyLoggerOptions } from 'fastify';

export const loggerConfig: FastifyLoggerOptions = {
  level: process.env.NODE_ENV === 'development' ? 'info' : 'warn'
};

export class Logger {
  private static instance: Logger;
  private isDevelopment = process.env.NODE_ENV === 'development';

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  info(message: string, data?: any): void {
    this.log('INFO', message, data);
  }

  warn(message: string, data?: any): void {
    this.log('WARN', message, data);
  }

  error(message: string, error?: any): void {
    this.log('ERROR', message, error);
  }

  debug(message: string, data?: any): void {
    if (this.isDevelopment) {
      this.log('DEBUG', message, data);
    }
  }

  private log(level: string, message: string, data?: any): void {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...(data && { data })
    };

    if (this.isDevelopment) {
      console.log(JSON.stringify(logEntry, null, 2));
    } else {
      console.log(JSON.stringify(logEntry));
    }
  }
}

export const logger = Logger.getInstance();
