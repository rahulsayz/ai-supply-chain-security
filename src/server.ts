import Fastify, { FastifyInstance, FastifyRequest } from 'fastify';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';
import { logger, loggerConfig } from './utils/logger';
import { DataService } from './services/data.service';
import { WebSocketService } from './services/websocket.service';
import { BigQueryService } from './services/bigquery.service';


// Import routes
import { healthRoutes } from './routes/health';
import { dashboardRoutes } from './routes/dashboard';
import { threatRoutes } from './routes/threats';
import { vendorRoutes } from './routes/vendors';
import { analyticsRoutes } from './routes/analytics';
import bigQueryAIRoutes from './routes/bigquery-ai';
import { networkGraphRoutes } from './routes/network-graph';
import { aiDashboardRoutes } from './routes/ai-dashboard';

// Load environment variables
dotenv.config();

class SupplyChainAPI {
  private fastify: FastifyInstance;
  private wss: WebSocketServer;
  private dataService: DataService;
  private websocketService: WebSocketService;
  private bigqueryService: BigQueryService;

  constructor() {
    this.fastify = Fastify({
      logger: loggerConfig,
      trustProxy: true
    });
    
    this.wss = new WebSocketServer({ server: this.fastify.server });
    
    this.dataService = new DataService();
    this.websocketService = new WebSocketService(this.dataService);
    this.bigqueryService = new BigQueryService();
  }

  async initialize(): Promise<void> {
    try {
      // Initialize services
      await this.dataService.initialize();
      
      // Register plugins
      await this.registerPlugins();
      
      // Register routes
      await this.registerRoutes();
      
      // Setup WebSocket handling
      this.setupWebSocket();
      
      // Setup graceful shutdown
      this.setupGracefulShutdown();
      
      logger.info('Supply Chain API initialization completed');
    } catch (error) {
      logger.error('Failed to initialize Supply Chain API', error);
      throw error;
    }
  }

  private async registerPlugins(): Promise<void> {
    // CORS
    await this.fastify.register(import('@fastify/cors'), {
      origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
      credentials: true
    });

    // Compression
    await this.fastify.register(import('@fastify/compress'), {
      threshold: 1024
    });

    // Security headers
    await this.fastify.register(import('@fastify/helmet'), {
      contentSecurityPolicy: false // Allow inline scripts for demo purposes
    });

    // Rate limiting
    await this.fastify.register(import('@fastify/rate-limit'), {
      max: parseInt(process.env.RATE_LIMIT_MAX || '100'),
      timeWindow: parseInt(process.env.RATE_LIMIT_TIME_WINDOW || '60000')
    });

    // Swagger
    await this.fastify.register(import('@fastify/swagger'));
    await this.fastify.register(import('@fastify/swagger-ui'), {
      routePrefix: '/documentation'
    });

    logger.info('Fastify plugins registered');
  }

  private async registerRoutes(): Promise<void> {
    // Root route for testing
    this.fastify.get('/', async (request, reply) => {
      return {
        message: 'Supply Chain Cybersecurity API',
        version: '1.0.0',
        status: 'running',
        timestamp: new Date().toISOString(),
        endpoints: [
          '/api/health',
          '/api/dashboard/overview',
          '/api/threats',
          '/api/vendors',
          '/api/analytics',
          '/api/analytics/trends',
          '/api/analytics/threat-types',
          '/api/analytics/attack-vectors',
          '/api/analytics/predictions',
          '/api/bigquery-ai/status',
          '/api/bigquery-ai/analyze-threat',
          '/api/bigquery-ai/analyze-vendor',
          '/api/bigquery-ai/vector-search',
          '/api/bigquery-ai/costs',
          '/api/ai/predicted-threats',
          '/api/ai/processing-steps',
          '/api/ai/insights',
          '/api/ai/impact-metrics',
          '/api/ai/executive-summary',
          '/api/ai/comprehensive-analysis'
        ]
      };
    });

    // Health routes - register without prefix since routes already have /health
    await this.fastify.register(healthRoutes, { prefix: '/api' });
    
    // Dashboard routes - register without prefix since routes already have /dashboard
    await this.fastify.register(dashboardRoutes, { prefix: '/api' });
    
    // Threat routes - register without prefix since routes already have /threats
    await this.fastify.register(threatRoutes, { prefix: '/api' });
    
    // Vendor routes - register without prefix since routes already have /vendors
    await this.fastify.register(vendorRoutes, { prefix: '/api' });
    
    // Analytics routes - register without prefix since routes already have /analytics
    await this.fastify.register(analyticsRoutes, { prefix: '/api' });

    // BigQuery AI routes - register without prefix since routes already have /bigquery-ai
    await this.fastify.register(bigQueryAIRoutes, { prefix: '/api' });

    // Network Graph routes - register without prefix since routes already have /network-graph
    await this.fastify.register(networkGraphRoutes, { prefix: '/api' });

    // AI Dashboard routes - register without prefix since routes already have /ai
    await this.fastify.register(aiDashboardRoutes, { prefix: '/api' });

    // Demo and admin routes
    await this.registerDemoRoutes();
    
    logger.info('API routes registered');
  }

