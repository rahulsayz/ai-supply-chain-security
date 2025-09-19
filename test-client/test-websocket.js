const WebSocket = require('ws');

const WS_URL = process.env.WS_URL || 'ws://localhost:8080/ws';

console.log(`Connecting to WebSocket server at: ${WS_URL}`);

const ws = new WebSocket(WS_URL);

ws.on('open', function open() {
  console.log('✅ Connected to WebSocket server');
  console.log('Waiting for real-time updates...\n');
});

ws.on('message', function message(data) {
  try {
    const message = JSON.parse(data);
    console.log('📡 Received message:');
    console.log(`   Type: ${message.type}`);
    console.log(`   Timestamp: ${message.timestamp}`);
    console.log(`   Data: ${JSON.stringify(message.data, null, 2)}`);
    console.log('');
  } catch (error) {
    console.log('📡 Received raw message:', data.toString());
  }
});

ws.on('close', function close() {
  console.log('❌ WebSocket connection closed');
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err.message);
});

// Handle process termination
process.on('SIGINT', function() {
  console.log('\n🛑 Shutting down test client...');
  ws.close();
  process.exit(0);
});

// Keep the process alive
setInterval(() => {
  // Send a ping to keep connection alive
  if (ws.readyState === WebSocket.OPEN) {
    ws.ping();
  }
}, 30000);

console.log('WebSocket test client started. Press Ctrl+C to exit.\n');
