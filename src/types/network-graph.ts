// Network Graph Type Definitions

export interface NetworkNode {
  id: string;
  label: string;
  type: 'vendor' | 'threat' | 'system' | 'dependency' | 'threat_actor';
  category: string;
  position: { x: number; y: number };
  size: number;
  color: string;
  properties: Record<string, any>;
}

export interface VendorNode extends NetworkNode {
  type: 'vendor';
  risk_level: 'low' | 'medium' | 'high';
  confidence: number;
  properties: {
    industry: string;
    location: string;
    security_rating: number;
    compliance_status: string;
    last_assessment: string;
  };
}

export interface ThreatNode extends NetworkNode {
  type: 'threat';
  severity: 'low' | 'medium' | 'high';
  confidence: number;
  properties: {
    ioc_count: number;
    detection_rate: number;
    mitigation_status: string;
    last_seen: string;
  };
}

export interface SystemNode extends NetworkNode {
  type: 'system';
  status: 'operational' | 'degraded' | 'critical';
  availability: number;
  properties: {
    uptime: number;
    last_maintenance: string;
    backup_status: string;
  };
}

export interface DependencyNode extends NetworkNode {
  type: 'dependency';
  criticality: 'low' | 'medium' | 'high';
  health_score: number;
  properties: {
    sla_target: number;
    last_incident: string;
    redundancy_level: string;
  };
}

export interface ThreatActorNode extends NetworkNode {
  type: 'threat_actor';
  sophistication: 'low' | 'medium' | 'high';
  threat_level: number;
  properties: {
    attack_frequency: string;
    target_preference: string;
    last_activity: string;
  };
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: 'data_flow' | 'attack_vector' | 'threat_connection' | 'dependency' | 'trust_relationship';
  label: string;
  properties: Record<string, any>;
  risk_level: 'low' | 'medium' | 'high';
  color: string;
  width: number;
  is_new: boolean;
}

export interface RiskAssessment {
  overallRiskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  riskDistribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  riskChanges: number;
  criticalPaths: string[];
  recommendations: string[];
  lastCalculated: string;
}

export interface VisualizationConfig {
  node_colors: {
    vendor: { safe: string; warning: string; critical: string };
    threat: { safe: string; warning: string; critical: string };
    system: { safe: string; warning: string; critical: string };
    dependency: { safe: string; warning: string; critical: string };
    threat_actor: { safe: string; warning: string; critical: string };
  };
  edge_colors: {
    data_flow: string;
    attack_vector: string;
    trust_relationship: string;
    dependency: string;
    threat_connection: string;
  };
  animation_config: {
    node_animation: boolean;
    edge_animation: boolean;
    risk_pulse: boolean;
    threat_highlight: boolean;
    update_transition: number;
  };
}

export interface NetworkGraphMetadata {
  total_nodes: number;
  total_edges: number;
  total_threats: number;
  risk_changes: number;
  new_connections: number;
  graph_depth: number;
  analysis_type: string;
  last_updated: string;
  update_frequency: string;
}

export interface NetworkGraphData {
  nodes: (VendorNode | ThreatNode | SystemNode | DependencyNode | ThreatActorNode)[];
  edges: NetworkEdge[];
  risk_assessment: RiskAssessment;
  metadata: NetworkGraphMetadata;
  visualization_config: VisualizationConfig;
}

export interface RiskMetrics {
  totalRiskScore: number;
  riskDistribution: { low: number; medium: number; high: number; critical: number };
  riskChanges: number;
  criticalPaths: string[];
  recommendations: string[];
}