  private async registerDemoRoutes(): Promise<void> {
    // POST /api/refresh-data
    this.fastify.post('/api/refresh-data', async (request, reply) => {
      try {
        await this.dataService.refreshData();
        return {
          success: true,
          message: 'Data cache refreshed successfully',
          timestamp: new Date().toISOString()
        };
      } catch (error) {
        logger.error('Failed to refresh data', error);
        reply.status(500);
        return {
          success: false,
          error: 'Failed to refresh data cache'
        };
      }
    });

    // POST /api/simulate/threat-alert
    this.fastify.post('/api/simulate/threat-alert', async (request: FastifyRequest<{ Body: { threatId?: string } }>, reply) => {
      try {
        const { threatId } = request.body || {};
        this.websocketService.triggerThreatAlert(threatId);
        
        return {
          success: true,
          message: 'Threat alert simulation triggered',
          threatId: threatId || 'random',
          timestamp: new Date().toISOString()
        };
      } catch (error) {
        logger.error('Failed to trigger threat alert simulation', error);
        reply.status(500);
        return {
          success: false,
          error: 'Failed to trigger threat alert simulation'
        };
      }
    });

    // POST /api/simulate/start
    this.fastify.post('/api/simulate/start', async (request, reply) => {
      try {
        this.websocketService.startSimulation();
        return {
          success: true,
          message: 'WebSocket simulation started',
          timestamp: new Date().toISOString()
        };
      } catch (error) {
        logger.error('Failed to start simulation', error);
        reply.status(500);
        return {
          success: false,
          error: 'Failed to start simulation'
        };
      }
    });

    // POST /api/simulate/stop
    this.fastify.post('/api/simulate/stop', async (request, reply) => {
      try {
        this.websocketService.stopSimulation();
        return {
          success: true,
          message: 'WebSocket simulation stopped',
          timestamp: new Date().toISOString()
        };
      } catch (error) {
        logger.error('Failed to stop simulation', error);
        reply.status(500);
        return {
          success: false,
          error: 'Failed to stop simulation'
        };
      }
    });

    // GET /api/admin/status
    this.fastify.get('/api/admin/status', async (request, reply) => {
      try {
        const dataFileInfo = this.dataService.getDataFileInfo();
        const cacheStats = this.dataService.getCacheStats();
        const websocketStatus = {
          clients: this.websocketService.getClientCount(),
          simulationRunning: this.websocketService.isSimulationRunning()
        };
        const bigqueryStatus = await this.bigqueryService.getConnectionStatus();
        
        return {
          success: true,
          data: {
            dataFiles: dataFileInfo,
            cache: cacheStats,
            websocket: websocketStatus,
            bigquery: bigqueryStatus,
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            environment: process.env.NODE_ENV
          },
          metadata: {
            timestamp: new Date().toISOString(),
            source: 'live',
            processingTime: 0
          }
        };
      } catch (error) {
        logger.error('Failed to get admin status', error);
        reply.status(500);
        return {
          success: false,
          error: 'Failed to retrieve admin status'
        };
      }
    });

    logger.info('Demo and admin routes registered');
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws) => {
      this.websocketService.addClient(ws);
    });

    // Start simulation if enabled
    if (process.env.SIMULATE_REAL_TIME === 'true') {
      this.websocketService.startSimulation();
      logger.info('WebSocket simulation auto-started');
    }

    logger.info('WebSocket server configured');
  }

  private setupGracefulShutdown(): void {
    const shutdown = async (signal: string) => {
      logger.info(`Received ${signal}, starting graceful shutdown`);
      
      try {
        // Stop WebSocket simulation
        this.websocketService.stopSimulation();
        
        // Close WebSocket server
        this.wss.close();
        
        // Close BigQuery service
        await this.bigqueryService.shutdown();
        
        // Close Fastify server
        await this.fastify.close();
        
        logger.info('Graceful shutdown completed');
        process.exit(0);
      } catch (error) {
        logger.error('Error during graceful shutdown', error);
        process.exit(1);
      }
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));
  }

  async start(): Promise<void> {
    try {
      const port = parseInt(process.env.PORT || '8080');
      const host = '0.0.0.0';
      
      await this.fastify.ready();
      
      this.fastify.listen(port, host, () => {
        logger.info(`Supply Chain API server listening on ${host}:${port}`);
        logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        logger.info(`WebSocket simulation: ${process.env.SIMULATE_REAL_TIME === 'true' ? 'enabled' : 'disabled'}`);
      });
    } catch (error) {
      logger.error('Failed to start server', error);
      throw error;
    }
  }
}

// Start the server
async function main() {
  try {
    const api = new SupplyChainAPI();
    await api.initialize();
    await api.start();
  } catch (error) {
    logger.error('Failed to start Supply Chain API', error);
    process.exit(1);
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection', { promise, reason });
  process.exit(1);
});

if (require.main === module) {
  main();
}

export { SupplyChainAPI };
