# 🌐 Network Graph API - Interactive Threat Visualization

## 🎯 **Overview**

Transform your threat data into an interactive network graph showing:
- **Nodes**: Vendors, systems, dependencies, threat actors, threats
- **Edges**: Connections, data flows, attack vectors, trust relationships
- **Colors**: Risk levels (green=safe, yellow=warning, red=critical)
- **Animation**: Real-time updates as threats are detected

## 📡 **API Endpoints**

### **1. Generate Network Graph Data**
```
POST /api/network-graph
Content-Type: application/json
```

**Request Body:**
```json
{
  "vendorId": "V001",
  "threatId": "T001",
  "analysisType": "comprehensive",
  "includeHistorical": true,
  "graphDepth": 3
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [...],
    "edges": [...],
    "risk_assessment": {...},
    "metadata": {...},
    "visualization_config": {...}
  }
}
```

### **2. Live Network Graph Updates**
```
POST /api/network-graph-live
Content-Type: text/event-stream
```

**Real-time streaming updates** with Server-Sent Events (SSE)

---

## 🏗️ **Data Structure**

### **Node Types**

#### **Vendor Nodes**
```json
{
  "id": "V001",
  "label": "TechCorp Solutions",
  "type": "vendor",
  "category": "software_vendor",
  "risk_level": "medium",
  "confidence": 0.85,
  "properties": {
    "industry": "technology",
    "location": "United States",
    "security_rating": 6.7,
    "compliance_status": "review_required",
    "last_assessment": "2025-08-30T03:01:10.918Z"
  },
  "position": { "x": 200, "y": 0 },
  "size": 20,
  "color": "#FF9800"
}
```

#### **Threat Nodes**
```json
{
  "id": "T001",
  "label": "Supply Chain Attack",
  "type": "threat",
  "category": "supply_chain_compromise",
  "severity": "high",
  "confidence": 0.90,
  "properties": {
    "ioc_count": 15,
    "detection_rate": 0.85,
    "mitigation_status": "urgent",
    "last_seen": "2025-08-30T03:01:10.918Z"
  },
  "position": { "x": 300, "y": 0 },
  "size": 30,
  "color": "#F44336"
}
```

#### **System Nodes**
```json
{
  "id": "S001",
  "label": "ERP System",
  "type": "system",
  "category": "business_critical",
  "status": "operational",
  "availability": 0.95,
  "properties": {
    "uptime": 99.5,
    "last_maintenance": "2025-08-30T03:01:10.918Z",
    "backup_status": "current"
  },
  "position": { "x": 150, "y": 0 },
  "size": 20,
  "color": "#2196F3"
}
```

#### **Dependency Nodes**
```json
{
  "id": "D001",
  "label": "Database Cluster",
  "type": "dependency",
  "category": "infrastructure",
  "criticality": "high",
  "health_score": 0.90,
  "properties": {
    "sla_target": 99.9,
    "last_incident": "none",
    "redundancy_level": "n+2"
  },
  "position": { "x": 250, "y": 0 },
  "size": 25,
  "color": "#F44336"
}
```

#### **Threat Actor Nodes**
```json
{
  "id": "TA001",
  "label": "APT Group Alpha",
  "type": "threat_actor",
  "category": "nation_state",
  "sophistication": "high",
  "threat_level": 0.80,
  "properties": {
    "attack_frequency": "daily",
    "target_preference": "high_value",
    "last_activity": "2025-08-30T03:01:10.918Z"
  },
  "position": { "x": 350, "y": 0 },
  "size": 30,
  "color": "#F44336"
}
```

### **Edge Types**

#### **Data Flow Connections**
```json
{
  "id": "C001",
  "source": "V001",
  "target": "S001",
  "type": "data_flow",
  "label": "Data Flow",
  "properties": {
    "data_type": "business_data",
    "encryption": "enabled",
    "volume": "high",
    "frequency": "real_time"
  },
  "risk_level": "medium",
  "color": "#FF9800",
  "width": 2,
  "is_new": false
}
```

#### **Attack Vector Connections**
```json
{
  "id": "C002",
  "source": "T001",
  "target": "S001",
  "type": "attack_vector",
  "label": "Attack Vector",
  "properties": {
    "attack_method": "supply_chain_compromise",
    "success_probability": 0.90,
    "last_attempt": "2025-08-30T03:01:10.918Z"
  },
  "risk_level": "high",
  "color": "#F44336",
  "width": 4,
  "is_new": false
}
```

