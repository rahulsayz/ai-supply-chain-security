import { WebSocket } from 'ws';
import { logger } from '../utils/logger';
import { WebSocketMessage, Threat } from '../types';
import { DataService } from './data.service';

export class WebSocketService {
  private clients = new Set<WebSocket>();
  private dataService: DataService;
  private simulationInterval?: NodeJS.Timeout;
  private isSimulationActive = false;

  constructor(dataService: DataService) {
    this.dataService = dataService;
    logger.info('WebSocketService initialized');
  }

  addClient(client: WebSocket): void {
    this.clients.add(client);
    logger.info('WebSocket client connected', { totalClients: this.clients.size });

    // Send initial connection message
    this.sendToClient(client, {
      type: 'system-status',
      data: { message: 'Connected to threat intelligence feed', status: 'active' },
      timestamp: new Date().toISOString()
    });

    // Handle client disconnect
    client.on('close', () => {
      this.clients.delete(client);
      logger.info('WebSocket client disconnected', { totalClients: this.clients.size });
    });

    client.on('error', (error) => {
      logger.error('WebSocket client error', error);
      this.clients.delete(client);
    });
  }

  startSimulation(): void {
    if (this.isSimulationActive) {
      logger.warn('Simulation already active');
      return;
    }

    const interval = parseInt(process.env.UPDATE_INTERVAL_MS || '10000');
    
    this.simulationInterval = setInterval(() => {
      this.broadcastThreatUpdate();
    }, interval);

    this.isSimulationActive = true;
    logger.info('WebSocket simulation started', { interval });
  }

  stopSimulation(): void {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = undefined;
      this.isSimulationActive = false;
      logger.info('WebSocket simulation stopped');
    }
  }

  private async broadcastThreatUpdate(): Promise<void> {
    try {
      const threats = await this.dataService.getThreats({ limit: 1 });
      if (threats.length === 0) return;

      const randomThreat = threats[Math.floor(Math.random() * threats.length)];
      const message: WebSocketMessage = {
        type: 'threat-detected',
        data: {
          threat: randomThreat,
          alertLevel: this.getAlertLevel(randomThreat.severity),
          priority: this.getPriority(randomThreat.aiRiskScore)
        },
        timestamp: new Date().toISOString()
      };

      this.broadcast(message);
      logger.debug('Broadcasted threat update', { threatId: randomThreat.id });
    } catch (error) {
      logger.error('Failed to broadcast threat update', error);
    }
  }

  broadcastVendorAlert(vendorId: string, alertType: string): void {
    const message: WebSocketMessage = {
      type: 'vendor-alert',
      data: {
        vendorId,
        alertType,
        severity: 'medium',
        timestamp: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    };

    this.broadcast(message);
    logger.info('Broadcasted vendor alert', { vendorId, alertType });
  }

  broadcastSystemStatus(status: string, details?: any): void {
    const message: WebSocketMessage = {
      type: 'system-status',
      data: {
        status,
        details,
        timestamp: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    };

    this.broadcast(message);
    logger.info('Broadcasted system status', { status });
  }

  private broadcast(message: WebSocketMessage): void {
    const messageStr = JSON.stringify(message);
    
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(messageStr);
        } catch (error) {
          logger.error('Failed to send message to client', error);
          this.clients.delete(client);
        }
      }
    });
  }

  private sendToClient(client: WebSocket, message: WebSocketMessage): void {
    if (client.readyState === WebSocket.OPEN) {
      try {
        client.send(JSON.stringify(message));
      } catch (error) {
        logger.error('Failed to send message to specific client', error);
      }
    }
  }

  private getAlertLevel(severity: number): string {
    if (severity >= 8) return 'critical';
    if (severity >= 6) return 'high';
    if (severity >= 4) return 'medium';
    return 'low';
  }

  private getPriority(aiRiskScore: number): string {
    if (aiRiskScore >= 0.8) return 'immediate';
    if (aiRiskScore >= 0.6) return 'high';
    if (aiRiskScore >= 0.4) return 'medium';
    return 'low';
  }

  getClientCount(): number {
    return this.clients.size;
  }

  isSimulationRunning(): boolean {
    return this.isSimulationActive;
  }

  // Manual trigger for demo purposes
  triggerThreatAlert(threatId?: string): void {
    if (threatId) {
      // Send specific threat alert
      this.dataService.getThreatById(threatId)
        .then(threat => {
          const message: WebSocketMessage = {
            type: 'threat-detected',
            data: {
              threat,
              alertLevel: this.getAlertLevel(threat.severity),
              priority: this.getPriority(threat.aiRiskScore),
              manual: true
            },
            timestamp: new Date().toISOString()
          };
          this.broadcast(message);
        })
        .catch(error => {
          logger.error('Failed to trigger specific threat alert', error);
        });
    } else {
      // Send random threat alert
      this.broadcastThreatUpdate();
    }
  }
}
