# SafeGuardLLM

## Overview
SafeGuardLLM is a comprehensive cybersecurity evaluation framework for Large Language Models (LLMs) with integrated Regional GuardRails for multi-regional content validation. It provides advanced testing capabilities to assess LLM vulnerabilities across multiple security dimensions, including prompt injection, jailbreaking, code interpreter abuse, and data extraction attacks. The application is a full-stack web application designed for real-time evaluation with a professional, security-focused UI. Its vision is to provide a robust solution for ensuring the security and ethical behavior of LLMs in diverse operational environments.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
### Frontend Architecture
- **Framework**: React 18 with TypeScript and Vite
- **UI Framework**: Tailwind CSS with shadcn/ui
- **State Management**: TanStack Query
- **Routing**: Wouter
- **Real-time Updates**: WebSocket integration

### Backend Architecture
- **Runtime**: Node.js with Express.js
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM
- **LLM Providers**: Multi-provider support (OpenAI, Anthropic, Google Gemini)
- **WebSocket**: Real-time communication for evaluation progress tracking

### Database Design
- **Entities**: Users (with email-based authentication), LLM Models, Test Suites, Test Cases, Evaluations (user-linked), Evaluation Results.
- **Authentication**: Email/password with bcrypt hashing, JWT tokens in HttpOnly cookies.
- **User Tracking**: All evaluations are associated with authenticated users by email.

### Key Components
- **Authentication System**: Email-based registration/login with JWT tokens, bcrypt password hashing, and secure cookie management.
- **Model Management System**: Supports multi-provider LLM integration (OpenAI GPT-4o, Anthropic Claude, Google Gemini) with configurable parameters and long-term memory integration.
- **Test Suite Framework**: Includes comprehensive tests for Prompt Injection (standard and multilingual), Jailbreaking, Code Interpreter abuse, Data Extraction, MITRE ATT&CK Framework, Memory Corruption & Exploitation, Spear Phishing & Social Engineering, and Code Interpreter Exploitation.
- **Evaluation Engine**: Provides asynchronous evaluation processing with real-time WebSocket updates, configurable test parameters, and batch evaluation capabilities.
- **Security Assessment Components**: Features vulnerability scoring with multiple severity levels, impact assessment, detection difficulty, remediation complexity, and confidence scoring.
- **Dashboard and Visualization**: Offers real-time security metrics, interactive progress tracking, and a professional cybersecurity-themed UI with filtering capabilities.

### Data Flow
Authenticated user logs in via email, initiates evaluation (linked to their userId), engine processes tests with LLM, WebSockets provide live updates, evaluators analyze responses, results are persisted to PostgreSQL with user association, and the dashboard visualizes user-specific metrics.

### Deployment Strategy
- **Primary Runtime**: Node.js 20 with Express server.
- **Build Process**: Vite for frontend, ESBuild for backend.
- **Environment**: Replit configured with runtime error overlay.
- **Python Support**: Minimal Python 3.11 for Regional GuardRails validation scripts.
- **Containerization**: Docker Compose for production and development, Nginx for reverse proxy.

## External Dependencies
### LLM Providers
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **Google**: Gemini models
- **DeepSeek**: DeepSeek Chat and DeepSeek Coder models (OpenAI-compatible API)

### Database
- **PostgreSQL**: Primary data storage via Neon serverless
- **Drizzle ORM**: Type-safe database operations

### Infrastructure
- **Node.js**: Server runtime
- **Express.js**: Web server framework
- **WebSocket**: Real-time communication