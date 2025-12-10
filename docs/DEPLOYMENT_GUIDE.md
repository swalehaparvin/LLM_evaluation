# SafeGuardLLM - Deployment Guide

This guide will help you deploy SafeGuardLLM to Replit and other cloud platforms.

## Prerequisites

1. A cloud platform account (Replit recommended)
2. API keys for the LLM providers you want to test:
   - `OPENAI_API_KEY` - For GPT models
   - `ANTHROPIC_API_KEY` - For Claude models
   - `GEMINI_API_KEY` - For Google Gemini models

## Replit Deployment (Recommended)

### 1. Project Configuration

The project is configured for seamless Replit deployment:
- **Primary Runtime**: Node.js 20 with Express server
- **Python Support**: Minimal Python 3.11 for MENA validation scripts only
- **Database**: PostgreSQL (automatically provisioned)
- **Port**: Server runs on port 5000

### 2. Build and Deploy Commands

```bash
# Build the application
npm run build

# Start production server
npm start
```

### 3. Important Notes

- **No Python package manager needed**: MENA validation scripts use only Python standard library
- **No pyproject.toml or requirements.txt**: Removed to avoid deployment conflicts
- **Single runtime focus**: Node.js is the primary runtime with minimal Python for validation

## Generic Cloud Platform Deployment

### 1. Project Setup

1. Clone or upload the project to your platform
2. Ensure Node.js 20+ is available
3. Ensure Python 3.11+ is available (for MENA validation only)

### 2. Build Configuration

```json
{
  "build": "npm run build",
  "start": "npm start",
  "port": 5000
}
```

### 3. Required Files

Essential files for deployment:
- `package.json` (Node.js dependencies and scripts)
- All `client/`, `server/`, `shared/` directories
- `validators_mena.py` (MENA validation script)
- `vite.config.ts` and `tsconfig.json`
- Database migration files in `migrations/`

### 3. Configure Environment Variables

Add your API keys as environment variables:
- `OPENAI_API_KEY` (if testing OpenAI models)
- `ANTHROPIC_API_KEY` (if testing Anthropic models)
- `GEMINI_API_KEY` (if testing Google Gemini models)
- `DATABASE_URL` (automatically configured on Replit)

### 4. Database Setup

Run database migrations after deployment:
```bash
npm run db:push
```

## Key Files for Deployment

- **`package.json`**: Node.js dependencies and build scripts
- **`validators_mena.py`**: MENA content validation (uses Python standard library only)
- **`server/`**: Express backend server
- **`client/`**: React frontend application
- **`shared/schema.ts`**: Database schema definitions

## How It Works

1. The Express server serves both API and static frontend files
2. Python scripts are called via child process for MENA validation
3. WebSocket connections handle real-time evaluation updates
4. PostgreSQL database stores all evaluation data

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Ensure Node.js 20+ is installed
   - Run `npm install` to install dependencies
   - Check that all TypeScript files compile without errors

2. **Python Script Issues**:
   - Verify Python 3.11+ is available
   - The `validators_mena.py` script only uses standard library
   - No external Python packages are required

3. **API Key Issues**:
   - Verify keys are set as environment variables
   - Check key format and permissions
   - Test keys with provider APIs directly

4. **Port Configuration**:
   - Application runs on port 5000
   - Ensure port is not blocked by firewall

5. **Database Connection**:
   - Verify DATABASE_URL environment variable is set
   - Run `npm run db:push` to apply migrations
   - Check PostgreSQL is accessible

### Deployment Checklist:

✅ Remove any `pyproject.toml` or `requirements.txt` files
✅ Ensure `package.json` has correct build/start scripts
✅ Python 3.11+ available for MENA validation
✅ PostgreSQL database configured
✅ Environment variables set (API keys, DATABASE_URL)
✅ Port 5000 is available

## Post-Deployment

1. Test the build process: `npm run build`
2. Verify the production server starts: `npm start`
3. Test MENA validation endpoint: `/api/validate-mena`
4. Run a small evaluation to verify LLM providers work
5. Check WebSocket connections for real-time updates
6. Test PDF export functionality

## Support

If you encounter deployment issues:
1. Check that no Python package managers (pip, uv) are configured
2. Verify Node.js is the primary runtime
3. Ensure Python scripts use only standard library
4. Test locally with `npm run dev` first
5. Review server logs for specific error messages