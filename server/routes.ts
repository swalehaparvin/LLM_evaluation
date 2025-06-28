import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer } from "ws";
import { storage } from "./storage";
import { evaluationEngine } from "./services/evaluation-engine";
import { insertEvaluationSchema } from "@shared/schema";
import { z } from "zod";

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

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);
  const wss = new WebSocketServer({ server: httpServer });

  // WebSocket connection for real-time updates
  wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        if (data.type === 'subscribe_evaluation' && data.evaluationId) {
          evaluationEngine.onProgress(data.evaluationId, (progress) => {
            ws.send(JSON.stringify({
              type: 'evaluation_progress',
              data: progress
            }));
          });
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    });

    ws.on('close', () => {
      console.log('WebSocket client disconnected');
    });
  });

  // Models endpoints
  app.get('/api/models', async (req, res) => {
    try {
      const models = await storage.getAllModels();
      res.json(models);
    } catch (error) {
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
      res.status(500).json({ error: 'Failed to fetch model' });
    }
  });

  // Test suites endpoints
  app.get('/api/test-suites', async (req, res) => {
    try {
      const testSuites = await storage.getAllTestSuites();
      res.json(testSuites);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch test suites' });
    }
  });

  app.get('/api/test-suites/:id/test-cases', async (req, res) => {
    try {
      const testSuiteId = parseInt(req.params.id);
      const testCases = await storage.getTestCasesByTestSuiteId(testSuiteId);
      res.json(testCases);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch test cases' });
    }
  });

  // Evaluations endpoints
  app.post('/api/evaluations', async (req, res) => {
    try {
      const data = runEvaluationSchema.parse(req.body);
      const evaluationId = await evaluationEngine.runEvaluation(
        data.modelId,
        data.testSuiteIds,
        data.options
      );
      res.json({ evaluationId });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: 'Invalid request data', details: error.errors });
      }
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
      const progress = await evaluationEngine.getEvaluationProgress(evaluationId);
      if (!progress) {
        return res.status(404).json({ error: 'Evaluation not found' });
      }
      res.json(progress);
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

  // Custom test endpoint
  app.post('/api/custom-test', async (req, res) => {
    try {
      const data = runCustomTestSchema.parse(req.body);
      const result = await evaluationEngine.runCustomTest(
        data.modelId,
        data.testSuiteName,
        data.prompt,
        data.systemPrompt,
        data.evaluationCriteria,
        data.options
      );
      res.json(result);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: 'Invalid request data', details: error.errors });
      }
      res.status(500).json({ error: 'Failed to run custom test' });
    }
  });

  // Recent results endpoint
  app.get('/api/recent-results', async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;
      const results = await storage.getRecentEvaluationResults(limit);
      res.json(results);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch recent results' });
    }
  });

  // Dashboard stats endpoint
  app.get('/api/stats', async (req, res) => {
    try {
      const models = await storage.getAllModels();
      const recentResults = await storage.getRecentEvaluationResults(100);
      
      const criticalVulns = recentResults.filter(r => 
        r.impactSeverity === 'critical' && !r.passed
      ).length;
      
      const testsPassed = recentResults.filter(r => r.passed).length;
      
      const avgScore = recentResults.length > 0
        ? recentResults.reduce((sum, r) => sum + (r.compositeScore || 0), 0) / recentResults.length
        : 0;

      res.json({
        activeModels: models.length,
        criticalVulns,
        testsPassed,
        avgScore: Math.round(avgScore * 10) / 10,
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch stats' });
    }
  });

  return httpServer;
}
