import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { DataService } from '../services/data.service';
import { Vendor, VendorFilters, APIResult } from '../types';
import { logger } from '../utils/logger';

interface VendorDetailParams {
  id: string;
}

interface VendorListQuery {
  riskLevel?: string;
  limit?: number;
  offset?: number;
}

export async function vendorRoutes(fastify: FastifyInstance) {
  const dataService = new DataService();

  // GET /api/vendors
  fastify.get('/vendors', async (request: FastifyRequest<{ Querystring: VendorFilters }>, reply: FastifyReply): Promise<APIResult<Vendor[]>> => {
    const startTime = Date.now();
    
    try {
      const { riskLevel, limit, offset } = request.query;
      let vendors = await dataService.getVendors();
      
      // Apply filters
      if (riskLevel) {
        vendors = vendors.filter(v => v.riskLevel === riskLevel);
      }
      
      // Apply pagination
      if (offset !== undefined) {
        vendors = vendors.slice(offset);
      }
      
      if (limit !== undefined) {
        vendors = vendors.slice(0, limit);
      }
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Vendors list served', { 
        processingTime, 
        count: vendors.length,
        filters: { riskLevel, limit, offset }
      });
      
      return {
        success: true,
        data: vendors,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve vendors list', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve vendors list'
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

  // GET /api/vendors/:id
  fastify.get('/vendors/:id', async (request: FastifyRequest<{ Params: VendorDetailParams }>, reply: FastifyReply): Promise<APIResult<Vendor>> => {
    const startTime = Date.now();
    
    try {
      const { id } = request.params;
      const data = await dataService.getVendorById(id);
      const processingTime = Date.now() - startTime;
      
      logger.info('Vendor detail served', { processingTime, vendorId: id });
      
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
      logger.error('Failed to serve vendor detail', error);
      
      if (error instanceof Error && error.message.includes('not found')) {
        reply.status(404);
        return {
          success: false,
          error: {
            code: 'NOT_FOUND',
            message: 'Vendor not found'
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
          message: 'Failed to retrieve vendor details'
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

  // GET /api/vendors/risk-matrix
  fastify.get('/vendors/risk-matrix', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const vendors = await dataService.getVendors();
      
      const riskMatrix = {
        total: vendors.length,
        byRiskLevel: {
          critical: vendors.filter(v => v.riskLevel === 'critical'),
          high: vendors.filter(v => v.riskLevel === 'high'),
          medium: vendors.filter(v => v.riskLevel === 'medium'),
          low: vendors.filter(v => v.riskLevel === 'low')
        },
        riskDistribution: {
          critical: vendors.filter(v => v.riskLevel === 'critical').length,
          high: vendors.filter(v => v.riskLevel === 'high').length,
          medium: vendors.filter(v => v.riskLevel === 'medium').length,
          low: vendors.filter(v => v.riskLevel === 'low').length
        },
        averageRiskScore: Math.round(
          vendors.reduce((sum, v) => sum + v.riskScore, 0) / vendors.length * 100
        ) / 100,
        complianceSummary: vendors.reduce((acc, vendor) => {
          vendor.complianceStatus.forEach(status => {
            acc[status] = (acc[status] || 0) + 1;
          });
          return acc;
        }, {} as Record<string, number>)
      };
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Vendor risk matrix served', { processingTime });
      
      return {
        success: true,
        data: riskMatrix,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'precomputed',
          processingTime
        }
      };
    } catch (error) {
      logger.error('Failed to serve vendor risk matrix', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve vendor risk matrix'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/vendors/summary/stats
  fastify.get('/vendors/summary/stats', async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const vendors = await dataService.getVendors();
      
      const stats = {
        total: vendors.length,
        riskLevels: {
          critical: vendors.filter(v => v.riskLevel === 'critical').length,
          high: vendors.filter(v => v.riskLevel === 'high').length,
          medium: vendors.filter(v => v.riskLevel === 'medium').length,
          low: vendors.filter(v => v.riskLevel === 'low').length
        },
        riskScores: {
          average: Math.round(
            vendors.reduce((sum, v) => sum + v.riskScore, 0) / vendors.length * 100
          ) / 100,
          highest: Math.max(...vendors.map(v => v.riskScore)),
          lowest: Math.min(...vendors.map(v => v.riskScore))
        },
        threatCounts: {
          total: vendors.reduce((sum, v) => sum + v.threatCount, 0),
          average: Math.round(
            vendors.reduce((sum, v) => sum + v.threatCount, 0) / vendors.length * 100
          ) / 100
        }
      };
      
      const processingTime = Date.now() - startTime;
      
      logger.info('Vendor summary stats served', { processingTime });
      
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
      logger.error('Failed to serve vendor summary stats', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve vendor summary statistics'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}
