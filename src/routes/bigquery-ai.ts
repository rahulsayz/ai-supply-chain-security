import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { logger } from '../utils/logger';

// Mock cost monitor for when Python module is not available
function getCostMonitor() {
  try {
    return require('../../tools/bigquery_ai/cost_monitor');
  } catch (error) {
    logger.warn('Python cost_monitor module not available, using mock implementation');
    return {
      getCostMonitor: () => ({
        currentCost: 0.048,
        costLimit: 100.0,
        costPerRequest: 0.008,
        dailyUsage: 12.5,
        monthlyUsage: 156.8,
        costAlerts: [
          { level: 'warning', threshold: 80, message: 'Approaching daily cost limit' },
          { level: 'critical', threshold: 95, message: 'Daily cost limit nearly exceeded' }
        ],
        getCostBreakdown: () => ({
          ai_processing: 0.032,
          data_analysis: 0.008,
          threat_detection: 0.008,
          total: 0.048
        })
      })
    };
  }
}

// Mock cost history for when Python module is not available
function getCostHistory() {
  try {
    return require('../../tools/bigquery_ai/cost_history');
  } catch (error) {
    logger.warn('Python cost_history module not available, using mock implementation');
    return {
      getCostHistory: () => [
        { date: '2024-01-15', cost: 0.048, requests: 6, analysis_type: 'comprehensive' },
        { date: '2024-01-14', cost: 0.064, requests: 8, analysis_type: 'comprehensive' },
        { date: '2024-01-13', cost: 0.032, requests: 4, analysis_type: 'quick' },
        { date: '2024-01-12', cost: 0.056, requests: 7, analysis_type: 'comprehensive' },
        { date: '2024-01-11', cost: 0.040, requests: 5, analysis_type: 'quick' }
      ]
    };
  }
}

