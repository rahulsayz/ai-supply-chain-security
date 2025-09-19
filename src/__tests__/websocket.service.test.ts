import { WebSocketService } from '../services/websocket.service';
import { DataService } from '../services/data.service';
import { WebSocket } from 'ws';

// Mock the DataService
jest.mock('../services/data.service');

// Mock the logger
jest.mock('../utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('WebSocketService', () => {
  let webSocketService: WebSocketService;
  let mockDataService: jest.Mocked<DataService>;
  let mockWebSocket: jest.Mocked<WebSocket>;

  beforeEach(() => {
    // Reset environment variable
    process.env.UPDATE_INTERVAL_MS = '1000';
    
    // Create mock data service
    mockDataService = {
      getThreats: jest.fn(),
      getThreatById: jest.fn(),
    } as any;

    // Create mock WebSocket
    mockWebSocket = {
      readyState: WebSocket.OPEN,
      send: jest.fn(),
      on: jest.fn(),
      close: jest.fn(),
    } as any;

    // Create fresh instance
    webSocketService = new WebSocketService(mockDataService);
    
    // Clear all mocks
    jest.clearAllMocks();
    
    // Clear timers
    jest.clearAllTimers();
  });

  afterEach(() => {
    // Stop any running simulation
    webSocketService.stopSimulation();
  });

  describe('constructor', () => {
    it('should initialize with data service', () => {
      expect(webSocketService).toBeDefined();
    });
  });

  describe('addClient', () => {
    it('should add client and send initial message', () => {
      webSocketService.addClient(mockWebSocket);

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('Connected to threat intelligence feed')
      );
    });

    it('should handle client disconnect', () => {
      webSocketService.addClient(mockWebSocket);
      
      // Simulate client disconnect
      const closeHandler = mockWebSocket.on.mock.calls.find(call => call[0] === 'close')?.[1];
      if (closeHandler) {
        closeHandler();
      }

      expect(webSocketService.getClientCount()).toBe(0);
    });

    it('should handle client error', () => {
      webSocketService.addClient(mockWebSocket);
      
      // Simulate client error
      const errorHandler = mockWebSocket.on.mock.calls.find(call => call[0] === 'error')?.[1];
      if (errorHandler) {
        errorHandler(new Error('Connection error'));
      }

      expect(webSocketService.getClientCount()).toBe(0);
    });
  });

  describe('startSimulation', () => {
    it('should start simulation when not already running', () => {
      expect(webSocketService.isSimulationRunning()).toBe(false);
      
      webSocketService.startSimulation();
      
      expect(webSocketService.isSimulationRunning()).toBe(true);
    });

    it('should not start simulation if already running', () => {
      webSocketService.startSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(true);
      
      webSocketService.startSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(true);
    });

    it('should use environment variable for update interval', () => {
      process.env.UPDATE_INTERVAL_MS = '5000';
      webSocketService.startSimulation();
      
      expect(webSocketService.isSimulationRunning()).toBe(true);
    });
  });

  describe('stopSimulation', () => {
    it('should stop running simulation', () => {
      webSocketService.startSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(true);
      
      webSocketService.stopSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(false);
    });

    it('should handle stopping when no simulation is running', () => {
      expect(webSocketService.isSimulationRunning()).toBe(false);
      
      webSocketService.stopSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(false);
    });
  });

  describe('broadcastThreatUpdate', () => {
    beforeEach(() => {
      // Add a client
      webSocketService.addClient(mockWebSocket);
      
      // Mock threat data
      mockDataService.getThreats.mockResolvedValue([
        { id: '1', severity: 8, aiRiskScore: 0.8 },
        { id: '2', severity: 6, aiRiskScore: 0.6 },
      ]);
    });

    it('should broadcast threat update to connected clients', async () => {
      // Start simulation to trigger broadcast
      webSocketService.startSimulation();
      
      // Fast-forward timers to trigger the interval
      jest.advanceTimersByTime(1000);
      
      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('threat-detected')
      );
    });

    it('should handle empty threats gracefully', async () => {
      mockDataService.getThreats.mockResolvedValue([]);
      
      webSocketService.startSimulation();
      jest.advanceTimersByTime(1000);
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      // Should not send any threat updates
      expect(mockWebSocket.send).not.toHaveBeenCalledWith(
        expect.stringContaining('threat-detected')
      );
    });
  });

  describe('broadcastVendorAlert', () => {
    beforeEach(() => {
      webSocketService.addClient(mockWebSocket);
    });

    it('should broadcast vendor alert to connected clients', () => {
      webSocketService.broadcastVendorAlert('V001', 'security-breach');
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('vendor-alert')
      );
    });
  });

  describe('broadcastSystemStatus', () => {
    beforeEach(() => {
      webSocketService.addClient(mockWebSocket);
    });

    it('should broadcast system status to connected clients', () => {
      webSocketService.broadcastSystemStatus('maintenance', { duration: '2 hours' });
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('system-status')
      );
    });
  });

  describe('triggerThreatAlert', () => {
    beforeEach(() => {
      webSocketService.addClient(mockWebSocket);
    });

    it('should trigger specific threat alert when threatId is provided', async () => {
      const mockThreat = { id: 'RPT001', severity: 9, aiRiskScore: 0.9 };
      mockDataService.getThreatById.mockResolvedValue(mockThreat);
      
      webSocketService.triggerThreatAlert('RPT001');
      
      // Wait for async operation
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(mockDataService.getThreatById).toHaveBeenCalledWith('RPT001');
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('threat-detected')
      );
    });

    it('should trigger random threat alert when no threatId is provided', async () => {
      mockDataService.getThreats.mockResolvedValue([
        { id: '1', severity: 8, aiRiskScore: 0.8 },
      ]);
      
      webSocketService.triggerThreatAlert();
      
      // Wait for async operation
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('threat-detected')
      );
    });

    it('should handle errors when triggering specific threat alert', async () => {
      mockDataService.getThreatById.mockRejectedValue(new Error('Threat not found'));
      
      webSocketService.triggerThreatAlert('INVALID');
      
      // Wait for async operation
      await new Promise(resolve => setTimeout(resolve, 0));
      
      // Should not send any messages due to error
      expect(mockWebSocket.send).not.toHaveBeenCalledWith(
        expect.stringContaining('threat-detected')
      );
    });
  });

  describe('getClientCount', () => {
    it('should return correct client count', () => {
      expect(webSocketService.getClientCount()).toBe(0);
      
      webSocketService.addClient(mockWebSocket);
      expect(webSocketService.getClientCount()).toBe(1);
      
      webSocketService.addClient(mockWebSocket);
      expect(webSocketService.getClientCount()).toBe(2);
    });
  });

  describe('isSimulationRunning', () => {
    it('should return correct simulation status', () => {
      expect(webSocketService.isSimulationRunning()).toBe(false);
      
      webSocketService.startSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(true);
      
      webSocketService.stopSimulation();
      expect(webSocketService.isSimulationRunning()).toBe(false);
    });
  });

  describe('private methods', () => {
    beforeEach(() => {
      webSocketService.addClient(mockWebSocket);
    });

    it('should handle closed WebSocket connections', () => {
      // Simulate closed connection
      mockWebSocket.readyState = WebSocket.CLOSED;
      
      webSocketService.broadcastVendorAlert('V001', 'test');
      
      // Should not send to closed connection
      expect(mockWebSocket.send).not.toHaveBeenCalled();
    });

    it('should handle WebSocket send errors', () => {
      // Mock send to throw error
      mockWebSocket.send.mockImplementation(() => {
        throw new Error('Send failed');
      });
      
      // Should handle error gracefully
      expect(() => {
        webSocketService.broadcastVendorAlert('V001', 'test');
      }).not.toThrow();
    });
  });
});
