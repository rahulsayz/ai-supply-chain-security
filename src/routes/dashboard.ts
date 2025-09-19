import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { DataService } from '../services/data.service';
import { DashboardOverview, APIResult } from '../types';
import { logger } from '../utils/logger';

export async function dashboardRoutes(fastify: FastifyInstance) {
  const dataService = new DataService();

  // GET /api/dashboard/overview
  fastify.get('/dashboard/overview', {
    schema: {
      tags: ['Dashboard'],
      summary: 'Get executive dashboard overview',
      description: 'Returns high-level metrics and summary for executive dashboard',
      response: {
        200: {
          description: 'Dashboard overview retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'object',
              properties: {
                totalThreats: { type: 'number' },
                activeThreats: { type: 'number' },
                criticalVendors: { type: 'number' },
                riskTrend: { type: 'string', enum: ['increasing', 'decreasing', 'stable'] },
                topThreatTypes: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      type: { type: 'string' },
                      count: { type: 'number' },
                      percentage: { type: 'number' }
                    }
                  }
                }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                source: { type: 'string', enum: ['precomputed', 'live'] },
                processingTime: { type: 'number' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply): Promise<APIResult<DashboardOverview>> => {
    const startTime = Date.now();
    
    try {
      const data = await dataService.getDashboardOverview();
      const processingTime = Date.now() - startTime;
      
      logger.info('Dashboard overview served', { processingTime });
      
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
      logger.error('Failed to serve dashboard overview', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve dashboard overview'
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

  // GET /api/dashboard/summary
  fastify.get('/dashboard/summary', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const overview = await dataService.getDashboardOverview();
      const threats = await dataService.getThreats({ limit: 5 });
      const vendors = await dataService.getVendors();
      
      const summary = {
        metrics: {
          totalThreats: overview.totalThreats,
          activeThreats: overview.activeThreats,
          criticalVendors: overview.criticalVendors,
          riskTrend: overview.riskTrend
        },
        recentActivity: {
          threats: threats.slice(0, 3),
          highRiskVendors: vendors.filter(v => v.riskLevel === 'high' || v.riskLevel === 'critical').slice(0, 3)
        },
        alerts: overview.recentAlerts
      };
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Dashboard summary served', { processingTime });
      
      return {
        success: true,
        data: summary,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve dashboard summary', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve dashboard summary'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/dashboard/metrics
  fastify.get('/dashboard/metrics', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const overview = await dataService.getDashboardOverview();
      const analytics = await dataService.getAnalytics();
      
      const metrics = {
        threatMetrics: {
          total: overview.totalThreats,
          active: overview.activeThreats,
          resolved: overview.totalThreats - overview.activeThreats,
          critical: overview.topThreatTypes.find(t => t.type === 'critical')?.count || 0
        },
        vendorMetrics: {
          total: overview.criticalVendors * 3, // Estimate based on critical vendors
          critical: overview.criticalVendors,
          highRisk: Math.floor(overview.criticalVendors * 1.5)
        },
        riskMetrics: {
          trend: overview.riskTrend,
          distribution: analytics.threatTypes,
          topThreatTypes: overview.topThreatTypes
        }
      };
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Dashboard metrics served', { processingTime });
      
      return {
        success: true,
        data: metrics,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve dashboard metrics', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve dashboard metrics'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}
