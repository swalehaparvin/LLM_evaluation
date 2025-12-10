# SafeGuardLLM - Cybersecurity Evaluation Framework

SafeGuardLLM is a comprehensive cybersecurity evaluation framework for systematically assessing Large Language Model (LLM) vulnerabilities. The application provides advanced testing capabilities to assess LLM vulnerabilities across multiple security dimensions including prompt injection, jailbreaking, code interpreter abuse, and data extraction attacks.

## Features

- **Multi-Provider LLM Support**: Evaluate OpenAI GPT-4, Anthropic Claude, and Google Gemini models
- **Comprehensive Test Suites**: 2,417+ test cases spanning:
  - Prompt Injection (251 standard + 1004 multilingual test cases)
  - MITRE ATT&CK Framework (1000 test cases)
  - Jailbreaking and Safety Bypass Testing
  - Code Interpreter Exploitation (100 advanced test cases)
  - Memory Corruption & Exploitation (6 test cases)
  - Spear Phishing & Social Engineering (50 test cases)
  - Data Extraction Vulnerabilities
  - Regional Content Validation (multi-region guardrails)

- **Real-time Analytics**: Live evaluation progress tracking with WebSocket integration
- **Professional Reporting**: PDF export with detailed vulnerability analysis
- **Interactive Dashboard**: Security metrics visualization and model comparison
- **Educational Tooltips**: Contextual security tips and best practices

## Technology Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express + TypeScript
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time**: WebSocket integration
- **Build System**: Vite + ESBuild
- **Python Support**: Minimal Python 3.11 for regional validation (standard library only)

## API Keys Required

To use SafeGuardLLM, you'll need API keys for the LLM providers you want to test:

- `OPENAI_API_KEY` - For GPT models
- `ANTHROPIC_API_KEY` - For Claude models  
- `GEMINI_API_KEY` - For Google Gemini models

## Deployment

### Quick Start (Replit)

1. Clone the repository to Replit
2. Set environment variables (API keys)
3. Run `npm install` to install dependencies
4. Run `npm run build` to build the application
5. Run `npm start` to start the production server

### Build Commands

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start

# Development mode
npm run dev

# Database migrations
npm run db:push
```

## Local Development

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up PostgreSQL database
4. Configure environment variables in `.env` file
5. Run database migrations: `npm run db:push`
6. Start the development server: `npm run dev`

## Deployment Requirements

### System Requirements
- Node.js 20 or higher
- Python 3.11 or higher (for regional validation)
- PostgreSQL database
- 2GB RAM minimum
- 1GB disk space

### Important Deployment Notes
- **No Python package manager files**: The project intentionally excludes `pyproject.toml` and `requirements.txt` to avoid deployment conflicts
- **Python scripts use standard library only**: The `validators_mena.py` script requires no external Python packages
- **Single package.json**: All dependencies are managed through npm
- **Port 5000**: The application is configured to run on port 5000

## Security Focus

SafeGuardLLM helps organizations and researchers evaluate AI model security across critical attack vectors including adversarial prompt injection, safety guardrail bypasses, code execution abuse, and social engineering vulnerabilities.

## License

MIT License - See LICENSE file for details.