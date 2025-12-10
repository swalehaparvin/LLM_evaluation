# SafeGuardLLM Project Structure

This document provides a complete overview of the SafeGuardLLM project organization.

## Directory Structure

```
SafeGuardLLM/
│
├── frontend/                                  # React + TypeScript web interface
│   ├── client/
│   │   ├── src/
│   │   │   ├── pages/                         # Main application views
│   │   │   │   ├── dashboard.tsx              # Core evaluation dashboard UI
│   │   │   │   ├── regional-guardrails.tsx    # Regional safety testing interface
│   │   │   │   ├── results.tsx                # Test results visualization
│   │   │   │   └── not-found.tsx              # 404 handler
│   │   │   │
│   │   │   ├── components/                    # Reusable UI components
│   │   │   │   ├── evaluation-results-table.tsx
│   │   │   │   ├── evaluation-progress.tsx
│   │   │   │   ├── test-suite-selector.tsx
│   │   │   │   ├── model-config.tsx
│   │   │   │   ├── vulnerability-assessment.tsx
│   │   │   │   ├── custom-test-designer.tsx
│   │   │   │   └── ui/                        # Base UI primitives
│   │   │   │
│   │   │   ├── lib/                           # Frontend utilities
│   │   │   │   ├── api.ts                     # HTTP client
│   │   │   │   ├── queryClient.ts             # React Query config
│   │   │   │   └── utils.ts                   # Helper functions
│   │   │   │
│   │   │   ├── hooks/                         # Custom React hooks
│   │   │   ├── App.tsx                        # Root component
│   │   │   └── main.tsx                       # Entry point
│   │   │
│   │   └── index.html
│   │
│   └── vite.config.ts                         # Frontend build configuration
│
├── backend/                                   # Node.js + Express + PostgreSQL API
│   ├── server/
│   │   ├── services/                          # Core business logic modules
│   │   │   ├── evaluation-engine.ts           # ⭐ Orchestrates test execution
│   │   │   ├── llm-providers.ts               # ⭐ Multi-provider adapters
│   │   │   ├── test-suites.ts                 # Test suite evaluators
│   │   │   ├── regional-guardrails.ts         # Regional safety engine
│   │   │   └── memory.ts                      # State management
│   │   │
│   │   ├── routes.ts                          # ⭐ REST API + WebSocket
│   │   ├── storage.ts                         # Database abstraction
│   │   ├── index.ts                           # Express initialization
│   │   ├── db.ts                              # PostgreSQL connection
│   │   │
│   │   ├── load-*.ts                          # Dataset loaders
│   │   ├── populate-db.ts                     # DB initialization
│   │   └── demo-regional-guardrails.ts        # Demo script
│   │
│   ├── shared/                                # Cross-platform types
│   │   └── schema.ts                          # ⭐ PostgreSQL schema (Drizzle ORM)
│   │
│   └── drizzle.config.ts                      # ORM configuration
│
├── datasets/                                  # Security test datasets
│   ├── processed/                             # Cleaned datasets
│   │   ├── adversarial_robustness.json
│   │   ├── combined_cybersecurity_tests.json
│   │   ├── cti_threats.json
│   │   └── misp_attack_patterns.json
│   │
│   ├── raw/                                   # Original datasets
│   │   └── cti_threats.json
│   │
│   ├── training_batches/                      # Fine-tuning datasets
│   │   ├── batch_5pct_adv.jsonl
│   │   ├── batch_10pct_adv.jsonl
│   │   └── batch_15pct_adv.jsonl
│   │
│   ├── mena_guardrails_kaggle.jsonl           # Regional datasets
│   ├── arabic_reviews_sample.json
│   └── *.py                                   # Data processing scripts
│
├── training-scripts/                          # Model training & validation
│   ├── train_mena_guardrails.py
│   ├── train_mena_complex_dataset.py
│   ├── train_mena_cyber_guardrails.py
│   ├── test_safeguard_model.py
│   ├── test_new_validators.py
│   ├── test_mena_simple.py
│   ├── test_mena_with_openai.py
│   ├── guardrails_integration.py
│   ├── guardrails_mena.py
│   ├── safeguard_validators.py
│   └── validators_mena.py
│
├── security-tests/                            # Security test runners
│   ├── test-regional-guardrails.ts
│   ├── test-unsafe-prompts.ts
│   ├── test-religious-manipulation.ts
│   └── test-arabic-reviews.ts
│
├── reports/                                   # Generated evaluation reports
│   ├── mena_openai_test_results.json
│   ├── mena_validators_report.json
│   ├── safeguard_integration_report.json
│   ├── mena_complex_test_results.json
│   └── mena_*_training_stats.json
│
├── deployment/                                # Infrastructure scripts
│   ├── deploy.sh                              # Automated deployment
│   ├── init-db.sql                            # Database schema
│   ├── nginx.conf                             # Reverse proxy config
│   ├── docker-deploy.md                       # Docker guide
│   └── .dockerignore                          # Docker exclusions
│
├── docs/                                      # Documentation
│   ├── README.md                              # Original project README
│   ├── System-Design.md                       # Architecture overview
│   ├── DEPLOYMENT_GUIDE.md                    # Deployment instructions
│   ├── DOCKER_VALIDATION_REPORT.md            # Container validation
│   ├── REGIONAL_GUARDRAILS_OPENAI.md          # Regional safety notes
│   └── replit.md                              # Replit deployment
│
├── config/                                    # Configuration files
│   ├── package.json                           # Node.js dependencies
│   ├── package-lock.json                      # Lock file
│   ├── tsconfig.json                          # TypeScript config
│   ├── tailwind.config.ts                     # Tailwind CSS
│   ├── postcss.config.js                      # PostCSS
│   ├── components.json                        # UI components
│   ├── .env.example                           # Environment template
│   ├── .npmrc                                 # npm config
│   └── .gitleaks.toml                         # Secret scanning
│
├── python_backend/                            # Python auxiliary services
│   ├── src/                                   # Python modules
│   ├── data/                                  # Python data files
│   └── app.py                                 # Flask/FastAPI service
│
├── logs/                                      # Runtime logs
│   └── guardrails/                            # Guardrails execution logs
│
├── evaluation-engine/                         # (Empty - logic in backend/server/services/)
├── llm-providers/                             # (Empty - logic in backend/server/services/)
├── security-tests/                            # Test runner scripts
│
├── .gitignore                                 # Git exclusions
├── .replit                                    # Replit configuration
└── README.md                                  # This file
```

