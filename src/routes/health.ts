import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { BigQueryService } from '../services/bigquery.service';
import { DataService } from '../services/data.service';
import { HealthResponse } from '../types';
import { logger } from '../utils/logger';

export async function healthRoutes(fastify: FastifyInstance) {
  const bigqueryService = new BigQueryService();
  const dataService = new DataService();

  // GET /api/health
  fastify.get('/health', {
    schema: {
      tags: ['Health'],
      summary: 'Get system health status',
      description: 'Returns overall system health including data files, BigQuery status, and memory usage',
      response: {
        200: {
          description: 'Health status retrieved successfully',
          type: 'object',
          properties: {
            status: { type: 'string', enum: ['healthy', 'degraded'] },
            timestamp: { type: 'string', format: 'date-time' },
            dataFiles: {
              type: 'object',
              properties: {
                loaded: { type: 'number' },
                total: { type: 'number' }
              }
            },
            bigquery: {
              type: 'object',
              properties: {
                connected: { type: 'boolean' }
              }
            },
            memory: {
              type: 'object',
              properties: {
                used: { type: 'number' },
                total: { type: 'number' },
                percentage: { type: 'number' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply): Promise<HealthResponse> => {
    const startTime = Date.now();
    
    try {
      // Get data file status
      const dataFileInfo = dataService.getDataFileInfo();
      const loadedFiles = dataFileInfo.filter(f => f.loaded).length;
      const totalFiles = dataFileInfo.length;
      
      // Get BigQuery status (optional)
      let bigqueryStatus: { connected: boolean } | undefined;
      if (bigqueryService.isAvailable()) {
        const connectionStatus = await bigqueryService.getConnectionStatus();
        bigqueryStatus = { connected: connectionStatus.connected };
      }
      
      // Get memory usage
      const memoryUsage = process.memoryUsage();
      const memory = {
        used: Math.round(memoryUsage.heapUsed / 1024 / 1024), // MB
        total: Math.round(memoryUsage.heapTotal / 1024 / 1024), // MB
        percentage: Math.round((memoryUsage.heapUsed / memoryUsage.heapTotal) * 100)
      };
      
      // Determine overall status
      const status: 'healthy' | 'degraded' = 
        (loadedFiles / totalFiles) >= 0.8 && memory.percentage < 90 ? 'healthy' : 'degraded';
      
      const response: HealthResponse = {
        status,
        timestamp: new Date().toISOString(),
        dataFiles: { loaded: loadedFiles, total: totalFiles },
        bigquery: bigqueryStatus,
        memory
      };
      
      const processingTime = Date.now() - startTime;
      logger.info('Health check completed', { 
        status, 
        processingTime, 
        loadedFiles, 
        totalFiles,
        memoryUsage: memory.percentage + '%'
      });
      
      return response;
    } catch (error) {
      logger.error('Health check failed', error);
      
      const response: HealthResponse = {
        status: 'degraded',
        timestamp: new Date().toISOString(),
        dataFiles: { loaded: 0, total: 0 },
        memory: {
          used: 0,
          total: 0,
          percentage: 0
        }
      };
      
      return response;
    }
  });

  // GET /api/health/data-files
  fastify.get('/health/data-files', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const dataFileInfo = dataService.getDataFileInfo();
      const cacheStats = dataService.getCacheStats();
      
      return {
        success: true,
        data: {
          files: dataFileInfo,
          cache: cacheStats
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0
        }
      };
    } catch (error) {
      logger.error('Failed to get data file info', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve data file information'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/health/bigquery
  fastify.get('/health/bigquery', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      if (!bigqueryService.isAvailable()) {
        return {
          success: true,
          data: {
            available: false,
            message: 'BigQuery service not configured'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            source: 'precomputed',
            processingTime: 0
          }
        };
      }
      
      const connectionStatus = await bigqueryService.getConnectionStatus();
      const projectInfo = await bigqueryService.getProjectInfo();
      
      return {
        success: true,
        data: {
          available: true,
          connected: connectionStatus.connected,
          projectId: connectionStatus.projectId,
          projectInfo
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'live',
          processingTime: 0
        }
      };
    } catch (error) {
      logger.error('Failed to get BigQuery health info', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve BigQuery health information'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}
