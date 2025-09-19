import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { DataService } from '../services/data.service';
import { AnalyticsData, APIResult } from '../types';
import { logger } from '../utils/logger';

export async function analyticsRoutes(fastify: FastifyInstance) {
  const dataService = new DataService();

  // GET /api/analytics - Main analytics data endpoint
  fastify.get('/analytics', async (request: FastifyRequest, reply: FastifyReply): Promise<APIResult<AnalyticsData>> => {
    const startTime = Date.now();
    
    try {
      const data = await dataService.getAnalytics();
      const processingTime = Date.now() - startTime;
      
      logger.info('Analytics data served', { processingTime });
      
      return {
        success: true,
        data,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve analytics data', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analytics data'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/analytics/trends - Time series data for line charts
  fastify.get('/analytics/trends', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const analytics = await dataService.getAnalytics();
      const processingTime = Date.now() - startTime;
      
      logger.info('Analytics trends served', { processingTime });
      
      return {
        success: true,
        data: {
          timeSeriesData: analytics.timeSeriesData
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve analytics trends', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analytics trends'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/analytics/threat-types - Threat category distribution for pie charts
  fastify.get('/analytics/threat-types', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const analytics = await dataService.getAnalytics();
      const processingTime = Date.now() - startTime;
      
      logger.info('Analytics threat types served', { processingTime });
      
      return {
        success: true,
        data: {
          threatTypes: analytics.threatTypes
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve analytics threat types', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analytics threat types'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/analytics/attack-vectors - Attack method analysis for bar charts
  fastify.get('/analytics/attack-vectors', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const analytics = await dataService.getAnalytics();
      const processingTime = Date.now() - startTime;
      
      logger.info('Analytics attack vectors served', { processingTime });
      
      return {
        success: true,
        data: {
          attackVectors: analytics.attackVectors
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve analytics attack vectors', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analytics attack vectors'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/analytics/predictions - AI threat forecasting for line charts
  fastify.get('/analytics/predictions', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const analytics = await dataService.getAnalytics();
      const processingTime = Date.now() - startTime;
      
      logger.info('Analytics predictions served', { processingTime });
      
      return {
        success: true,
        data: {
          predictions: analytics.predictions
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve analytics predictions', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analytics predictions'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });
}