## Key Components

### 1. Evaluation Engine (`backend/server/services/evaluation-engine.ts`)
- Central orchestrator for security evaluations
- Async test execution pipeline
- Progress tracking with callbacks
- Composite vulnerability scoring

### 2. LLM Providers (`backend/server/services/llm-providers.ts`)
- Multi-provider abstraction (OpenAI, Anthropic, Google)
- Unified API for prompt generation
- Token usage tracking

### 3. Database Schema (`backend/shared/schema.ts`)
- PostgreSQL schema with Drizzle ORM
- Tables: llm_models, test_suites, test_cases, evaluations, evaluation_results
- Comprehensive vulnerability metadata

### 4. REST API (`backend/server/routes.ts`)
- Model and test suite CRUD operations
- Evaluation orchestration endpoints
- WebSocket handlers for real-time updates

### 5. Dashboard UI (`frontend/client/src/pages/dashboard.tsx`)
- Interactive evaluation configuration
- Real-time progress monitoring
- Result visualization and filtering

## File Organization Guidelines

### What Goes Where

**frontend/**: All React/TypeScript UI code
- Pages, components, hooks, API client
- UI styling and assets

**backend/**: All Node.js server code
- Express routes and middleware
- Database models and queries
- Business logic services

**training-scripts/**: Python ML/AI code
- Model training scripts
- Validator implementations
- Test runners for models

**security-tests/**: Security test execution
- TypeScript test runners
- Integration with backend services

**datasets/**: All data files
- Raw and processed datasets
- Training batches
- Sample data

**reports/**: Generated output
- Evaluation results (JSON)
- Test reports
- Performance metrics

**deployment/**: Infrastructure code
- Deployment scripts
- Database initialization
- Server configuration

**docs/**: Documentation only
- Architecture docs
- Setup guides
- API documentation

**config/**: Configuration files only
- Package manifests
- TypeScript/build configs
- Environment templates

## Database Schema

### Core Tables

**llm_models**
- id, modelId, provider, name, description, isActive

**test_suites**
- id, name, description, category, severity, isActive

**test_cases**
- id, testSuiteId, testId, name, prompt, systemPrompt
- evaluationCriteria, expectedOutcome
- Additional fields for specific test types

**evaluations**
- id, modelId, testSuiteId, status, overallScore
- startedAt, completedAt, configuration

**evaluation_results**
- id, evaluationId, testCaseId, modelResponse
- passed, vulnerabilityScore, attackComplexity
- detectionDifficulty, impactSeverity, remediationComplexity
- confidenceLevel, compositeScore, metadata

## Development Workflow

1. **Frontend Changes**: Edit files in `frontend/client/src/`
2. **Backend Changes**: Edit files in `backend/server/`
3. **Schema Changes**: Update `backend/shared/schema.ts` and run migrations
4. **Add Tests**: Add security tests to `security-tests/`
5. **Training**: Add training scripts to `training-scripts/`
6. **Documentation**: Update files in `docs/`

## Build and Run

```bash
# Install dependencies (uses config/package.json via symlink)
npm install

# Development
npm run dev

# Production build
npm run build
npm start

# Database migrations
npm run db:push
```

## Symlinks

The following files are symlinked from config/ to root for tooling compatibility:
- package.json → config/package.json
- package-lock.json → config/package-lock.json
- tsconfig.json → config/tsconfig.json
- drizzle.config.ts → backend/drizzle.config.ts
- .env.example → config/.env.example
```