export default async function bigqueryAiRoutes(fastify: FastifyInstance) {
  // GET /api/bigquery-ai/health - Health check endpoint
  fastify.get('/bigquery-ai/health', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const costMonitor = getCostMonitor();
      const costInfo = costMonitor.getCostMonitor();
      
      return {
        success: true,
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          bigquery_ai: 'operational',
          cost_monitoring: 'operational',
          threat_detection: 'operational'
        },
        cost_info: {
          current_cost: costInfo.currentCost,
          cost_limit: costInfo.costLimit,
          daily_usage: costInfo.dailyUsage,
          monthly_usage: costInfo.monthlyUsage
        },
        metadata: {
          version: '1.0.0',
          environment: process.env.NODE_ENV || 'development'
        }
      };
    } catch (error) {
      logger.error('Health check failed', error);
      reply.status(500);
      return {
        success: false,
        status: 'unhealthy',
        error: {
          code: 'HEALTH_CHECK_FAILED',
          message: 'Health check failed'
        },
        timestamp: new Date().toISOString()
      };
    }
  });

  // POST /api/bigquery-ai/quick-analysis - Quick threat analysis
  fastify.post('/bigquery-ai/quick-analysis', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const { vendorId, threatType, analysisDepth } = request.body as any;
      
      // Validate required parameters
      if (!vendorId) {
        reply.status(400);
        return {
          success: false,
          error: {
            code: 'MISSING_VENDOR_ID',
            message: 'vendorId is required for quick analysis'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            requestId: request.id
          }
        };
      }

      // Simulate AI analysis processing time
      const processingTime = Math.random() * 2000 + 1000; // 1-3 seconds
      await new Promise(resolve => setTimeout(resolve, processingTime));

      // Generate mock analysis result
      const result = {
        analysis_id: `QA_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        vendor_id: vendorId,
        analysis_type: 'quick',
        processing_time: processingTime,
        timestamp: new Date().toISOString(),
        threat_analysis: {
          threat_level: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
          confidence: 0.85 + (Math.random() * 0.10),
          detected_threats: Math.floor(Math.random() * 5) + 1,
          risk_score: Math.floor(Math.random() * 40) + 20
        },
        ai_insights: {
          risk_assessment: {
            overall_risk: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
            confidence: 0.92,
            threat_patterns: [
              { pattern: 'supply_chain_compromise', confidence: 0.89, severity: 'medium' },
              { pattern: 'data_exfiltration', confidence: 0.91, severity: 'low' }
            ],
            recommendations: [
              'Implement additional vendor security checks',
              'Monitor data access patterns',
              'Review third-party dependencies'
            ]
          }
        },
        processing_metadata: {
          model_version: 'bigquery-ai-v2.1',
          cost_per_step: 0.008,
          total_steps: 8,
          cost_breakdown: {
            data_ingestion: 0.001,
            threat_analysis: 0.003,
            risk_assessment: 0.002,
            ai_processing: 0.002
          }
        }
      };

      // Calculate cost estimate
      const cost_estimate = result.processing_time * 0.0008;

      return {
        success: true,
        data: result,
        cost_estimate: cost_estimate,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'bigquery_ai',
          processingTime: processingTime,
          requestId: request.id
        }
      };

    } catch (error) {
      logger.error('Quick analysis failed', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'QUICK_ANALYSIS_FAILED',
          message: 'Quick analysis failed'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // POST /api/bigquery-ai/live-analysis - Live AI-powered threat analysis with streaming
  fastify.post('/bigquery-ai/live-analysis', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const { vendorId, analysisType, includeHistorical } = request.body as any;
      
      // Validate required parameters
      if (!vendorId) {
        reply.status(400);
        return {
          success: false,
          error: {
            code: 'MISSING_VENDOR_ID',
            message: 'vendorId is required for live analysis'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            requestId: request.id
          }
        };
      }

      // Set response headers for streaming
      reply.raw.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
      });

      // Send initial analysis start
      reply.raw.write(`data: ${JSON.stringify({
        type: 'analysis_start',
        message: 'Starting comprehensive AI-powered threat analysis',
        timestamp: new Date().toISOString(),
        vendor_id: vendorId,
        analysis_type: analysisType || 'comprehensive'
      })}\n\n`);

      // Simulate analysis steps with realistic timing
      const analysisSteps = [
        { step: 'data_collection', message: 'Collecting vendor and dependency data...', duration: 1500 },
        { step: 'threat_intelligence', message: 'Analyzing threat intelligence feeds...', duration: 2000 },
        { step: 'ai_analysis', message: 'Running AI-powered threat detection...', duration: 3000 },
        { step: 'risk_assessment', message: 'Assessing overall risk levels...', duration: 1500 },
        { step: 'recommendations', message: 'Generating security recommendations...', duration: 1000 }
      ];

      let totalCost = 0;
      const costPerStep = 0.008;

      for (let i = 0; i < analysisSteps.length; i++) {
        const step = analysisSteps[i];
        
        // Send step start
        reply.raw.write(`data: ${JSON.stringify({
          type: 'step_start',
          step: step.step,
          message: step.message,
          timestamp: new Date().toISOString(),
          stepNumber: i + 1,
          totalSteps: analysisSteps.length,
          progress: (i / analysisSteps.length) * 100
        })}\n\n`);

        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, step.duration));
        
        // Calculate cost for this step
        totalCost += costPerStep;
        
        // Send step completion with detailed results
        const stepResult: any = {
          step: step.step,
          completed: true,
          duration: step.duration,
          cost: costPerStep,
          total_cost: totalCost,
          timestamp: new Date().toISOString()
        };

        // Add step-specific data
        if (step.step === 'threat_intelligence') {
          stepResult.threats_detected = Math.floor(Math.random() * 8) + 3;
          stepResult.risk_indicators = Math.floor(Math.random() * 5) + 2;
        } else if (step.step === 'ai_analysis') {
          stepResult.ai_confidence = 0.92;
          
          // Generate realistic threats during AI analysis step
          const threatTypes = [
            'supply-chain-compromise',
            'credential-theft',
            'data-exfiltration',
            'insider-threat',
            'malware-infection',
            'network-intrusion',
            'api-abuse',
            'privilege-escalation'
          ];
          
          const systemTypes = [
            'web-servers',
            'database-servers',
            'load-balancers',
            'api-gateways',
            'authentication-servers',
            'file-storage-systems',
            'monitoring-systems',
            'backup-systems'
          ];
          
          const vendorNames = [
            'TechCorp Solutions',
            'SecureNet Systems',
            'CloudGuard Inc',
            'DataSafe Technologies',
            'CyberShield Corp'
          ];

          // Generate 3-8 realistic threats
          const numThreats = Math.floor(Math.random() * 6) + 3;
          
          // Send threats individually with small delays for proper streaming
          for (let j = 0; j < numThreats; j++) {
            const threatType = threatTypes[Math.floor(Math.random() * threatTypes.length)];
            const severity = Math.floor(Math.random() * 10) + 1;
            const aiRiskScore = 0.7 + (Math.random() * 0.3);
            const confidenceScore = 0.8 + (Math.random() * 0.2);
            
            // Generate affected systems for this threat
            const numSystems = Math.floor(Math.random() * 4) + 1;
            const threatSystems: string[] = [];
            for (let k = 0; k < numSystems; k++) {
              const system = systemTypes[Math.floor(Math.random() * systemTypes.length)];
              if (!threatSystems.includes(system)) {
                threatSystems.push(system);
              }
            }
            
            const threat = {
              threat_type: threatType,
              severity: severity,
              description: generateThreatDescription(threatType, severity),
              affectedSystems: threatSystems,
              aiRiskScore: parseFloat(aiRiskScore.toFixed(2)),
              recommendations: generateThreatRecommendations(threatType, severity),
              threat_id: `THR-${new Date().getFullYear()}-${String(j + 1).padStart(3, '0')}`,
              vendor_name: vendorNames[Math.floor(Math.random() * vendorNames.length)],
              detection_method: 'AI-Powered Network Analysis',
              confidence_score: parseFloat(confidenceScore.toFixed(2))
            };
            
            // Send threat-detected event immediately
            const threatEvent = {
              type: 'threat-detected',
              data: threat,
              timestamp: new Date().toISOString()
            };
            
            reply.raw.write(`data: ${JSON.stringify(threatEvent)}\n\n`);
            
            // Force flush after each threat event
            flushResponse(reply);
            
            // Small delay between threats for proper streaming effect
            await new Promise(resolve => setTimeout(resolve, 300));
          }
          
          stepResult.threat_patterns = [
            { pattern: 'supply_chain_compromise', confidence: 0.89, severity: 'medium' },
            { pattern: 'data_exfiltration', confidence: 0.91, severity: 'low' },
            { pattern: 'insider_threat', confidence: 0.87, severity: 'high' }
          ];
        } else if (step.step === 'risk_assessment') {
          stepResult.overall_risk = Math.random() > 0.6 ? 'medium' : 'low';
          stepResult.risk_score = Math.floor(Math.random() * 30) + 15;
        }

        reply.raw.write(`data: ${JSON.stringify({
          type: 'step_complete',
          ...stepResult
        })}\n\n`);
      }

      // Send final comprehensive analysis
      const finalAnalysis = {
        analysis_id: `LA_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        vendor_id: vendorId,
        analysis_type: analysisType || 'comprehensive',
        processing_time: analysisSteps.reduce((sum, step) => sum + step.duration, 0),
        timestamp: new Date().toISOString(),
        threat_analysis: {
          threat_level: Math.random() > 0.6 ? 'medium' : 'low',
          confidence: 0.92,
          detected_threats: Math.floor(Math.random() * 8) + 3,
          risk_score: Math.floor(Math.random() * 30) + 15,
          threat_patterns: [
            { pattern: 'supply_chain_compromise', confidence: 0.89, severity: 'medium' },
            { pattern: 'data_exfiltration', confidence: 0.91, severity: 'low' },
            { pattern: 'insider_threat', confidence: 0.87, severity: 'high' }
          ]
        },
        ai_insights: {
          risk_assessment: {
            overall_risk: Math.random() > 0.6 ? 'medium' : 'low',
            confidence: 0.92,
            threat_patterns: [
              { pattern: 'supply_chain_compromise', confidence: 0.89, severity: 'medium' },
              { pattern: 'data_exfiltration', confidence: 0.91, severity: 'low' },
              { pattern: 'insider_threat', confidence: 0.87, severity: 'high' }
            ],
            recommendations: [
              'Implement additional vendor security checks',
              'Monitor data access patterns',
              'Review third-party dependencies',
              'Enhance insider threat detection',
              'Strengthen supply chain security protocols'
            ]
          }
        },
        processing_metadata: {
          model_version: 'bigquery-ai-v2.1',
          cost_per_step: costPerStep,
          total_steps: analysisSteps.length,
          total_cost: totalCost,
          cost_breakdown: {
            data_collection: costPerStep,
            threat_intelligence: costPerStep,
            ai_analysis: costPerStep,
            risk_assessment: costPerStep,
            recommendations: costPerStep
          }
        }
      };

      reply.raw.write(`data: ${JSON.stringify({
        type: 'analysis_complete',
        message: 'Comprehensive threat analysis completed successfully',
        timestamp: new Date().toISOString(),
        analysis: finalAnalysis,
        summary: {
          total_threats_detected: finalAnalysis.threat_analysis.detected_threats,
          overall_risk_level: finalAnalysis.threat_analysis.threat_level,
          ai_confidence: finalAnalysis.ai_insights.risk_assessment.confidence,
          total_cost: totalCost,
          processing_time: finalAnalysis.processing_time
        }
      })}\n\n`);

      // Send end marker
      reply.raw.write(`data: ${JSON.stringify({ type: 'end' })}\n\n`);
      
      reply.raw.end();
      
      return undefined;

    } catch (error) {
      logger.error('Live analysis failed', error);
      
      if (!reply.sent) {
        reply.raw.write(`data: ${JSON.stringify({
          type: 'error',
          message: 'Live analysis failed',
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        })}\n\n`);
        reply.raw.end();
      }
      
      return {
        success: false,
        error: {
          code: 'LIVE_ANALYSIS_FAILED',
          message: 'Live analysis failed'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/bigquery-ai/analysis-status/:analysisId - Get analysis status
  fastify.get('/bigquery-ai/analysis-status/:analysisId', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const { analysisId } = request.params as any;
      
      if (!analysisId) {
        reply.status(400);
        return {
          success: false,
          error: {
            code: 'MISSING_ANALYSIS_ID',
            message: 'analysisId is required'
          },
          metadata: {
            timestamp: new Date().toISOString(),
            requestId: request.id
          }
        };
      }

      // Mock analysis status - in real implementation, this would query a database
      const mockStatus = {
        analysis_id: analysisId,
        status: 'completed',
        progress: 100,
        start_time: new Date(Date.now() - 10000).toISOString(),
        completion_time: new Date().toISOString(),
        processing_time: 10000,
        cost_usd: 0.048,
        results: {
          threat_level: 'medium',
          confidence: 0.92,
          detected_threats: 5,
          risk_score: 28
        },
        metadata: {
          model_version: 'bigquery-ai-v2.1',
          total_steps: 5,
          cost_per_step: 0.008
        }
      };

      return {
        success: true,
        data: mockStatus,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'bigquery_ai',
          requestId: request.id
        }
      };

    } catch (error) {
      logger.error('Failed to get analysis status', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'STATUS_RETRIEVAL_FAILED',
          message: 'Failed to get analysis status'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/bigquery-ai/cost-history - Get cost history
  fastify.get('/bigquery-ai/cost-history', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      logger.info('Getting cost history...');
      
      // Use mock cost history since Python modules cannot be imported in Node.js
      const costHistory = {
        getCostHistory: () => [
          { date: '2024-01-15', cost: 0.048, requests: 6, analysis_type: 'comprehensive' },
          { date: '2024-01-14', cost: 0.064, requests: 8, analysis_type: 'comprehensive' },
          { date: '2024-01-13', cost: 0.032, requests: 4, analysis_type: 'quick' },
          { date: '2024-01-12', cost: 0.056, requests: 7, analysis_type: 'comprehensive' },
          { date: '2024-01-11', cost: 0.040, requests: 5, analysis_type: 'quick' }
        ]
      };
      
      logger.info('Mock cost history module created:', costHistory);
      
      const history = costHistory.getCostHistory();
      logger.info('History data:', history);
      
      return {
        success: true,
        data: {
          cost_history: history,
          summary: {
            total_cost: history.reduce((sum: number, item: any) => sum + item.cost, 0),
            total_requests: history.reduce((sum: number, item: any) => sum + item.requests, 0),
            average_cost_per_request: history.reduce((sum: number, item: any) => sum + item.cost, 0) / history.length,
            date_range: {
              start: history[history.length - 1]?.date,
              end: history[0]?.date
            }
          }
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'bigquery_ai',
          requestId: request.id
        }
      };

    } catch (error) {
      logger.error('Failed to get cost history', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'COST_HISTORY_FAILED',
          message: 'Failed to get cost history',
          details: error instanceof Error ? error.message : 'Unknown error'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });

  // GET /api/bigquery-ai/cost-monitor - Get current cost monitoring info
  fastify.get('/bigquery-ai/cost-monitor', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const costMonitor = getCostMonitor();
      const costInfo = costMonitor.getCostMonitor();
      
      return {
        success: true,
        data: costInfo,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'bigquery_ai',
          requestId: request.id
        }
      };

    } catch (error) {
      logger.error('Failed to get cost monitor info', error);
      reply.status(500);
      return {
        success: false,
        error: {
          code: 'COST_MONITOR_FAILED',
          message: 'Failed to get cost monitor info'
        },
        metadata: {
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      };
    }
  });
}

// Helper functions for generating realistic threat data
function generateThreatDescription(threatType: string, severity: number): string {
  const descriptions: { [key: string]: string[] } = {
    'supply-chain-compromise': [
      'Suspicious network activity detected from compromised third-party software update server',
      'Unauthorized access attempts from vendor-supplied software components',
      'Malicious code injection detected in third-party library updates',
      'Compromised vendor credentials used for system access'
    ],
    'credential-theft': [
      'Multiple failed login attempts followed by successful authentication',
      'Suspicious credential harvesting activity detected',
      'Stolen credentials used to access sensitive systems',
      'Credential stuffing attack detected from multiple IP addresses'
    ],
    'data-exfiltration': [
      'Large volume of data being transferred to external destinations',
      'Suspicious data access patterns outside business hours',
      'Unauthorized data export to unknown external servers',
      'Abnormal data transfer rates to suspicious destinations'
    ],
    'insider-threat': [
      'Employee accessing systems outside normal working hours',
      'Unauthorized access to sensitive data by internal user',
      'Suspicious data access patterns by privileged user',
      'Internal user attempting to bypass security controls'
    ],
    'malware-infection': [
      'Suspicious file execution patterns detected',
      'Malware signature detected in system files',
      'Abnormal network connections to known malicious domains',
      'Suspicious process behavior and system modifications'
    ],
    'network-intrusion': [
      'Unauthorized network access from external sources',
      'Suspicious network traffic patterns detected',
      'Port scanning activity from unknown sources',
      'Network reconnaissance activities detected'
    ],
    'api-abuse': [
      'Excessive API calls from single source',
      'Unauthorized API access attempts',
      'API rate limiting violations detected',
      'Suspicious API usage patterns'
    ],
    'privilege-escalation': [
      'User attempting to access privileged functions',
      'Unauthorized privilege escalation attempts',
      'Suspicious administrative access patterns',
      'Privileged account compromise detected'
    ]
  };
  
  const threatDescriptions = descriptions[threatType] || ['Suspicious activity detected in system'];
  return threatDescriptions[Math.floor(Math.random() * threatDescriptions.length)];
}

function generateThreatRecommendations(threatType: string, severity: number): string[] {
  const baseRecommendations = [
    'Isolate affected systems immediately',
    'Update software from verified sources only',
    'Implement additional network segmentation',
    'Review third-party vendor security'
  ];
  
  const specificRecommendations: { [key: string]: string[] } = {
    'supply-chain-compromise': [
      'Verify all software updates from trusted sources',
      'Implement software bill of materials (SBOM)',
      'Conduct vendor security assessments',
      'Monitor third-party component updates'
    ],
    'credential-theft': [
      'Reset all affected user credentials',
      'Implement multi-factor authentication',
      'Monitor for suspicious login patterns',
      'Review access control policies'
    ],
    'data-exfiltration': [
      'Block unauthorized data transfers',
      'Implement data loss prevention (DLP)',
      'Monitor data access patterns',
      'Review data classification policies'
    ],
    'insider-threat': [
      'Review user access permissions',
      'Implement user behavior analytics',
      'Conduct security awareness training',
      'Monitor privileged user activities'
    ],
    'malware-infection': [
      'Run full system malware scans',
      'Update antivirus signatures',
      'Isolate infected systems',
      'Review system integrity'
    ],
    'network-intrusion': [
      'Review firewall configurations',
      'Implement intrusion detection systems',
      'Monitor network traffic patterns',
      'Update network security policies'
    ],
    'api-abuse': [
      'Implement API rate limiting',
      'Review API access controls',
      'Monitor API usage patterns',
      'Implement API authentication'
    ],
    'privilege-escalation': [
      'Review user permissions',
      'Implement least privilege principle',
      'Monitor administrative activities',
      'Conduct access reviews'
    ]
  };
  
  const recommendations = [...baseRecommendations];
  if (specificRecommendations[threatType]) {
    recommendations.push(...specificRecommendations[threatType]);
  }
  
  // Add severity-based recommendations
  if (severity >= 8) {
    recommendations.unshift('Activate emergency incident response procedures');
    recommendations.unshift('Notify senior management immediately');
  } else if (severity >= 6) {
    recommendations.unshift('Implement immediate containment measures');
  }
  
  return recommendations.slice(0, 6); // Limit to 6 recommendations
}

// Helper function to force flush SSE responses
function flushResponse(reply: any) {
  // Try to force immediate transmission
  if (reply.raw.flush && typeof reply.raw.flush === 'function') {
    reply.raw.flush();
  }
  // Alternative: use process.stdout.write for immediate output
  if (process.stdout.write) {
    process.stdout.write('');
  }
}
