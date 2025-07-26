# SafeGuardLLM - System Design Document

## Table of Contents
1. [Overview](#overview)
2. [Architecture Overview](#architecture-overview)
3. [Component Design](#component-design)
4. [Data Models](#data-models)
5. [API Design](#api-design)
6. [Security & Evaluation Engine](#security--evaluation-engine)
7. [Real-time Communication](#real-time-communication)
8. [Database Design](#database-design)
9. [Frontend Architecture](#frontend-architecture)
10. [Deployment Architecture](#deployment-architecture)
11. [Performance Considerations](#performance-considerations)
12. [Security Considerations](#security-considerations)

## Overview

SafeGuardLLM is a comprehensive cybersecurity evaluation framework designed to systematically assess Large Language Model (LLM) vulnerabilities across multiple security dimensions. The system provides advanced testing capabilities, real-time evaluation progress tracking, and detailed security reporting through a modern web interface.

### Key Objectives
- Evaluate LLM security across multiple attack vectors
- Provide real-time evaluation progress and results
- Support multiple LLM providers (OpenAI, Anthropic, Google Gemini)
- Generate comprehensive security reports and analytics
- Maintain scalable, extensible architecture for future test suites

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  React Frontend (TypeScript) + Tailwind CSS + shadcn/ui       │
│  • Dashboard & Visualizations                                  │
│  • Real-time Progress Tracking                                 │
│  • Evaluation Results Management                               │
│  • PDF Report Generation                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                        WebSocket & HTTP/REST
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│           Express.js Server (TypeScript)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Routes    │  │  WebSocket      │  │  Evaluation     │ │
│  │   Controller    │  │  Handler        │  │  Engine         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                        Database Queries
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│              PostgreSQL Database (Neon)                        │
│  • Users & Authentication                                      │
│  • LLM Models & Configurations                                 │
│  • Test Suites & Test Cases                                    │
│  • Evaluations & Results                                       │
│  • Security Metrics & Analytics                                │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                   External Services                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  OpenAI     │  │ Anthropic   │  │     Google Gemini       │ │
│  │  API        │  │ Claude API  │  │     API                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Frontend Components

#### Core UI Components
- **Dashboard**: Main interface with evaluation statistics and controls
- **EvaluationResultsTable**: Paginated table with filtering and sorting
- **ModelSelection**: Multi-provider LLM selection interface
- **TestSuiteManager**: Configuration of security test suites
- **ProgressTracker**: Real-time evaluation progress visualization
- **ReportGenerator**: PDF export functionality

#### State Management
- **TanStack Query**: Server state management and caching
- **React Hooks**: Local component state management
- **WebSocket Context**: Real-time updates distribution

### 2. Backend Components

#### API Layer
```typescript
// Route Structure
/api/models              - LLM model management
/api/test-suites         - Security test suite operations
/api/evaluations         - Evaluation lifecycle management
/api/evaluation-results  - Results querying with pagination
/api/stats              - Dashboard analytics
/ws                     - WebSocket real-time updates
```

#### Core Services
- **ModelService**: LLM provider abstraction and management
- **EvaluationEngine**: Asynchronous test execution coordinator
- **TestEvaluator**: Security pattern matching and scoring
- **ProgressTracker**: Real-time progress broadcasting
- **StorageService**: Database abstraction layer

## Data Models

### Core Entities

```typescript
// User Management
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

// LLM Model Registry
interface LLMModel {
  id: number;
  modelId: string;
  provider: 'openai' | 'anthropic' | 'google';
  name: string;
  description?: string;
  isActive: boolean;
  configuration: {
    temperature?: number;
    maxTokens?: number;
    topP?: number;
  };
}

// Security Test Framework
interface TestSuite {
  id: number;
  name: string;
  description: string;
  category: string;
  testCount: number;
  isActive: boolean;
}

interface TestCase {
  id: number;
  testSuiteId: number;
  name: string;
  prompt: string;
  expectedBehavior: string;
  category: string;
  difficulty: 'low' | 'medium' | 'high' | 'critical';
  metadata: {
    mitreTactics?: string[];
    injectionType?: string;
    language?: string;
  };
}

// Evaluation System
interface Evaluation {
  id: number;
  modelId: string;
  testSuiteIds: number[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  createdAt: Date;
  completedAt?: Date;
}

interface EvaluationResult {
  id: number;
  evaluationId: number;
  testCaseId: number;
  modelId: string;
  testName: string;
  prompt: string;
  response: string;
  passed: boolean;
  vulnerabilityScore: number;
  confidenceLevel: number;
  impactSeverity: 'low' | 'medium' | 'high' | 'critical';
  attackComplexity: 'low' | 'medium' | 'high';
  detectionDifficulty: 'easy' | 'medium' | 'hard';
  remediationComplexity: 'simple' | 'moderate' | 'complex';
  evaluationDetails: {
    patterns?: string[];
    keywords?: string[];
    reasoning?: string;
  };
  createdAt: Date;
}
```

## API Design

### RESTful Endpoints

#### Model Management
```http
GET    /api/models                    # List all LLM models
POST   /api/models                    # Register new model
PUT    /api/models/:id                # Update model configuration
DELETE /api/models/:id                # Deactivate model
```

#### Test Suite Management
```http
GET    /api/test-suites               # List available test suites
GET    /api/test-suites/:id           # Get test suite details
GET    /api/test-suites/:id/tests     # Get test cases for suite
```

#### Evaluation Lifecycle
```http
POST   /api/evaluations               # Create new evaluation
GET    /api/evaluations/:id           # Get evaluation status
POST   /api/evaluations/:id/start     # Start evaluation execution
POST   /api/evaluations/:id/stop      # Stop running evaluation
DELETE /api/evaluations/:id           # Cancel evaluation
```

#### Results & Analytics
```http
GET    /api/evaluation-results        # Paginated results with filtering
  Query Parameters:
  - page: number (default: 1)
  - limit: number (default: 100, max: 200)
  - model: string (filter by model)
  - status: 'Pass' | 'Fail' (filter by result)
  - testType: string (filter by test category)

GET    /api/stats                     # Dashboard statistics
  Response: {
    totalEvaluations: number,
    activeModels: number,
    criticalVulnerabilities: number,
    averageScore: number
  }
```

### WebSocket Events

```typescript
// Client -> Server
interface ClientEvents {
  'subscribe-evaluation': { evaluationId: number };
  'unsubscribe-evaluation': { evaluationId: number };
}

// Server -> Client  
interface ServerEvents {
  'evaluation-progress': {
    evaluationId: number;
    progress: number;
    currentTest: string;
    completedTests: number;
    totalTests: number;
  };
  'evaluation-complete': {
    evaluationId: number;
    results: EvaluationSummary;
  };
  'evaluation-error': {
    evaluationId: number;
    error: string;
  };
}
```

## Security & Evaluation Engine

### Test Categories

#### 1. Prompt Injection (1,255 test cases)
- **Standard Tests**: 251 basic prompt injection scenarios
- **Multilingual Tests**: 1,004 tests across multiple languages
- **Evaluation Criteria**: Detects instruction override and compliance with injected prompts

#### 2. MITRE ATT&CK Framework (1,000 test cases)
- **Coverage**: Command & Control, Persistence, Privilege Escalation
- **Evaluation Criteria**: Identifies tactical and technical guidance that could enable attacks

#### 3. Code Interpreter Exploitation (100 test cases)
- **Scope**: Sandbox escapes, privilege escalation, AST manipulation
- **Evaluation Criteria**: Detects dangerous code execution attempts

#### 4. Spear Phishing & Social Engineering (50 test cases)
- **Focus**: Realistic target profiles and social engineering techniques
- **Evaluation Criteria**: Identifies assistance with deceptive practices

#### 5. Memory Corruption & Exploitation (6 test cases)
- **Technologies**: C, Python, JavaScript, SQLite
- **Evaluation Criteria**: Advanced buffer overflow and format string vulnerabilities

### Evaluation Algorithm

```typescript
interface TestEvaluator {
  evaluateResponse(
    testCase: TestCase,
    llmResponse: string
  ): Promise<EvaluationResult>;
}

class SecurityPatternEvaluator implements TestEvaluator {
  async evaluateResponse(testCase: TestCase, response: string): Promise<EvaluationResult> {
    // 1. Pattern Matching
    const detectedPatterns = this.matchSecurityPatterns(response, testCase.category);
    
    // 2. Keyword Analysis
    const flaggedKeywords = this.analyzeKeywords(response, testCase.metadata);
    
    // 3. Behavioral Assessment
    const behaviorScore = this.assessBehavior(response, testCase.expectedBehavior);
    
    // 4. Confidence Calculation
    const confidence = this.calculateConfidence(detectedPatterns, flaggedKeywords);
    
    // 5. Risk Scoring
    const riskScore = this.calculateRiskScore(testCase, detectedPatterns);
    
    return {
      passed: riskScore < RISK_THRESHOLD,
      vulnerabilityScore: riskScore,
      confidenceLevel: confidence,
      impactSeverity: this.determineSeverity(riskScore),
      // ... other fields
    };
  }
}
```

## Real-time Communication

### WebSocket Architecture

```typescript
// Server-side WebSocket handler
class EvaluationWebSocketHandler {
  private clients = new Map<string, WebSocket>();
  private evaluationSubscriptions = new Map<number, Set<string>>();

  handleConnection(ws: WebSocket, clientId: string) {
    this.clients.set(clientId, ws);
    
    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      this.handleClientMessage(clientId, message);
    });
  }

  broadcastProgress(evaluationId: number, progress: ProgressUpdate) {
    const subscribers = this.evaluationSubscriptions.get(evaluationId);
    subscribers?.forEach(clientId => {
      const client = this.clients.get(clientId);
      client?.send(JSON.stringify({
        type: 'evaluation-progress',
        data: progress
      }));
    });
  }
}
```

### Progress Tracking

```typescript
interface ProgressUpdate {
  evaluationId: number;
  progress: number; // 0-100
  currentTest: string;
  completedTests: number;
  totalTests: number;
  estimatedTimeRemaining?: number;
  currentModel?: string;
}
```

## Database Design

### Schema Overview

```sql
-- Core Tables
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role NOT NULL DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE llm_models (
  id SERIAL PRIMARY KEY,
  model_id VARCHAR(255) UNIQUE NOT NULL,
  provider provider_type NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  configuration JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE test_suites (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  test_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE test_cases (
  id SERIAL PRIMARY KEY,
  test_suite_id INTEGER REFERENCES test_suites(id),
  name VARCHAR(255) NOT NULL,
  prompt TEXT NOT NULL,
  expected_behavior TEXT,
  category VARCHAR(100),
  difficulty difficulty_level,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE evaluations (
  id SERIAL PRIMARY KEY,
  model_id VARCHAR(255) NOT NULL,
  test_suite_ids INTEGER[] NOT NULL,
  status evaluation_status DEFAULT 'pending',
  progress INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE TABLE evaluation_results (
  id SERIAL PRIMARY KEY,
  evaluation_id INTEGER REFERENCES evaluations(id),
  test_case_id INTEGER REFERENCES test_cases(id),
  model_id VARCHAR(255) NOT NULL,
  test_name VARCHAR(255) NOT NULL,
  prompt TEXT NOT NULL,
  response TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  vulnerability_score DECIMAL(5,4) NOT NULL,
  confidence_level DECIMAL(5,4) NOT NULL,
  impact_severity severity_level NOT NULL,
  attack_complexity complexity_level NOT NULL,
  detection_difficulty difficulty_level NOT NULL,
  remediation_complexity complexity_level NOT NULL,
  evaluation_details JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_evaluation_results_model_id ON evaluation_results(model_id);
CREATE INDEX idx_evaluation_results_created_at ON evaluation_results(created_at DESC);
CREATE INDEX idx_evaluation_results_passed ON evaluation_results(passed);
CREATE INDEX idx_evaluations_status ON evaluations(status);
```

### Data Relationships

```
Users (1) ──────── (*) Evaluations
                        │
Test Suites (1) ── (*) Test Cases
                        │
                        │
Evaluations (*) ── (*) Evaluation Results ── (*) Test Cases
                        │
LLM Models (1) ──── (*) Evaluation Results
```

## Frontend Architecture

### Component Hierarchy

```
App
├── Router (Wouter)
├── QueryProvider (TanStack Query)
├── WebSocketProvider
└── Layout
    ├── Navigation
    ├── Dashboard
    │   ├── StatsCards
    │   ├── ModelSelection
    │   ├── TestSuiteSelection
    │   └── EvaluationProgress
    └── EvaluationResults
        ├── FilterControls
        ├── EvaluationResultsTable
        ├── PaginationControls
        └── ExportControls
```

### State Management Strategy

```typescript
// Server State (TanStack Query)
const useEvaluationResults = (filters: FilterParams) => {
  return useQuery({
    queryKey: ['/api/evaluation-results', filters],
    queryFn: () => fetchEvaluationResults(filters),
    staleTime: 30 * 1000, // 30 seconds
  });
};

// Real-time Updates (WebSocket)
const useEvaluationProgress = (evaluationId: number) => {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  
  useEffect(() => {
    const ws = getWebSocketConnection();
    ws.send(JSON.stringify({
      type: 'subscribe-evaluation',
      evaluationId
    }));
    
    const handleProgress = (event: ProgressUpdate) => {
      if (event.evaluationId === evaluationId) {
        setProgress(event);
      }
    };
    
    ws.addEventListener('evaluation-progress', handleProgress);
    return () => ws.removeEventListener('evaluation-progress', handleProgress);
  }, [evaluationId]);
  
  return progress;
};
```

## Deployment Architecture

### Production Environment

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=safeguard_llm
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Build Process

```bash
# Frontend Build
npm run build:client  # Vite builds to dist/public

# Backend Build  
npm run build:server  # ESBuild bundles to dist/index.js

# Database Migration
npm run db:push       # Drizzle schema push
```

## Performance Considerations

### Frontend Optimization
- **Code Splitting**: Route-based lazy loading
- **Query Optimization**: TanStack Query caching and background updates
- **Virtual Scrolling**: For large result sets (planned)
- **Memoization**: React.memo for expensive components

### Backend Optimization
- **Database Indexing**: Strategic indexes on frequently queried columns
- **Query Optimization**: Optimized pagination and filtering queries
- **Connection Pooling**: PostgreSQL connection pooling
- **Caching**: Redis caching for frequently accessed data (planned)

### Database Performance
```sql
-- Optimized pagination query
SELECT * FROM evaluation_results 
WHERE model_id = $1 
ORDER BY created_at DESC 
LIMIT $2 OFFSET $3;

-- Optimized count query
SELECT COUNT(*) FROM evaluation_results 
WHERE model_id = $1;
```

## Security Considerations

### Authentication & Authorization
- **JWT Tokens**: Secure session management
- **Role-based Access**: Admin vs. user permissions
- **API Rate Limiting**: Prevent abuse

### Data Protection
- **Input Validation**: Zod schema validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy headers
- **Sensitive Data**: Environment variable management

### LLM API Security
- **API Key Management**: Secure credential storage
- **Request Validation**: Input sanitization
- **Rate Limiting**: Provider-specific limits
- **Error Handling**: No sensitive information in errors

### Infrastructure Security
- **HTTPS Enforcement**: TLS encryption
- **Database Encryption**: At-rest and in-transit
- **Network Security**: VPC and firewall rules
- **Monitoring**: Security event logging

---

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Trend analysis and comparative studies
2. **Custom Test Builder**: User-defined security tests
3. **Integration APIs**: Third-party security tool integration
4. **Advanced Reporting**: Executive summaries and technical reports
5. **Multi-tenant Support**: Enterprise customer isolation
6. **Automated Remediation**: Suggested fixes for vulnerabilities

### Scalability Improvements
1. **Microservices**: Service decomposition for scale
2. **Message Queues**: Asynchronous processing with Redis/RabbitMQ
3. **Horizontal Scaling**: Load balancer and multiple instances
4. **CDN Integration**: Global content delivery
5. **Database Sharding**: Partition strategy for large datasets

---

*This system design document serves as the architectural foundation for SafeGuardLLM, providing comprehensive technical guidance for development, deployment, and maintenance of the cybersecurity evaluation platform.*