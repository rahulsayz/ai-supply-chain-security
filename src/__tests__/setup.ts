// Test setup file for Jest
import dotenv from 'dotenv';

// Load environment variables for testing
dotenv.config({ path: '.env.test' });

// Set default test environment variables
process.env.NODE_ENV = 'test';
process.env.PORT = '8081';
process.env.DATA_PATH = './data';
process.env.SIMULATE_REAL_TIME = 'false';

// Mock console methods to reduce noise in tests
const originalConsole = {
  log: console.log,
  warn: console.warn,
  error: console.error,
  info: console.info,
  debug: console.debug,
};

beforeAll(() => {
  // Suppress console output during tests unless explicitly needed
  if (process.env.SHOW_CONSOLE !== 'true') {
    console.log = jest.fn();
    console.warn = jest.fn();
    console.error = jest.fn();
    console.info = jest.fn();
    console.debug = jest.fn();
  }
});

afterAll(() => {
  // Restore console methods
  console.log = originalConsole.log;
  console.warn = originalConsole.warn;
  console.error = originalConsole.error;
  console.info = originalConsole.info;
  console.debug = originalConsole.debug;
});

// Global test utilities
declare global {
  var testUtils: {
    createMockRequest: (params?: any) => any;
    createMockReply: () => any;
    wait: (ms: number) => Promise<void>;
  };
  
  namespace jest {
    interface Matchers<R> {
      // Add custom matchers here if needed
    }
  }
}

global.testUtils = {
  // Helper to create mock Fastify request
  createMockRequest: (params: any = {}) => ({
    id: 'test-request-id',
    params: {},
    query: {},
    body: {},
    headers: {},
    ...params,
  }),

  // Helper to create mock Fastify reply
  createMockReply: () => {
    const reply = {
      status: jest.fn().mockReturnThis(),
      send: jest.fn().mockReturnThis(),
      header: jest.fn().mockReturnThis(),
    };
    return reply;
  },

  // Helper to wait for async operations
  wait: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
};