#### **Trust Relationships**
```json
{
  "id": "C003",
  "source": "V001",
  "target": "V002",
  "type": "trust_relationship",
  "label": "Trust Relationship",
  "properties": {
    "relationship_type": "business_partner",
    "trust_level": 0.85,
    "established_date": "2025-08-30T03:01:10.918Z"
  },
  "risk_level": "medium",
  "color": "#FF9800",
  "width": 2,
  "is_new": false
}
```

---

## 🎨 **Visualization Configuration**

### **Color Schemes**
```json
{
  "node_colors": {
    "vendor": { "safe": "#4CAF50", "warning": "#FF9800", "critical": "#F44336" },
    "threat": { "safe": "#4CAF50", "warning": "#FF9800", "critical": "#F44336" },
    "system": { "safe": "#2196F3", "warning": "#FF9800", "critical": "#F44336" },
    "dependency": { "safe": "#9C27B0", "warning": "#FF9800", "critical": "#F44336" },
    "threat_actor": { "safe": "#795548", "warning": "#FF9800", "critical": "#F44336" }
  },
  "edge_colors": {
    "data_flow": "#2196F3",
    "attack_vector": "#F44336",
    "trust_relationship": "#4CAF50",
    "dependency": "#FF9800",
    "threat_connection": "#9C27B0"
  }
}
```

### **Animation Configuration**
```json
{
  "animation_config": {
    "node_animation": true,
    "edge_animation": true,
    "risk_pulse": true,
    "threat_highlight": true,
    "update_transition": 500
  }
}
```

---

## 🚀 **Real-Time Updates**

### **Live Network Graph Stream**

The `/api/network-graph-live` endpoint provides real-time updates:

#### **Initial Graph**
```json
data: {
  "type": "graph_initial",
  "timestamp": "2025-08-30T03:01:10.918Z",
  "graph_data": {...}
}
```

#### **Step Updates**
```json
data: {
  "type": "step_start",
  "step": "threat_detection",
  "message": "Detecting new threats...",
  "timestamp": "2025-08-30T03:01:10.918Z",
  "stepNumber": 1,
  "totalSteps": 5
}

data: {
  "type": "graph_update",
  "step": "threat_detection",
  "timestamp": "2025-08-30T03:01:12.918Z",
  "stepNumber": 1,
  "totalSteps": 5,
  "progress": 20,
  "graph_data": {...},
  "changes": {
    "new_threats": 2,
    "risk_changes": 1,
    "new_connections": 3
  }
}
```

#### **Final Results**
```json
data: {
  "type": "graph_complete",
  "message": "Network graph analysis completed successfully",
  "timestamp": "2025-08-30T03:01:18.918Z",
  "graph_data": {...},
  "summary": {
    "total_threats_detected": 5,
    "risk_level_changes": 3,
    "new_connections_found": 8
  }
}
```

---

## 🔧 **UI Implementation Guide**

### **1. Initialize Network Graph**
```javascript
// Create network graph visualization
const networkGraph = new NetworkGraph(container, {
  nodes: initialData.nodes,
  edges: initialData.edges,
  colors: initialData.visualization_config.node_colors,
  animations: initialData.visualization_config.animation_config
});
```

### **2. Handle Real-Time Updates**
```javascript
// Connect to live network graph endpoint
const eventSource = new EventSource('/api/network-graph-live');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'graph_initial':
      networkGraph.initialize(data.graph_data);
      break;
      
    case 'graph_update':
      networkGraph.update(data.graph_data);
      updateProgressBar(data.progress);
      showChanges(data.changes);
      break;
      
    case 'graph_complete':
      networkGraph.finalize(data.graph_data);
      showSummary(data.summary);
      break;
  }
};
```

### **3. Risk Level Visualization**
```javascript
// Update node colors based on risk levels
nodes.forEach(node => {
  const riskColor = getRiskColor(node.type, node.risk_level);
  node.color = riskColor;
  
  // Add risk pulse animation for high-risk nodes
  if (node.risk_level === 'high' || node.risk_level === 'critical') {
    node.animation = 'risk_pulse';
  }
});
```

