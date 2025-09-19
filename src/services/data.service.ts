import { promises as fs } from 'fs';
import path from 'path';
import { logger } from '../utils/logger';
import { Threat, Vendor, DashboardOverview, AnalyticsData, ThreatFilters, DataFileInfo } from '../types';

export class DataService {
  private cache = new Map<string, any>();
  private dataPath: string;
  private expectedFiles: string[] = [
    'dashboard/overview.json',
    'threats.json',
    'threats/RPT001.json',
    'threats/RPT002.json',
    'threats/RPT003.json',
    'vendors.json',
    'vendors/V001.json',
    'vendors/V002.json',
    'vendors/V003.json',
    'analytics.json'
  ];

  constructor() {
    this.dataPath = process.env.DATA_PATH || './data';
    logger.info('DataService initialized', { dataPath: this.dataPath });
  }

  async initialize(): Promise<void> {
    try {
      await this.preloadData();
      logger.info('DataService initialization completed', { 
        cachedFiles: this.cache.size,
        totalFiles: this.expectedFiles.length 
      });
    } catch (error) {
      logger.error('Failed to initialize DataService', error);
      throw error;
    }
  }

  private async preloadData(): Promise<void> {
    const loadPromises = this.expectedFiles.map(async (filePath) => {
      try {
        const data = await this.loadData(filePath);
        logger.debug(`Preloaded data file: ${filePath}`);
        return { filePath, success: true };
      } catch (error) {
        logger.warn(`Failed to preload data file: ${filePath}`, error);
        return { filePath, success: false, error };
      }
    });

    await Promise.all(loadPromises);
  }

  async loadData<T>(filePath: string): Promise<T> {
    const fullPath = path.join(this.dataPath, filePath);
    
    // Check cache first
    if (this.cache.has(filePath)) {
      return this.cache.get(filePath);
    }

    try {
      // Load from file system
      const data = await fs.readFile(fullPath, 'utf8');
      const parsed = JSON.parse(data);
      
      // Cache for fast subsequent access
      this.cache.set(filePath, parsed);
      return parsed;
    } catch (error) {
      logger.error(`Failed to load data file: ${filePath}`, error);
      throw new Error(`Data file not found: ${filePath}`);
    }
  }

  async getDashboardOverview(): Promise<DashboardOverview> {
    return this.loadData<DashboardOverview>('dashboard/overview.json');
  }

  async getThreats(filters?: ThreatFilters): Promise<Threat[]> {
    const threats = await this.loadData<Threat[]>('threats.json');
    return this.filterThreats(threats, filters);
  }

  async getThreatById(id: string): Promise<Threat> {
    const filePath = `threats/${id}.json`;
    return this.loadData<Threat>(filePath);
  }

  async getVendors(): Promise<Vendor[]> {
    return this.loadData<Vendor[]>('vendors.json');
  }

  async getVendorById(id: string): Promise<Vendor> {
    const filePath = `vendors/${id}.json`;
    return this.loadData<Vendor>(filePath);
  }

  async getAnalytics(): Promise<AnalyticsData> {
    return this.loadData<AnalyticsData>('analytics.json');
  }

  private filterThreats(threats: Threat[], filters?: ThreatFilters): Threat[] {
    if (!filters) return threats;

    let filtered = [...threats];

    if (filters.severity !== undefined) {
      filtered = filtered.filter(t => t.severity >= filters.severity!);
    }

    if (filters.vendor) {
      filtered = filtered.filter(t => 
        t.vendorName.toLowerCase().includes(filters.vendor!.toLowerCase())
      );
    }

    if (filters.status) {
      filtered = filtered.filter(t => t.status === filters.status);
    }

    // Apply pagination
    if (filters.offset !== undefined) {
      filtered = filtered.slice(filters.offset);
    }

    if (filters.limit !== undefined) {
      filtered = filtered.slice(0, filters.limit);
    }

    return filtered;
  }

  async refreshData(): Promise<void> {
    logger.info('Refreshing data cache');
    this.cache.clear();
    await this.preloadData();
  }

  getDataFileInfo(): DataFileInfo[] {
    return this.expectedFiles.map(filePath => {
      const cached = this.cache.has(filePath);
      return {
        path: filePath,
        size: cached ? JSON.stringify(this.cache.get(filePath)).length : 0,
        lastModified: new Date().toISOString(),
        loaded: cached
      };
    });
  }

  getCacheStats(): { size: number; totalFiles: number; memoryUsage: number } {
    const memoryUsage = process.memoryUsage();
    return {
      size: this.cache.size,
      totalFiles: this.expectedFiles.length,
      memoryUsage: Math.round(memoryUsage.heapUsed / 1024 / 1024) // MB
    };
  }
}
