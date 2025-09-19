const EventSource = require('eventsource');

// Test the live-analysis endpoint
async function testLiveAnalysis() {
  console.log('🧪 Testing Live Analysis API Endpoint');
  console.log('=====================================\n');

  const baseUrl = 'http://localhost:3000';
  const endpoint = '/api/bigquery-ai/live-analysis';

  try {
    // Make POST request to start analysis
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        vendorId: 'V001',
        analysisType: 'comprehensive',
        includeHistorical: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('✅ Analysis started successfully');
    console.log('📡 Listening for SSE events...\n');

    // Create EventSource to listen to the stream
    const eventSource = new EventSource(`${baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      }
    });

    let eventCount = 0;
    let threatEvents = 0;
    let analysisComplete = false;

    eventSource.onmessage = function(event) {
      eventCount++;
      const data = JSON.parse(event.data);
      
      console.log(`📨 Event ${eventCount}: ${data.type}`);
      console.log(`⏰ Timestamp: ${data.timestamp}`);
      
      if (data.type === 'threat-detected') {
        threatEvents++;
        console.log(`🚨 THREAT DETECTED #${threatEvents}:`);
        console.log(`   Type: ${data.data.threat_type}`);
        console.log(`   Severity: ${data.data.severity}/10`);
        console.log(`   Description: ${data.data.description}`);
        console.log(`   AI Risk Score: ${data.data.aiRiskScore}`);
        console.log(`   Confidence: ${data.data.confidence_score}`);
        console.log(`   Threat ID: ${data.data.threat_id}`);
        console.log(`   Vendor: ${data.data.vendor_name}`);
        console.log(`   Affected Systems: ${data.data.affectedSystems.join(', ')}`);
        console.log(`   Recommendations: ${data.data.recommendations.length} items`);
        console.log('');
      } else if (data.type === 'step_start') {
        console.log(`🔄 Step: ${data.message}`);
        console.log(`   Progress: ${data.progress}% (${data.stepNumber}/${data.totalSteps})`);
        console.log('');
      } else if (data.type === 'step_complete') {
        if (data.step) {
          console.log(`✅ Step Complete: ${data.step}`);
          console.log(`   Duration: ${data.duration}ms`);
          console.log(`   Cost: $${data.cost}`);
          console.log('');
        } else if (data.message) {
          console.log(`📊 Progress: ${data.message}`);
          console.log(`   Cost: $${data.cost_usd}`);
          console.log('');
        }
      } else if (data.type === 'analysis_complete') {
        analysisComplete = true;
        console.log(`🎯 ANALYSIS COMPLETE:`);
        console.log(`   Risk Level: ${data.results.ai_insights.risk_assessment.overall_risk}`);
        console.log(`   Confidence: ${data.results.ai_insights.risk_assessment.confidence}`);
        console.log(`   Total Threats: ${data.results.threat_summary.total_threats}`);
        console.log(`   Critical Threats: ${data.results.threat_summary.critical_threats}`);
        console.log(`   High Threats: ${data.results.threat_summary.high_threats}`);
        console.log(`   Affected Vendors: ${data.results.threat_summary.affected_vendors}`);
        console.log(`   Affected Systems: ${data.results.threat_summary.affected_systems}`);
        console.log(`   Processing Time: ${data.results.processing_metadata.processing_time_ms}ms`);
        console.log(`   Total Cost: $${data.results.processing_metadata.cost_usd}`);
        console.log(`   AI Models Used: ${data.results.processing_metadata.ai_models_used.join(', ')}`);
        console.log('');
        console.log('📋 Risk Factors:');
        data.results.ai_insights.risk_assessment.risk_factors.forEach((factor, index) => {
          console.log(`   ${index + 1}. ${factor}`);
        });
        console.log('');
        console.log('💡 Recommendations:');
        data.results.ai_insights.recommendations.forEach((rec, index) => {
          console.log(`   ${index + 1}. ${rec}`);
        });
        console.log('');
      } else if (data.type === 'end') {
        console.log('🏁 Stream ended');
        eventSource.close();
      } else if (data.type === 'error') {
        console.log(`❌ Error: ${data.message}`);
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
    console.log(`   Total Events: ${eventCount}`);
    console.log(`   Threat Events: ${threatEvents}`);
    console.log(`   Analysis Completed: ${analysisComplete ? 'Yes' : 'No'}`);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testLiveAnalysis();
