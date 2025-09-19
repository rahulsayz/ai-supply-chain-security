import { DataService } from '../services/data.service';
import { promises as fs } from 'fs';
import path from 'path';

// Mock fs promises
jest.mock('fs', () => ({
  promises: {
    readFile: jest.fn(),
  },
}));

// Mock logger
jest.mock('../utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('DataService', () => {
  let dataService: DataService;
  let mockFs: jest.Mocked<typeof fs>;

  beforeEach(() => {
    // Reset environment variable
    process.env.DATA_PATH = './data';
    
    // Create fresh instance
    dataService = new DataService();
    
    // Get mocked fs
    mockFs = fs as jest.Mocked<typeof fs>;
    
    // Clear all mocks
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with default data path', () => {
      delete process.env.DATA_PATH;
      const service = new DataService();
      expect(service).toBeDefined();
    });

    it('should initialize with custom data path', () => {
      process.env.DATA_PATH = '/custom/path';
      const service = new DataService();
      expect(service).toBeDefined();
    });
  });

  describe('initialize', () => {
    it('should successfully initialize and preload data', async () => {
      // Mock successful file reads
      mockFs.readFile.mockResolvedValue('{"test": "data"}');

      await expect(dataService.initialize()).resolves.not.toThrow();
    });

    it('should handle initialization errors gracefully', async () => {
      // Mock file read failure
      mockFs.readFile.mockRejectedValue(new Error('File not found'));

      await expect(dataService.initialize()).rejects.toThrow();
    });
  });

  describe('loadData', () => {
    beforeEach(async () => {
      // Initialize the service first
      mockFs.readFile.mockResolvedValue('{"test": "data"}');
      await dataService.initialize();
    });

    it('should load data from file system', async () => {
      const result = await dataService.loadData('test.json');
      expect(result).toEqual({ test: 'data' });
    });

    it('should return cached data on subsequent calls', async () => {
      // First call should read from file
      await dataService.loadData('test.json');
      
      // Second call should use cache
      const result = await dataService.loadData('test.json');
      expect(result).toEqual({ test: 'data' });
      
      // Verify fs.readFile was only called once
      expect(mockFs.readFile).toHaveBeenCalledTimes(1);
    });

    it('should throw error for non-existent files', async () => {
      mockFs.readFile.mockRejectedValue(new Error('File not found'));
      
      await expect(dataService.loadData('nonexistent.json')).rejects.toThrow('Data file not found: nonexistent.json');
    });
  });

  describe('getDashboardOverview', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('{"totalThreats": 10}');
      await dataService.initialize();
    });

    it('should return dashboard overview data', async () => {
      const result = await dataService.getDashboardOverview();
      expect(result).toEqual({ totalThreats: 10 });
    });
  });

  describe('getThreats', () => {
    const mockThreats = [
      { id: '1', severity: 8, vendorName: 'Vendor1', status: 'active' },
      { id: '2', severity: 6, vendorName: 'Vendor2', status: 'resolved' },
      { id: '3', severity: 9, vendorName: 'Vendor1', status: 'active' },
    ];

    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue(JSON.stringify(mockThreats));
      await dataService.initialize();
    });

    it('should return all threats when no filters applied', async () => {
      const result = await dataService.getThreats();
      expect(result).toHaveLength(3);
    });

    it('should filter threats by severity', async () => {
      const result = await dataService.getThreats({ severity: 8 });
      expect(result).toHaveLength(2);
      expect(result.every(t => t.severity >= 8)).toBe(true);
    });

    it('should filter threats by vendor', async () => {
      const result = await dataService.getThreats({ vendor: 'Vendor1' });
      expect(result).toHaveLength(2);
      expect(result.every(t => t.vendorName.includes('Vendor1'))).toBe(true);
    });

    it('should filter threats by status', async () => {
      const result = await dataService.getThreats({ status: 'active' });
      expect(result).toHaveLength(2);
      expect(result.every(t => t.status === 'active')).toBe(true);
    });

    it('should apply pagination', async () => {
      const result = await dataService.getThreats({ limit: 2, offset: 1 });
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe('2');
    });
  });

  describe('getThreatById', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('{"id": "RPT001", "severity": 9}');
      await dataService.initialize();
    });

    it('should return threat by ID', async () => {
      const result = await dataService.getThreatById('RPT001');
      expect(result).toEqual({ id: 'RPT001', severity: 9 });
    });
  });

  describe('getVendors', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('[{"id": "V001", "name": "Vendor1"}]');
      await dataService.initialize();
    });

    it('should return vendors list', async () => {
      const result = await dataService.getVendors();
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe('V001');
    });
  });

  describe('getVendorById', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('{"id": "V001", "name": "Vendor1"}');
      await dataService.initialize();
    });

    it('should return vendor by ID', async () => {
      const result = await dataService.getVendorById('V001');
      expect(result).toEqual({ id: 'V001', name: 'Vendor1' });
    });
  });

  describe('getAnalytics', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('{"threatTrends": []}');
      await dataService.initialize();
    });

    it('should return analytics data', async () => {
      const result = await dataService.getAnalytics();
      expect(result).toEqual({ threatTrends: [] });
    });
  });

  describe('refreshData', () => {
    beforeEach(async () => {
      mockFs.readFile.mockResolvedValue('{"test": "data"}');
      await dataService.initialize();
    });

    it('should clear cache and reload data', async () => {
      // Load some data first
      await dataService.loadData('test.json');
      
      // Refresh data
      await dataService.refreshData();
      
      // Verify cache is cleared by checking if fs.readFile is called again
      await dataService.loadData('test.json');
      expect(mockFs.readFile).toHaveBeenCalledTimes(3); // Initial + refresh + reload
    });
  });

  describe('getDataFileInfo', () => {
    it('should return information about expected data files', () => {
      const fileInfo = dataService.getDataFileInfo();
      
      expect(fileInfo).toBeDefined();
      expect(fileInfo.length).toBeGreaterThan(0);
      expect(fileInfo[0]).toHaveProperty('path');
      expect(fileInfo[0]).toHaveProperty('loaded');
    });
  });

  describe('getCacheStats', () => {
    it('should return cache statistics', () => {
      const stats = dataService.getCacheStats();
      
      expect(stats).toHaveProperty('size');
      expect(stats).toHaveProperty('totalFiles');
      expect(stats).toHaveProperty('memoryUsage');
      expect(typeof stats.memoryUsage).toBe('number');
    });
  });
});
