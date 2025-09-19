import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { AIDashboardService } from '../services/ai-dashboard.service';
import { logger } from '../utils/logger';
import { 
  PredictedThreat, 
  AIProcessingStep, 
  AIInsight, 
  AIImpactMetrics, 
  AIExecutiveSummary,
  AIAnalysisRequest,
  AIAnalysisResponse
} from '../types';

export async function aiDashboardRoutes(fastify: FastifyInstance) {
  const aiDashboardService = new AIDashboardService();

  // GET /api/ai/predicted-threats - Get AI threat predictions for next 30 days
  fastify.get('/ai/predicted-threats', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get AI threat predictions',
      description: 'Returns AI-generated threat predictions for the next 30 days with reasoning and recommendations',
      querystring: {
        type: 'object',
        properties: {
          vendorId: { type: 'string', description: 'Optional vendor ID to filter predictions' }
        }
      },
      response: {
        200: {
          description: 'AI threat predictions retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  vendorName: { type: 'string' },
                  probability: { type: 'number' },
                  threatType: { type: 'string' },
                  aiReasoning: { type: 'string' },
                  recommendedAction: { type: 'string' },
                  potentialImpact: { type: 'string' },
                  timeframe: { type: 'string' },
                  confidence: { type: 'number' },
                  riskScore: { type: 'number' }
                }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest<{ Querystring: { vendorId?: string } }>, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const { vendorId } = request.query;
      const predictions = await aiDashboardService.generateThreatPredictions(vendorId);
      const processingTime = Date.now() - startTime;
      
      logger.info('AI threat predictions served', { vendorId, processingTime, count: predictions.length });
      
      return {
        success: true,
        data: predictions,
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime,
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to serve AI threat predictions', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve AI threat predictions'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/ai/processing-steps/:analysisId - Get real-time AI processing steps
  fastify.get('/ai/processing-steps/:analysisId', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get AI processing steps',
      description: 'Returns real-time AI processing steps for live analysis theater',
      params: {
        type: 'object',
        properties: {
          analysisId: { type: 'string', description: 'Analysis ID to get processing steps for' }
        },
        required: ['analysisId']
      },
      response: {
        200: {
          description: 'AI processing steps retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  description: { type: 'string' },
                  progress: { type: 'number' },
                  status: { type: 'string', enum: ['pending', 'processing', 'completed', 'failed'] },
                  cost: { type: 'number' },
                  eta: { type: 'string' }
                }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { analysisId: string } }>, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const { analysisId } = request.params;
      const steps = await aiDashboardService.getProcessingSteps(analysisId);
      const processingTime = Date.now() - startTime;
      
      logger.info('AI processing steps served', { analysisId, processingTime, count: steps.length });
      
      return {
        success: true,
        data: steps,
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime,
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to serve AI processing steps', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve AI processing steps'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/ai/insights/:analysisId - Get AI-generated insights
  fastify.get('/ai/insights/:analysisId', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get AI insights',
      description: 'Returns AI-generated insights for live analysis theater',
      params: {
        type: 'object',
        properties: {
          analysisId: { type: 'string', description: 'Analysis ID to get insights for' }
        },
        required: ['analysisId']
      },
      response: {
        200: {
          description: 'AI insights retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  type: { type: 'string' },
                  message: { type: 'string' },
                  confidence: { type: 'number' },
                  timestamp: { type: 'string' },
                  impact: { type: 'string' },
                  source: { type: 'string' }
                }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { analysisId: string } }>, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const { analysisId } = request.params;
      const insights = await aiDashboardService.generateAIInsights(analysisId);
      const processingTime = Date.now() - startTime;
      
      logger.info('AI insights served', { analysisId, processingTime, count: insights.length });
      
      return {
        success: true,
        data: insights,
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime,
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to serve AI insights', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve AI insights'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/ai/impact-metrics - Get AI impact metrics
  fastify.get('/ai/impact-metrics', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get AI impact metrics',
      description: 'Returns AI impact metrics showing business value and performance improvements',
      response: {
        200: {
          description: 'AI impact metrics retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'object',
              properties: {
                preventedLosses: { type: 'number' },
                speedAdvantage: { type: 'number' },
                accuracyBoost: { type: 'number' },
                processingVolume: { type: 'number' },
                riskReduction: { type: 'number' },
                predictionSuccess: { type: 'number' },
                timeToDetection: { type: 'number' },
                analystWorkloadReduction: { type: 'number' },
                costPerInvestigation: { type: 'number' },
                traditionalCostComparison: { type: 'number' }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const metrics = await aiDashboardService.generateImpactMetrics();
      const processingTime = Date.now() - startTime;
      
      logger.info('AI impact metrics served', { processingTime });
      
      return {
        success: true,
        data: metrics,
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime,
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to serve AI impact metrics', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve AI impact metrics'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/ai/executive-summary - Get AI-generated executive summary
  fastify.get('/ai/executive-summary', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get AI executive summary',
      description: 'Returns AI-generated executive summary with business insights and recommendations',
      response: {
        200: {
          description: 'AI executive summary retrieved successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                generatedAt: { type: 'string' },
                keyFindings: { type: 'array', items: { type: 'string' } },
                aiConfidenceMetrics: { type: 'object' },
                immediateActions: { type: 'array' },
                businessImpact: { type: 'object' },
                threatPatterns: { type: 'array' },
                recommendations: { type: 'array', items: { type: 'string' } }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const startTime = Date.now();
    
    try {
      const summary = await aiDashboardService.generateExecutiveSummary();
      const processingTime = Date.now() - startTime;
      
      logger.info('AI executive summary served', { processingTime });
      
      return {
        success: true,
        data: summary,
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime,
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to serve AI executive summary', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve AI executive summary'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          requestId: request.id
        }
      };
    }
  });

  // POST /api/ai/comprehensive-analysis - Perform comprehensive AI analysis
  fastify.post('/ai/comprehensive-analysis', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Perform comprehensive AI analysis',
      description: 'Performs comprehensive AI analysis combining all dashboard components',
      body: {
        type: 'object',
        properties: {
          vendorId: { type: 'string', description: 'Optional vendor ID to focus analysis on' },
          analysisType: { 
            type: 'string', 
            enum: ['quick', 'comprehensive', 'predictive', 'executive'],
            default: 'comprehensive'
          },
          includeHistorical: { type: 'boolean', default: true },
          includePredictions: { type: 'boolean', default: true },
          timeframe: { type: 'number', description: 'Analysis timeframe in days', default: 30 }
        }
      },
      response: {
        200: {
          description: 'Comprehensive AI analysis completed successfully',
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            data: {
              type: 'object',
              properties: {
                analysisId: { type: 'string' },
                predictedThreats: { type: 'array' },
                processingSteps: { type: 'array' },
                insights: { type: 'array' },
                executiveSummary: { type: 'object' },
                impactMetrics: { type: 'object' }
              }
            },
            metadata: {
              type: 'object',
              properties: {
                timestamp: { type: 'string', format: 'date-time' },
                processingTime: { type: 'number' },
                cost: { type: 'number' },
                requestId: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }, async (request: FastifyRequest<{ Body: AIAnalysisRequest }>, reply: FastifyReply) => {
    try {
      const analysisRequest = request.body;
      const result = await aiDashboardService.performComprehensiveAnalysis(analysisRequest);
      
      if (result.success) {
        logger.info('Comprehensive AI analysis completed', { 
          analysisId: result.data?.analysisId,
          processingTime: result.metadata.processingTime,
          cost: result.metadata.cost
        });
        return result;
      } else {
        reply.status(500);
        return result;
      }
    } catch (error) {
      logger.error('Comprehensive AI analysis failed', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to perform comprehensive AI analysis'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          processingTime: 0,
          cost: 0,
          requestId: request.id
        }
      };
    }
  });

  // GET /api/ai/analysis-results/:analysisId - Get cached analysis results
  fastify.get('/ai/analysis-results/:analysisId', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Get analysis results',
      description: 'Returns cached comprehensive AI analysis results',
      params: {
        type: 'object',
        properties: {
          analysisId: { type: 'string', description: 'Analysis ID to get results for' }
        },
        required: ['analysisId']
      }
    }
  }, async (request: FastifyRequest<{ Params: { analysisId: string } }>, reply: FastifyReply) => {
    try {
      const { analysisId } = request.params;
      const results = await aiDashboardService.getAnalysisResults(analysisId);
      
      if (!results) {
        reply.status(404);
        return {
          success: false,
          error: {
            code: 'NOT_FOUND',
            message: 'Analysis results not found'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            requestId: request.id
          }
        };
      }
      
      return results;
    } catch (error) {
      logger.error('Failed to get analysis results', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to retrieve analysis results'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // PUT /api/ai/processing-steps/:analysisId/:stepId - Update processing step progress
  fastify.put('/ai/processing-steps/:analysisId/:stepId', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Update processing step',
      description: 'Updates processing step progress for real-time updates',
      params: {
        type: 'object',
        properties: {
          analysisId: { type: 'string' },
          stepId: { type: 'string' }
        },
        required: ['analysisId', 'stepId']
      },
      body: {
        type: 'object',
        properties: {
          progress: { type: 'number' },
          status: { type: 'string', enum: ['pending', 'processing', 'completed', 'failed'] },
          eta: { type: 'string' }
        }
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { analysisId: string; stepId: string };
    Body: Partial<AIProcessingStep>;
  }>, reply: FastifyReply) => {
    try {
      const { analysisId, stepId } = request.params;
      const updates = request.body;
      
      await aiDashboardService.updateProcessingStep(analysisId, stepId, updates);
      
      logger.info('Processing step updated', { analysisId, stepId, updates });
      
      return {
        success: true,
        message: 'Processing step updated successfully',
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to update processing step', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to update processing step'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // POST /api/ai/insights/:analysisId - Add new AI insight
  fastify.post('/ai/insights/:analysisId', {
    schema: {
      tags: ['AI Dashboard'],
      summary: 'Add AI insight',
      description: 'Adds new AI insight for real-time updates',
      params: {
        type: 'object',
        properties: {
          analysisId: { type: 'string' }
        },
        required: ['analysisId']
      },
      body: {
        type: 'object',
        properties: {
          type: { type: 'string', enum: ['threat', 'anomaly', 'pattern', 'recommendation', 'discovery'] },
          message: { type: 'string' },
          confidence: { type: 'number' },
          impact: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] },
          source: { type: 'string' }
        },
        required: ['type', 'message', 'confidence', 'impact', 'source']
      }
    }
  }, async (request: FastifyRequest<{ 
    Params: { analysisId: string };
    Body: Partial<AIInsight>;
  }>, reply: FastifyReply) => {
    try {
      const { analysisId } = request.params;
      const insightData = request.body;
      
      const insight: AIInsight = {
        id: `INSIGHT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        urgency: 'medium',
        ...insightData
      } as AIInsight;
      
      await aiDashboardService.addAIInsight(analysisId, insight);
      
      logger.info('AI insight added', { analysisId, insightId: insight.id });
      
      return {
        success: true,
        data: insight,
        message: 'AI insight added successfully',
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    } catch (error) {
      logger.error('Failed to add AI insight', error);
      reply.status(500);
      
      return {
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: 'Failed to add AI insight'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}
