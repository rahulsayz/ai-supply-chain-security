const EventSource = require('eventsource').EventSource;

// Test specifically the threat-detected events
async function testThreatDetection() {
  console.log('🧪 Testing Threat Detection Events');
  console.log('==================================\n');

  const baseUrl = 'http://localhost:8080';
  const endpoint = '/api/bigquery-ai/live-analysis';

  try {
    console.log('📡 Starting live analysis...');
    
    // Create EventSource to listen to the stream
    const eventSource = new EventSource(`${baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    let threatEvents = [];
    let analysisComplete = false;

    eventSource.onmessage = function(event) {
      const data = JSON.parse(event.data);
      
      if (data.type === 'threat-detected') {
        console.log(`🚨 THREAT DETECTED:`);
        console.log(`   Event Type: ${data.type}`);
        console.log(`   Threat Type: ${data.data.threat_type}`);
        console.log(`   Severity: ${data.data.severity}/10`);
        console.log(`   Description: ${data.data.description}`);
        console.log(`   AI Risk Score: ${data.data.aiRiskScore}`);
        console.log(`   Confidence: ${data.data.confidence_score}`);
        console.log(`   Threat ID: ${data.data.threat_id}`);
        console.log(`   Vendor: ${data.data.vendor_name}`);
        console.log(`   Affected Systems: ${data.data.affectedSystems.join(', ')}`);
        console.log(`   Recommendations: ${data.data.recommendations.length} items`);
        console.log('');
        
        threatEvents.push(data.data);
      } else if (data.type === 'analysis_complete') {
        analysisComplete = true;
        console.log(`🎯 ANALYSIS COMPLETE:`);
        console.log(`   Total Threats Detected: ${data.results.threat_summary.total_threats}`);
        console.log(`   Critical Threats: ${data.results.threat_summary.critical_threats}`);
        console.log(`   High Threats: ${data.results.threat_summary.high_threats}`);
        console.log('');
        
        eventSource.close();
      } else if (data.type === 'end') {
        eventSource.close();
      }
    };

    eventSource.onerror = function(error) {
      console.error('❌ EventSource error:', error);
      eventSource.close();
    };

    // Wait for analysis to complete
    await new Promise((resolve) => {
      const checkComplete = setInterval(() => {
        if (analysisComplete) {
          clearInterval(checkComplete);
          resolve(true);
        }
      }, 1000);
      
      // Timeout after 30 seconds
      setTimeout(() => {
        clearInterval(checkComplete);
        if (!analysisComplete) {
          console.log('⏰ Timeout waiting for analysis to complete');
          eventSource.close();
          resolve(false);
        }
      }, 30000);
    });

    console.log('📊 Test Summary:');
    console.log(`   Total Threat Events: ${threatEvents.length}`);
    
    if (threatEvents.length > 0) {
      console.log('\n🔍 Threat Types Detected:');
      threatEvents.forEach((threat, index) => {
        console.log(`   ${index + 1}. ${threat.threat_type} (Severity: ${threat.severity})`);
      });
      
      console.log('\n✅ Backend is working correctly!');
      console.log('   The issue is likely in your frontend code.');
      console.log('\n🔧 Frontend Fix Required:');
      console.log('   Make sure your frontend is listening for "threat-detected" events');
      console.log('   and extracting data.data.threat_type (not data.threat_type)');
    } else {
      console.log('❌ No threat events detected - backend issue');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testThreatDetection();
