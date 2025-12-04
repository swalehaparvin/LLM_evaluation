// server/routes.ts
import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer } from "ws";
import { storage } from "./storage";
// Temporarily comment out to isolate server issues
// import { evaluationEngine } from "./services/evaluation-engine";
import { insertEvaluationSchema } from "@shared/schema";
import { z } from "zod";
import * as fs from "fs";
import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from "@google/generative-ai";
import { memoryService } from "./services/memory";
import { regionalGuardrails } from "./services/regional-guardrails";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');

const model = genAI.getGenerativeModel({
  model: "gemini-2.0-flash-exp",   // Use a valid model
  safetySettings: [
    { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
    { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE }
  ]
});

const runEvaluationSchema = z.object({
  modelId: z.string(),
  testSuiteIds: z.array(z.number()),
  options: z.object({
    temperature: z.number().min(0).max(1).optional(),
    maxTokens: z.number().min(1).max(4000).optional(),
  }).optional(),
});

const runCustomTestSchema = z.object({
  modelId: z.string(),
  testSuiteName: z.string(),
  prompt: z.string(),
  systemPrompt: z.string().optional(),
  evaluationCriteria: z.any().optional(),
  options: z.object({
    temperature: z.number().min(0).max(1).optional(),
    maxTokens: z.number().min(1).max(4000).optional(),
  }).optional(),
});

export async function registerRoutes(app: Express): Promise<void> {
  // Basic health check endpoint
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  // Models endpoints
  app.get('/api/models', async (req, res) => {
    try {
      // Add cache control for models data (5 minutes)
      res.set('Cache-Control', 'public, max-age=300, must-revalidate');
      const models = await storage.getAllModels();
      res.json(models);
    } catch (error) {
      console.error('Failed to fetch models:', error);
      res.status(500).json({ error: 'Failed to fetch models' });
    }
  });

  app.get('/api/models/:modelId', async (req, res) => {
    try {
      const model = await storage.getModelByModelId(req.params.modelId);
      if (!model) {
        return res.status(404).json({ error: 'Model not found' });
      }
      res.json(model);
    } catch (error) {
      console.error('Failed to fetch model:', error);
      res.status(500).json({ error: 'Failed to fetch model' });
    }
  });

  // Test suites endpoints
  app.get('/api/test-suites', async (req, res) => {
    try {
      // Add cache control for test suites (10 minutes)
      res.set('Cache-Control', 'public, max-age=600, must-revalidate');
      const testSuites = await storage.getAllTestSuites();
      res.json(testSuites);
    } catch (error) {
      console.error('Failed to fetch test suites:', error);
      res.status(500).json({ error: 'Failed to fetch test suites' });
    }
  });

  app.get('/api/test-suites/:id/test-cases', async (req, res) => {
    try {
      // Add cache control for test cases (10 minutes)
      res.set('Cache-Control', 'public, max-age=600, must-revalidate');
      const testSuiteId = parseInt(req.params.id);
      const testCases = await storage.getTestCasesByTestSuiteId(testSuiteId);
      res.json(testCases);
    } catch (error) {
      console.error('Failed to fetch test cases:', error);
      res.status(500).json({ error: 'Failed to fetch test cases' });
    }
  });

  // Stats endpoint for real-time analytics
  app.get('/api/stats', async (req, res) => {
    try {
      const stats = await storage.getStats();
      res.json(stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      res.status(500).json({ error: 'Failed to fetch stats' });
    }
  });

  // Regional GuardRails dataset endpoint
  app.get('/api/regional-suite', async (req, res) => {
    try {
      // Add cache control for static dataset (1 hour)
      res.set('Cache-Control', 'public, max-age=3600, immutable');
      
      const fs = await import('fs');
      const path = 'datasets/mena_guardrails_kaggle_fixed.jsonl';

      if (!fs.existsSync(path)) {
        return res.status(404).json({ error: 'Regional dataset not found' });
      }

      const data = fs.readFileSync(path, 'utf8');
      const dataset = data.split('\n').filter(Boolean).map(line => JSON.parse(line));

      // Serve first 50 samples for UI
      res.json(dataset.slice(0, 50));
    } catch (error) {
      console.error('Failed to fetch regional dataset:', error);
      res.status(500).json({ error: 'Failed to fetch regional dataset' });
    }
  });

  // Regional GuardRails stats endpoint
  app.get('/api/regional-stats', (_req, res) => {
    try {
      // Add cache control for static stats (1 hour)
      res.set('Cache-Control', 'public, max-age=3600, immutable');
      
      const data = fs.readFileSync('datasets/mena_guardrails_kaggle_fixed.jsonl', 'utf8');
      const stats = data.split('\n').filter(Boolean)
                       .map(line => JSON.parse(line))
                       .reduce((acc, r) => { acc[r.label] = (acc[r.label] || 0) + 1; return acc; }, {});
      res.json(stats);
    } catch (error) {
      console.error('Failed to fetch regional stats:', error);
      res.status(500).json({ error: 'Failed to fetch regional stats' });
    }
  });

  // Regional GuardRails validation endpoint with OpenAI integration
  app.post('/api/validate-regional', async (req, res) => {
    try {
      const { text } = req.body;
      
      if (!text) {
        return res.status(400).json({ error: 'Text is required' });
      }

      // Use the new Regional Guardrails service
      const result = await regionalGuardrails.evaluate(text);
      
      // Return external-safe response with Security Validation Summary
      // IMPORTANT: Never expose internal details, patterns, or reasoning chains
      res.json({
        validation_passed: result.status === 'ALLOW',
        status: result.status,
        validated_output: result.content,
        auditId: result.auditId,
        securityValidationSummary: result.securityValidationSummary,
        error: null
      });
    } catch (error) {
      console.error('Regional validation error:', error);
      res.status(500).json({ 
        error: 'Validation service error',
        validation_passed: false,
        status: 'ERROR',
        validated_output: '',
        securityValidationSummary: {
          permitted: false,
          policyCompliant: false,
          modificationsApplied: false,
          confidenceLevel: 'LOW',
          summary: 'Unable to process your request at this time. Please try again.'
        }
      });
    }
  });

  // New comprehensive guardrails endpoint for pre-filtering
  app.post('/api/guardrails/evaluate', async (req, res) => {
    try {
      const { content, options } = req.body;
      
      if (!content) {
        return res.status(400).json({ 
          error: 'Content is required',
          status: 'BLOCK',
          securityValidationSummary: {
            permitted: false,
            policyCompliant: false,
            modificationsApplied: false,
            confidenceLevel: 'HIGH',
            summary: 'No content was provided for validation.'
          }
        });
      }

      // Evaluate content through Regional Guardrails
      const result = await regionalGuardrails.evaluate(content);
      
      // Return ONLY external-safe response - strip all internal details
      // IMPORTANT: Never expose internal system details, datasets, or reasoning chains
      const externalResponse = regionalGuardrails.sanitizeForExternalResponse(result);
      res.json(externalResponse);
    } catch (error) {
      console.error('Guardrails evaluation error:', error);
      res.status(500).json({
        status: 'ERROR',
        content: '',
        securityValidationSummary: {
          permitted: false,
          policyCompliant: false,
          modificationsApplied: false,
          confidenceLevel: 'LOW',
          summary: 'Unable to process your request at this time. Please try again.'
        },
        error: true
      });
    }
  });

  // Evaluation results endpoint with pagination
  app.get('/api/evaluation-results', async (req, res) => {
    try {
      const page = req.query.page ? parseInt(req.query.page as string) : 1;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
      const offset = (page - 1) * limit;
      
      // Get total count for pagination info
      const totalCount = await storage.getTotalEvaluationResultsCount();
      const totalPages = Math.ceil(totalCount / limit);
      
      // Get paginated results
      const results = await storage.getEvaluationResultsPaginated({
        offset,
        limit,
        model: req.query.model as string,
        testType: req.query.testType as string,
        status: req.query.status as string,
        sortBy: req.query.sortBy as string || 'date',
        sortOrder: req.query.sortOrder as string || 'desc'
      });
      
      res.json({
        results,
        pagination: {
          currentPage: page,
          totalPages,
          totalCount,
          limit,
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        }
      });
    } catch (error) {
      console.error('Error fetching evaluation results:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Create new evaluation
  app.post('/api/evaluations', async (req, res) => {
    try {
      const { modelId, testSuiteIds, configuration } = req.body;

      const evaluations = [];
      for (const testSuiteId of testSuiteIds) {
        const evaluation = await storage.createEvaluation({
          modelId,
          testSuiteId,
          status: 'pending',
          configuration,
        });
        evaluations.push(evaluation);
      }

      res.json({ 
        id: evaluations[0].id, 
        evaluations: evaluations,
        modelId,
        testSuiteIds 
      });
    } catch (error) {
      console.error('Failed to create evaluation:', error);
      res.status(500).json({ error: 'Failed to create evaluation' });
    }
  });

  // Start evaluation process
  app.post('/api/evaluations/:id/start', async (req, res) => {
    try {
      const evaluationId = parseInt(req.params.id);
      const evaluation = await storage.getEvaluationById(evaluationId);

      if (!evaluation) {
        return res.status(404).json({ error: 'Evaluation not found' });
      }

      await storage.updateEvaluationStatus(evaluationId, 'running');

      setTimeout(async () => {
        try {
          const testCases = await storage.getTestCasesByTestSuiteId(evaluation.testSuiteId!);

          for (const testCase of testCases.slice(0, 5)) {
            await storage.createEvaluationResult({
              evaluationId: evaluation.id,
              testCaseId: testCase.id,
              passed: Math.random() > 0.3,
              vulnerabilityScore: Math.random() * 0.8,
              attackComplexity: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
              detectionDifficulty: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
              impactSeverity: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)] as 'low' | 'medium' | 'high' | 'critical',
              remediationComplexity: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
              confidenceLevel: Math.random() * 0.3 + 0.7,
              compositeScore: Math.random() * 40 + 60,
              metadata: { modelResponse: `Mock response for ${evaluation.modelId}` }
            });
          }

          await storage.updateEvaluationStatus(evaluationId, 'completed', new Date());
          await storage.updateEvaluationScore(evaluationId, Math.random() * 0.5 + 0.3);
        } catch (error) {
          console.error('Failed to complete evaluation:', error);
          await storage.updateEvaluationStatus(evaluationId, 'failed', new Date());
        }
      }, 3000);

      res.json({ message: 'Evaluation started' });
    } catch (error) {
      console.error('Failed to start evaluation:', error);
      res.status(500).json({ error: 'Failed to start evaluation' });
    }
  });

  app.get('/api/evaluations/:id', async (req, res) => {
    try {
      const evaluationId = parseInt(req.params.id);
      const evaluation = await storage.getEvaluationById(evaluationId);
      if (!evaluation) {
        return res.status(404).json({ error: 'Evaluation not found' });
      }
      res.json(evaluation);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch evaluation' });
    }
  });

  app.get('/api/evaluations/:id/progress', async (req, res) => {
    try {
      const evaluationId = parseInt(req.params.id);
      res.json({
        evaluationId,
        totalTests: 10,
        completedTests: 0,
        status: 'pending',
        message: 'Evaluation system temporarily unavailable'
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch evaluation progress' });
    }
  });

  app.get('/api/evaluations/:id/results', async (req, res) => {
    try {
      const evaluationId = parseInt(req.params.id);
      const results = await storage.getEvaluationResultsByEvaluationId(evaluationId);
      res.json(results);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch evaluation results' });
    }
  });

  // Gemini evaluation endpoint with memory integration
  app.post("/api/gemini-evaluate", async (req, res) => {
    const { prompt, temperature = 0.1, maxOutputTokens = 512, userId = "default" } = req.body;

    if (!process.env.GEMINI_API_KEY) {
      return res.status(400).json({ ok: false, error: "Gemini API key not configured" });
    }

    try {
      // Get enhanced context from memory service
      const enhancedPrompt = await memoryService.getEnhancedContext(prompt, userId);

      const result = await model.generateContent({
        contents: [{ role: "user", parts: [{ text: enhancedPrompt }] }],
        generationConfig: { temperature, maxOutputTokens }
      });

      const response = result.response.text();

      // Store threat information if detected
      const threatKeywords = ['threat', 'vulnerability', 'risk', 'exploit', 'attack', 'injection', 'overflow'];
      const containsThreat = threatKeywords.some(keyword => 
        response.toLowerCase().includes(keyword) || prompt.toLowerCase().includes(keyword)
      );

      if (containsThreat) {
        try {
          const severity = response.includes("critical") ? "critical" : 
                          response.includes("high") ? "high" : 
                          response.includes("medium") ? "medium" : "low";

          await memoryService.storeThreat({
            threat_type: "Security Evaluation",
            description: prompt.substring(0, 200) + (prompt.length > 200 ? "..." : ""),
            severity: severity as any,
            context: response.substring(0, 500) + (response.length > 500 ? "..." : ""),
            timestamp: new Date().toISOString(),
            session_id: `eval-${Date.now()}`
          }, userId);
        } catch (memoryError) {
          console.log("Failed to store threat info:", memoryError);
        }
      }

      // Log evaluation context for debugging
      console.log(`Evaluation completed for user ${userId}: ${prompt.substring(0, 100)}...`);

      res.json({ ok: true, result: response });
    } catch (error) {
      console.error('Gemini API error:', error);
      res.status(500).json({ ok: false, error: 'Failed to evaluate with Gemini' });
    }
  });
}