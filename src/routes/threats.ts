import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { DataService } from '../services/data.service';
import { Threat, ThreatFilters, APIResult } from '../types';
import { logger } from '../utils/logger';

interface ThreatListQuery {
  severity?: number;
  vendor?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

interface ThreatDetailParams {
  id: string;
}

export async function threatRoutes(fastify: FastifyInstance) {
  const dataService = new DataService();

  // GET /api/threats
  fastify.get('/threats', async (request: FastifyRequest<{ Querystring: ThreatFilters }>, reply: FastifyReply): Promise<APIResult<Threat[]>> => {
    const startTime = Date.now();
    
    try {
      const filters: ThreatFilters = {
        severity: request.query.severity,
        vendor: request.query.vendor,
        status: request.query.status as 'active' | 'investigating' | 'resolved',
        limit: request.query.limit,
        offset: request.query.offset
      };
      
      const data = await dataService.getThreats(filters);
      const processingTime = Date.now() - startTime;
      
      logger.info('Threats list served', { 
        processingTime, 
        count: data.length,
        filters: Object.keys(filters).filter(k => filters[k as keyof ThreatFilters] !== undefined)
      });
      
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
      logger.error('Failed to serve threats list', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve threats list'
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

  // GET /api/threats/:id
  fastify.get('/threats/:id', async (request: FastifyRequest<{ Params: ThreatDetailParams }>, reply: FastifyReply): Promise<APIResult<Threat>> => {
    const startTime = Date.now();
    
    try {
      const { id } = request.params;
      const data = await dataService.getThreatById(id);
      const processingTime = Date.now() - startTime;
      
      logger.info('Threat detail served', { processingTime, threatId: id });
      
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
      logger.error('Failed to serve threat detail', error);
      
      if (error instanceof Error && error.message.includes('not found')) {
        reply.status(404);
        return {
          success: false,
          error: {
            code: 'NOT_FOUND',
            message: 'Threat not found'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            source: 'precomputed',
            processingTime: 0,
            requestId: request.id
          }
        };
      }
      
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve threat details'
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

  // GET /api/threats/summary/stats
  fastify.get('/threats/summary/stats', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const threats = await dataService.getThreats();
      
      const stats = {
        total: threats.length,
        byStatus: {
          active: threats.filter(t => t.status === 'active').length,
          investigating: threats.filter(t => t.status === 'investigating').length,
          resolved: threats.filter(t => t.status === 'resolved').length
        },
        bySeverity: {
          critical: threats.filter(t => t.severity >= 8).length,
          high: threats.filter(t => t.severity >= 6 && t.severity < 8).length,
          medium: threats.filter(t => t.severity >= 4 && t.severity < 6).length,
          low: threats.filter(t => t.severity < 4).length
        },
        byType: threats.reduce((acc, threat) => {
          acc[threat.threatType] = (acc[threat.threatType] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
        averageRiskScore: Math.round(
          threats.reduce((sum, t) => sum + t.aiRiskScore, 0) / threats.length * 100
        ) / 100
      };
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Threat summary stats served', { processingTime });
      
      return {
        success: true,
        data: stats,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve threat summary stats', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve threat summary statistics'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/threats/search
  fastify.get('/threats/search', async (request: FastifyRequest<{ Querystring: { q: string; limit?: number } }>, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const { q, limit = 10 } = request.query;
      
      if (!q || q.trim().length === 0) {
        reply.status(400);
        return {
          success: false,
          error: {
            code: 'INVALID_PARAMS',
            message: 'Search query is required'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            requestId: request.id
          }
        };
      }
      
      const threats = await dataService.getThreats();
      const searchTerm = q.toLowerCase().trim();
      
      const results = threats
        .filter(threat => 
          threat.description.toLowerCase().includes(searchTerm) ||
          threat.vendorName.toLowerCase().includes(searchTerm) ||
          threat.threatType.toLowerCase().includes(searchTerm) ||
          threat.id.toLowerCase().includes(searchTerm)
        )
        .slice(0, limit);
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Threat search completed', { processingTime, query: q, results: results.length });
      
      return {
        success: true,
        data: {
          query: q,
          results,
          total: results.length
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to perform threat search', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to perform threat search'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}
