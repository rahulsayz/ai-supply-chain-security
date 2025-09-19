import { BigQuery } from '@google-cloud/bigquery';
import { logger } from '../utils/logger';

export class BigQueryService {
  private bigquery: BigQuery | null = null;
  private isInitialized = false;

  constructor() {
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      const projectId = process.env.GCP_PROJECT_ID;
      const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

      if (!projectId) {
        logger.warn('GCP_PROJECT_ID not set, BigQuery service disabled');
        return;
      }

      if (!credentialsPath) {
        logger.warn('GOOGLE_APPLICATION_CREDENTIALS not set, BigQuery service disabled');
        return;
      }

      this.bigquery = new BigQuery({
        projectId,
        keyFilename: credentialsPath
      });

      // Test connection
      await this.healthCheck();
      this.isInitialized = true;
      logger.info('BigQuery service initialized successfully', { projectId });
    } catch (error) {
      logger.error('Failed to initialize BigQuery service', error);
      this.bigquery = null;
      this.isInitialized = false;
    }
  }

  async healthCheck(): Promise<boolean> {
    if (!this.bigquery) {
      return false;
    }

    try {
      const query = 'SELECT 1 as health_check';
      const [rows] = await this.bigquery.query(query);
      
      if (rows && rows.length > 0) {
        logger.debug('BigQuery health check passed');
        return true;
      }
      
      return false;
    } catch (error) {
      logger.error('BigQuery health check failed', error);
      return false;
    }
  }

  async getConnectionStatus(): Promise<{ connected: boolean; projectId?: string }> {
    if (!this.isInitialized || !this.bigquery) {
      return { connected: false };
    }

    try {
      const isHealthy = await this.healthCheck();
      return {
        connected: isHealthy,
        projectId: this.bigquery.projectId
      };
    } catch (error) {
      logger.error('Failed to get BigQuery connection status', error);
      return { connected: false };
    }
  }

  // Method to check if BigQuery is available (for conditional features)
  isAvailable(): boolean {
    return this.isInitialized && this.bigquery !== null;
  }

  // Get basic project info (for health dashboard)
  async getProjectInfo(): Promise<{ projectId: string; datasets: number } | null> {
    if (!this.bigquery) {
      return null;
    }

    try {
      const [datasets] = await this.bigquery.getDatasets();
      return {
        projectId: this.bigquery.projectId,
        datasets: datasets.length
      };
    } catch (error) {
      logger.error('Failed to get BigQuery project info', error);
      return null;
    }
  }

  // Graceful shutdown
  async shutdown(): Promise<void> {
    if (this.bigquery) {
      try {
        // BigQuery client doesn't have a close method, just clear reference
        this.bigquery = null;
        this.isInitialized = false;
        logger.info('BigQuery service shutdown completed');
      } catch (error) {
        logger.error('Error during BigQuery service shutdown', error);
      }
    }
  }
}