### **4. Interactive Features**
```javascript
// Node click handling
networkGraph.onNodeClick = function(node) {
  showNodeDetails(node);
  highlightConnections(node.id);
};

// Edge hover handling
networkGraph.onEdgeHover = function(edge) {
  showEdgeDetails(edge);
  highlightPath(edge.source, edge.target);
};
```

---

## 📊 **Risk Assessment Data**

### **Overall Risk Metrics**
```json
{
  "risk_assessment": {
    "overallRiskScore": 45,
    "riskLevel": "high",
    "riskDistribution": {
      "low": 8,
      "medium": 12,
      "high": 6,
      "critical": 2
    },
    "recommendations": [
      "Immediate attention required for high-risk nodes",
      "Review medium-risk nodes for potential mitigation",
      "Overall network risk is elevated - consider security review"
    ],
    "lastCalculated": "2025-08-30T03:01:18.918Z"
  }
}
```

---

## 🎯 **Use Cases**

### **1. Supply Chain Risk Assessment**
- Visualize vendor relationships
- Identify critical dependencies
- Track risk propagation paths

### **2. Threat Intelligence Mapping**
- Map threat actors to targets
- Visualize attack vectors
- Track threat evolution

### **3. Incident Response Planning**
- Identify critical systems
- Map attack paths
- Plan response strategies

### **4. Security Posture Monitoring**
- Real-time risk visualization
- Trend analysis
- Compliance monitoring

---

## 🚨 **Error Handling**

### **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "NETWORK_GRAPH_FAILED",
    "message": "Failed to generate network graph data"
  },
  "metadata": {
    "timestamp": "2025-08-30T03:01:10.918Z",
    "requestId": "req-123"
  }
}
```

### **Common Error Codes**
- `INVALID_PARAMS`: Missing required parameters
- `NETWORK_GRAPH_FAILED`: Graph generation failed
- `LIVE_NETWORK_GRAPH_FAILED`: Live updates failed

---

## 🔄 **Performance Considerations**

### **Graph Complexity Limits**
- **Small graphs**: Up to 50 nodes, 100 edges
- **Medium graphs**: Up to 200 nodes, 500 edges  
- **Large graphs**: Up to 1000 nodes, 2000 edges

### **Update Frequency**
- **Real-time**: Every 1-2 seconds during analysis
- **Live updates**: Every 5-10 seconds for monitoring
- **Batch updates**: Every minute for historical data

### **Caching Strategy**
- Cache static graph data for 5 minutes
- Cache risk assessments for 1 minute
- Real-time updates bypass cache

---

## 📱 **Mobile Optimization**

### **Responsive Design**
- Adaptive node sizing
- Touch-friendly interactions
- Optimized rendering for small screens

### **Performance Tuning**
- Reduced animation complexity
- Simplified visual effects
- Optimized data loading

---

## 🔐 **Security Considerations**

### **Data Access Control**
- Vendor data: Role-based access
- Threat data: Security clearance required
- System data: Infrastructure team access

### **Data Sanitization**
- Remove sensitive information
- Anonymize vendor details
- Filter classified threat data

---

## 🚀 **Getting Started**

### **1. Test the API**
```bash
# Generate static network graph
curl -X POST http://localhost:3000/api/network-graph \
  -H "Content-Type: application/json" \
  -d '{"vendorId": "V001", "analysisType": "comprehensive"}'
```

### **2. Test Live Updates**
```bash
# Connect to live network graph
curl -X POST http://localhost:3000/api/network-graph-live \
  -H "Content-Type: application/json" \
  -d '{"vendorId": "V001", "analysisType": "comprehensive"}'
```

### **3. Integrate with UI**
- Use the provided data structures
- Implement real-time updates
- Add interactive features
- Customize visualization

---

## 📚 **Additional Resources**

- **Network Graph Libraries**: D3.js, vis.js, Cytoscape.js
- **Real-time Updates**: Server-Sent Events, WebSockets
- **Risk Visualization**: Color theory, accessibility guidelines
- **Performance**: Graph algorithms, rendering optimization

---

## 🎉 **Success Metrics**

- **User Engagement**: Time spent analyzing graphs
- **Risk Detection**: Threats identified through visualization
- **Response Time**: Faster incident response with visual context
- **User Satisfaction**: Intuitive threat understanding

Your network graph API is now ready to transform threat data into interactive, real-time visualizations! 🚀
