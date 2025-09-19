import { FastifyInstance } from 'fastify';
import { healthRoutes } from '../routes/health';
import { DataService } from '../services/data.service';
import { BigQueryService } from '../services/bigquery.service';

// Mock the services
jest.mock('../services/data.service');
jest.mock('../services/bigquery.service');

describe('Health Routes', () => {
  let fastify: FastifyInstance;
  let mockDataService: jest.Mocked<DataService>;
  let mockBigQueryService: jest.Mocked<BigQueryService>;

  beforeEach(async () => {
    // Create a fresh Fastify instance for each test
    fastify = require('fastify')();
    
    // Mock the services
    mockDataService = {
      getDataFileInfo: jest.fn(),
      getCacheStats: jest.fn(),
    } as any;

    mockBigQueryService = {
      isAvailable: jest.fn(),
      getConnectionStatus: jest.fn(),
    } as any;

    // Register the health routes
    await fastify.register(healthRoutes);
  });

  afterEach(async () => {
    await fastify.close();
  });

  describe('GET /health', () => {
    it('should return healthy status when all systems are operational', async () => {
      // Mock data service responses
      mockDataService.getDataFileInfo.mockReturnValue([
        { path: 'test.json', size: 100, lastModified: '2024-01-15', loaded: true },
        { path: 'test2.json', size: 200, lastModified: '2024-01-15', loaded: true },
      ]);

      // Mock BigQuery service responses
      mockBigQueryService.isAvailable.mockReturnValue(true);
      mockBigQueryService.getConnectionStatus.mockResolvedValue({
        connected: true,
        projectId: 'test-project',
      });

      const response = await fastify.inject({
        method: 'GET',
        url: '/health',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.status).toBe('healthy');
      expect(data.dataFiles.loaded).toBe(2);
      expect(data.dataFiles.total).toBe(2);
      expect(data.bigquery.connected).toBe(true);
      expect(data.memory).toBeDefined();
    });

    it('should return degraded status when data files are missing', async () => {
      // Mock data service responses with missing files
      mockDataService.getDataFileInfo.mockReturnValue([
        { path: 'test.json', size: 100, lastModified: '2024-01-15', loaded: true },
        { path: 'test2.json', size: 200, lastModified: '2024-01-15', loaded: false },
      ]);

      // Mock BigQuery service responses
      mockBigQueryService.isAvailable.mockReturnValue(true);
      mockBigQueryService.getConnectionStatus.mockResolvedValue({
        connected: true,
        projectId: 'test-project',
      });

      const response = await fastify.inject({
        method: 'GET',
        url: '/health',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.status).toBe('degraded');
      expect(data.dataFiles.loaded).toBe(1);
      expect(data.dataFiles.total).toBe(2);
    });

    it('should handle BigQuery service unavailability gracefully', async () => {
      // Mock data service responses
      mockDataService.getDataFileInfo.mockReturnValue([
        { path: 'test.json', size: 100, lastModified: '2024-01-15', loaded: true },
      ]);

      // Mock BigQuery service as unavailable
      mockBigQueryService.isAvailable.mockReturnValue(false);

      const response = await fastify.inject({
        method: 'GET',
        url: '/health',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.status).toBe('healthy');
      expect(data.bigquery).toBeUndefined();
    });
  });

  describe('GET /health/data-files', () => {
    it('should return data file information and cache stats', async () => {
      const mockFileInfo = [
        { path: 'test.json', size: 100, lastModified: '2024-01-15', loaded: true },
        { path: 'test2.json', size: 200, lastModified: '2024-01-15', loaded: false },
      ];

      const mockCacheStats = {
        size: 1,
        totalFiles: 2,
        memoryUsage: 50,
      };

      mockDataService.getDataFileInfo.mockReturnValue(mockFileInfo);
      mockDataService.getCacheStats.mockReturnValue(mockCacheStats);

      const response = await fastify.inject({
        method: 'GET',
        url: '/health/data-files',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.success).toBe(true);
      expect(data.data.files).toEqual(mockFileInfo);
      expect(data.data.cache).toEqual(mockCacheStats);
    });
  });

  describe('GET /health/bigquery', () => {
    it('should return BigQuery status when service is available', async () => {
      mockBigQueryService.isAvailable.mockReturnValue(true);
      mockBigQueryService.getConnectionStatus.mockResolvedValue({
        connected: true,
        projectId: 'test-project',
      });

      const response = await fastify.inject({
        method: 'GET',
        url: '/health/bigquery',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.success).toBe(true);
      expect(data.data.available).toBe(true);
      expect(data.data.connected).toBe(true);
      expect(data.data.projectId).toBe('test-project');
    });

    it('should return unavailable status when BigQuery service is not configured', async () => {
      mockBigQueryService.isAvailable.mockReturnValue(false);

      const response = await fastify.inject({
        method: 'GET',
        url: '/health/bigquery',
      });

      expect(response.statusCode).toBe(200);
      const data = JSON.parse(response.payload);
      
      expect(data.success).toBe(true);
      expect(data.data.available).toBe(false);
      expect(data.data.message).toBe('BigQuery service not configured');
    });
  });
});
