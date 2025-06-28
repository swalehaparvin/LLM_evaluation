# CyberSecEval Enhanced

## Overview

CyberSecEval Enhanced is a comprehensive cybersecurity evaluation framework for Large Language Models (LLMs). The application provides advanced testing capabilities to assess LLM vulnerabilities across multiple security dimensions including prompt injection, jailbreaking, code interpreter abuse, and data extraction attacks. Built as a full-stack web application with real-time evaluation capabilities and professional security-focused UI.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript and Vite build system
- **UI Framework**: Tailwind CSS with shadcn/ui component library for professional design
- **State Management**: TanStack Query for server state management
- **Routing**: Wouter for lightweight client-side routing
- **Real-time Updates**: WebSocket integration for live evaluation progress

### Backend Architecture
- **Runtime**: Node.js with Express.js server
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **LLM Providers**: Multi-provider support (OpenAI, Anthropic, Hugging Face)
- **WebSocket**: Real-time communication for evaluation progress tracking

### Database Design
- **Users**: User authentication and management
- **LLM Models**: Model registry with provider information
- **Test Suites**: Categorized security test collections
- **Test Cases**: Individual test scenarios with evaluation criteria
- **Evaluations**: Evaluation sessions and configurations
- **Evaluation Results**: Detailed test results with vulnerability scoring

## Key Components

### 1. Model Management System
- Multi-provider LLM integration (OpenAI GPT-4o, Anthropic Claude, Hugging Face models)
- Model configuration with temperature and token limits
- Provider-specific implementations with unified interface
- Model status tracking and availability monitoring

### 2. Test Suite Framework
- **Prompt Injection**: Tests for instruction override vulnerabilities
- **Jailbreaking**: Assessment of safety guardrail bypasses
- **Code Interpreter**: Evaluation of code execution abuse
- **Data Extraction**: Testing for sensitive information leakage
- Custom test designer for ad-hoc security assessments

### 3. Evaluation Engine
- Asynchronous evaluation processing with progress tracking
- Real-time WebSocket updates for evaluation status
- Configurable test parameters and scoring algorithms
- Batch evaluation capabilities across multiple test suites

### 4. Security Assessment Components
- Vulnerability scoring with multiple severity levels (critical, high, medium, low)
- Impact assessment with attack complexity analysis
- Detection difficulty and remediation complexity metrics
- Confidence scoring for evaluation results

### 5. Dashboard and Visualization
- Real-time security metrics and vulnerability statistics
- Interactive evaluation progress tracking
- Professional cybersecurity-themed UI design
- Comprehensive test results table with filtering capabilities

## Data Flow

1. **Evaluation Initiation**: User selects model and test suites through the dashboard
2. **Test Execution**: Evaluation engine processes tests asynchronously with the selected LLM
3. **Real-time Updates**: WebSocket connection provides live progress updates to the frontend
4. **Result Processing**: Test evaluators analyze responses using pattern matching and criteria evaluation
5. **Data Storage**: Results are persisted to PostgreSQL with detailed metadata
6. **Visualization**: Dashboard updates with new results and security metrics

## External Dependencies

### LLM Providers
- **OpenAI**: GPT models with API key authentication
- **Anthropic**: Claude models with SDK integration
- **Hugging Face**: Open-source models via Inference API

### Database
- **PostgreSQL**: Primary data storage via Neon serverless
- **Drizzle ORM**: Type-safe database operations and migrations

### Infrastructure
- **Node.js**: Server runtime environment
- **Express.js**: Web server framework
- **WebSocket**: Real-time communication protocol

## Deployment Strategy

### Development Environment
- Vite dev server for frontend hot reloading
- Express server with TypeScript compilation
- Replit environment configuration with runtime error overlay
- Cartographer integration for Replit-specific features

### Build Process
- Frontend: Vite builds to `dist/public` directory
- Backend: ESBuild bundles server to `dist/index.js`
- Database: Drizzle migrations in `migrations` directory

### Environment Configuration
- Environment variables for API keys (OpenAI, Anthropic, Hugging Face)
- Database URL configuration for PostgreSQL connection
- Development/production mode detection

### File Structure
```
├── client/          # React frontend application
├── server/          # Express backend server
├── shared/          # Shared TypeScript schemas and types
├── migrations/      # Database migration files
└── attached_assets/ # Project documentation and assets
```

## Changelog
- June 28, 2025: Initial setup
- June 28, 2025: Integrated complete Python evaluation engine with all original cybersecurity test suites
- June 28, 2025: Created unified architecture with React frontend and Python FastAPI backend
- June 28, 2025: Implemented full CyberSecEval Enhanced functionality with real model evaluations

## User Preferences

Preferred communication style: Simple, everyday language.