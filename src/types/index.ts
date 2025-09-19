export interface Threat {
  id: string;
  vendorName: string;
  threatType: string;
  severity: number;
  aiRiskScore: number;
  status: 'active' | 'investigating' | 'resolved';
  detectionTime: string;
  description: string;
  affectedSystems?: string[];
  remediationSteps?: string[];
  similarThreats?: string[];
  timeline?: ThreatEvent[];
}

export interface ThreatEvent {
  timestamp: string;
  event: string;
  description: string;
  actor?: string;
}

export interface Vendor {
  id: string;
  name: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  riskScore: number;
  threatCount: number;
  lastAssessment: string;
  complianceStatus: string[];
  criticalAssets: string[];
}

export interface DashboardOverview {
  totalThreats: number;
  activeThreats: number;
  criticalVendors: number;
  riskTrend: 'increasing' | 'decreasing' | 'stable';
  topThreatTypes: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  recentAlerts: Array<{
    id: string;
    vendor: string;
    severity: number;
    timestamp: string;
  }>;
}

export interface AnalyticsData {
  timeSeriesData: Array<{
    date: string;
    threats: number;
    riskScore: number;
  }>;
  threatTypes: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  attackVectors: Array<{
    vector: string;
    count: number;
    trend: string;
  }>;
  predictions: Array<{
    month: string;
    predicted: number;
    actual: number | null;
  }>;
}

export interface APIResponse<T> {
  success: true;
  data: T;
  metadata: {
    timestamp: string;
    source: 'precomputed' | 'live';
    processingTime: number;
    requestId?: string;
  };
}

export interface APIErrorResponse {
  success: false;
  error: {
    code: 'NOT_FOUND' | 'INVALID_PARAMS' | 'SERVER_ERROR';
    message: string;
  };
  metadata: {
    timestamp: string;
    source: 'precomputed' | 'live';
    processingTime: number;
    requestId?: string;
  };
}

export type APIResult<T> = APIResponse<T> | APIErrorResponse;

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  timestamp: string;
  dataFiles: { loaded: number; total: number };
  bigquery?: { connected: boolean };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
}

export interface ThreatFilters {
  severity?: number;
  vendor?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export interface ThreatDetailParams {
  id: string;
}

export interface VendorFilters {
  riskLevel?: string;
  limit?: number;
  offset?: number;
}

export interface VendorDetailParams {
  id: string;
}

export interface WebSocketMessage {
  type: 'threat-detected' | 'vendor-alert' | 'system-status';
  data: any;
  timestamp: string;
}

export interface DataFileInfo {
  path: string;
  size: number;
  lastModified: string;
  loaded: boolean;
}

// AI Dashboard Interfaces
export interface PredictedThreat {
  id: string;
  vendorName: string;
  probability: number;
  threatType: string;
  aiReasoning: string;
  recommendedAction: string;
  potentialImpact: string;
  timeframe: string;
  confidence: number;
  riskScore: number;
  affectedSystems?: string[];
  historicalPatterns?: string[];
  lastUpdated: string;
}

export interface AIProcessingStep {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  cost: number;
  eta: string;
  startTime: string;
  endTime?: string;
  metadata?: {
    recordsProcessed?: number;
    aiModel?: string;
    confidence?: number;
  };
}

export interface AIInsight {
  id: string;
  type: 'threat' | 'anomaly' | 'pattern' | 'recommendation' | 'discovery';
  message: string;
  confidence: number;
  timestamp: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  relatedThreats?: string[];
  affectedVendors?: string[];
  businessImpact?: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
}

export interface AIImpactMetrics {
  preventedLosses: number;
  speedAdvantage: number;
  accuracyBoost: number;
  processingVolume: number;
  riskReduction: number;
  predictionSuccess: number;
  timeToDetection: number;
  analystWorkloadReduction: number;
  costPerInvestigation: number;
  traditionalCostComparison: number;
  lastUpdated: string;
}

export interface AIExecutiveSummary {
  id: string;
  generatedAt: string;
  keyFindings: string[];
  aiConfidenceMetrics: {
    threatDetectionAccuracy: number;
    falsePositiveReduction: number;
    predictionReliability: number;
    overallConfidence: number;
  };
  immediateActions: Array<{
    priority: 'low' | 'medium' | 'high' | 'critical';
    action: string;
    description: string;
    timeline: string;
    responsible: string;
    riskScore: number;
  }>;
  businessImpact: {
    timeToThreatDetection: number;
    analystWorkloadReduction: number;
    costPerThreatInvestigation: number;
    traditionalCostComparison: number;
    potentialLossesPrevented: number;
  };
  threatPatterns: Array<{
    pattern: string;
    confidence: number;
    affectedVendors: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  recommendations: string[];
  nextUpdate: string;
}

export interface AIAnalysisRequest {
  vendorId?: string;
  analysisType: 'quick' | 'comprehensive' | 'predictive' | 'executive';
  includeHistorical?: boolean;
  includePredictions?: boolean;
  timeframe?: number; // days
}

export interface AIAnalysisResponse {
  success: boolean;
  data?: {
    analysisId: string;
    predictedThreats?: PredictedThreat[];
    processingSteps?: AIProcessingStep[];
    insights?: AIInsight[];
    executiveSummary?: AIExecutiveSummary;
    impactMetrics?: AIImpactMetrics;
  };
  error?: string;
  metadata: {
    timestamp: string;
    processingTime: number;
    cost: number;
    requestId: string;
  };
}
