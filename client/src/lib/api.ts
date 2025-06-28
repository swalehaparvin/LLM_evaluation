import { apiRequest } from "./queryClient";

export interface DashboardStats {
  activeModels: number;
  criticalVulns: number;
  testsPassed: number;
  avgScore: number;
}

export interface LlmModel {
  id: number;
  modelId: string;
  provider: string;
  name: string;
  description?: string;
  isActive: boolean;
}

export interface TestSuite {
  id: number;
  name: string;
  description?: string;
  category: string;
  severity: string;
  isActive: boolean;
}

export interface TestCase {
  id: number;
  testSuiteId: number;
  testId: string;
  name: string;
  description?: string;
  prompt: string;
  systemPrompt?: string;
  evaluationCriteria: any;
  expectedOutcome?: string;
}

export interface EvaluationResult {
  id: number;
  evaluationId: number;
  testCaseId: number;
  modelResponse: string;
  passed: boolean;
  vulnerabilityScore: number;
  attackComplexity: string;
  detectionDifficulty: string;
  impactSeverity: string;
  remediationComplexity: string;
  confidenceLevel: number;
  compositeScore: number;
  metadata: any;
  createdAt: string;
}

export interface EvaluationProgress {
  evaluationId: number;
  totalTests: number;
  completedTests: number;
  currentTest?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface RunEvaluationRequest {
  modelId: string;
  testSuiteIds: number[];
  options?: {
    temperature?: number;
    maxTokens?: number;
  };
}

export interface RunCustomTestRequest {
  modelId: string;
  testSuiteName: string;
  prompt: string;
  systemPrompt?: string;
  evaluationCriteria?: any;
  options?: {
    temperature?: number;
    maxTokens?: number;
  };
}

// API functions
export const api = {
  // Dashboard
  getStats: async (): Promise<DashboardStats> => {
    const res = await apiRequest('GET', '/api/stats');
    return res.json();
  },

  // Models
  getModels: async (): Promise<LlmModel[]> => {
    const res = await apiRequest('GET', '/api/models');
    return res.json();
  },

  getModel: async (modelId: string): Promise<LlmModel> => {
    const res = await apiRequest('GET', `/api/models/${modelId}`);
    return res.json();
  },

  // Test Suites
  getTestSuites: async (): Promise<TestSuite[]> => {
    const res = await apiRequest('GET', '/api/test-suites');
    return res.json();
  },

  getTestCases: async (testSuiteId: number): Promise<TestCase[]> => {
    const res = await apiRequest('GET', `/api/test-suites/${testSuiteId}/test-cases`);
    return res.json();
  },

  // Evaluations
  runEvaluation: async (data: RunEvaluationRequest): Promise<{ evaluationId: number }> => {
    const res = await apiRequest('POST', '/api/evaluations', data);
    return res.json();
  },

  getEvaluationProgress: async (evaluationId: number): Promise<EvaluationProgress> => {
    const res = await apiRequest('GET', `/api/evaluations/${evaluationId}/progress`);
    return res.json();
  },

  getEvaluationResults: async (evaluationId: number): Promise<EvaluationResult[]> => {
    const res = await apiRequest('GET', `/api/evaluations/${evaluationId}/results`);
    return res.json();
  },

  // Custom tests
  runCustomTest: async (data: RunCustomTestRequest): Promise<EvaluationResult> => {
    const res = await apiRequest('POST', '/api/custom-test', data);
    return res.json();
  },

  // Recent results
  getRecentResults: async (limit = 10): Promise<EvaluationResult[]> => {
    const res = await apiRequest('GET', `/api/recent-results?limit=${limit}`);
    return res.json();
  },
};

// WebSocket connection for real-time updates
export class EvaluationWebSocket {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}`;
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const listeners = this.listeners.get(data.type);
        if (listeners) {
          listeners.forEach(listener => listener(data.data));
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  subscribeToEvaluation(evaluationId: number) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe_evaluation',
        evaluationId
      }));
    }
  }

  onProgress(callback: (progress: EvaluationProgress) => void) {
    if (!this.listeners.has('evaluation_progress')) {
      this.listeners.set('evaluation_progress', new Set());
    }
    this.listeners.get('evaluation_progress')!.add(callback);
  }

  offProgress(callback: (progress: EvaluationProgress) => void) {
    const listeners = this.listeners.get('evaluation_progress');
    if (listeners) {
      listeners.delete(callback);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const evaluationWS = new EvaluationWebSocket();
