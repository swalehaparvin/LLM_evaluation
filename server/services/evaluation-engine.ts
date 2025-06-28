import type { LlmModel, TestSuite, TestCase, Evaluation, EvaluationResult } from "@shared/schema";
import { createProvider, type LLMProvider, type GenerateOptions } from "./llm-providers";
import { getEvaluatorForTestSuite } from "./test-suites";
import { storage } from "../storage";

export interface EvaluationProgress {
  evaluationId: number;
  totalTests: number;
  completedTests: number;
  currentTest?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export class EvaluationEngine {
  private progressCallbacks: Map<number, (progress: EvaluationProgress) => void> = new Map();

  async runEvaluation(
    modelId: string,
    testSuiteIds: number[],
    options: GenerateOptions = {}
  ): Promise<number> {
    try {
      // Get model information
      const model = await storage.getModelByModelId(modelId);
      if (!model) {
        throw new Error(`Model not found: ${modelId}`);
      }

      // Create evaluation record
      const evaluation = await storage.createEvaluation({
        modelId,
        testSuiteId: testSuiteIds[0], // For simplicity, use first test suite ID
        status: 'pending',
        configuration: { options, testSuiteIds },
      });

      // Start evaluation in background
      this.runEvaluationAsync(evaluation.id, model, testSuiteIds, options);

      return evaluation.id;
    } catch (error) {
      throw new Error(`Failed to start evaluation: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async runEvaluationAsync(
    evaluationId: number,
    model: LlmModel,
    testSuiteIds: number[],
    options: GenerateOptions
  ) {
    try {
      await storage.updateEvaluationStatus(evaluationId, 'running');

      // Get all test cases for the selected test suites
      const allTestCases: TestCase[] = [];
      for (const testSuiteId of testSuiteIds) {
        const testCases = await storage.getTestCasesByTestSuiteId(testSuiteId);
        allTestCases.push(...testCases);
      }

      const totalTests = allTestCases.length;
      let completedTests = 0;

      // Update progress
      this.updateProgress(evaluationId, {
        evaluationId,
        totalTests,
        completedTests,
        status: 'running'
      });

      // Create LLM provider
      const provider = createProvider(model.modelId, model.provider);

      const results: EvaluationResult[] = [];

      // Run tests sequentially
      for (const testCase of allTestCases) {
        try {
          this.updateProgress(evaluationId, {
            evaluationId,
            totalTests,
            completedTests,
            currentTest: testCase.name,
            status: 'running'
          });

          // Generate response from the model
          const response = await provider.generate(
            testCase.prompt,
            testCase.systemPrompt || undefined,
            options
          );

          // Get the appropriate test suite for evaluation
          const testSuite = await storage.getTestSuiteById(testCase.testSuiteId!);
          if (!testSuite) {
            throw new Error(`Test suite not found: ${testCase.testSuiteId}`);
          }

          // Evaluate the response
          const evaluator = getEvaluatorForTestSuite(testSuite.name);
          const evaluationResult = await evaluator.evaluateResponse(
            testCase,
            response.text,
            model.modelId
          );

          // Store the result
          const result = await storage.createEvaluationResult({
            evaluationId,
            testCaseId: testCase.id,
            ...evaluationResult,
          });

          results.push(result);
          completedTests++;

        } catch (error) {
          console.error(`Error evaluating test case ${testCase.id}:`, error);
          // Continue with other tests even if one fails
          completedTests++;
        }
      }

      // Calculate overall score
      const overallScore = results.length > 0
        ? results.reduce((sum, result) => sum + (result.compositeScore || 0), 0) / results.length
        : 0;

      // Update evaluation with completion status
      await storage.updateEvaluationStatus(evaluationId, 'completed');
      await storage.updateEvaluationScore(evaluationId, overallScore);

      // Final progress update
      this.updateProgress(evaluationId, {
        evaluationId,
        totalTests,
        completedTests,
        status: 'completed'
      });

    } catch (error) {
      console.error(`Evaluation ${evaluationId} failed:`, error);
      await storage.updateEvaluationStatus(evaluationId, 'failed');
      
      this.updateProgress(evaluationId, {
        evaluationId,
        totalTests: 0,
        completedTests: 0,
        status: 'failed'
      });
    }
  }

  async runCustomTest(
    modelId: string,
    testSuiteName: string,
    prompt: string,
    systemPrompt?: string,
    evaluationCriteria?: any,
    options: GenerateOptions = {}
  ): Promise<EvaluationResult> {
    try {
      // Get model information
      const model = await storage.getModelByModelId(modelId);
      if (!model) {
        throw new Error(`Model not found: ${modelId}`);
      }

      // Get test suite
      const testSuite = await storage.getTestSuiteByName(testSuiteName);
      if (!testSuite) {
        throw new Error(`Test suite not found: ${testSuiteName}`);
      }

      // Create provider and generate response
      const provider = createProvider(model.modelId, model.provider);
      const response = await provider.generate(prompt, systemPrompt, options);

      // Create temporary test case for evaluation
      const tempTestCase: TestCase = {
        id: 0, // Temporary ID
        testSuiteId: testSuite.id,
        testId: 'custom_test',
        name: 'Custom Test',
        description: 'User-defined custom test',
        prompt,
        systemPrompt: systemPrompt || null,
        evaluationCriteria: evaluationCriteria || {},
        expectedOutcome: 'User-defined outcome',
        createdAt: new Date(),
      };

      // Evaluate the response
      const evaluator = getEvaluatorForTestSuite(testSuite.name);
      const evaluationResult = await evaluator.evaluateResponse(
        tempTestCase,
        response.text,
        model.modelId
      );

      // Return result without storing (since this is a custom test)
      return {
        id: 0,
        evaluationId: 0,
        testCaseId: 0,
        ...evaluationResult,
        createdAt: new Date(),
      };

    } catch (error) {
      throw new Error(`Custom test failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  onProgress(evaluationId: number, callback: (progress: EvaluationProgress) => void) {
    this.progressCallbacks.set(evaluationId, callback);
  }

  offProgress(evaluationId: number) {
    this.progressCallbacks.delete(evaluationId);
  }

  private updateProgress(evaluationId: number, progress: EvaluationProgress) {
    const callback = this.progressCallbacks.get(evaluationId);
    if (callback) {
      callback(progress);
    }
  }

  async getEvaluationProgress(evaluationId: number): Promise<EvaluationProgress | null> {
    const evaluation = await storage.getEvaluationById(evaluationId);
    if (!evaluation) {
      return null;
    }

    const results = await storage.getEvaluationResultsByEvaluationId(evaluationId);
    const configuration = evaluation.configuration as any;
    const testSuiteIds = configuration?.testSuiteIds || [evaluation.testSuiteId];
    
    let totalTests = 0;
    for (const testSuiteId of testSuiteIds) {
      const testCases = await storage.getTestCasesByTestSuiteId(testSuiteId);
      totalTests += testCases.length;
    }

    return {
      evaluationId,
      totalTests,
      completedTests: results.length,
      status: evaluation.status as any,
    };
  }
}

export const evaluationEngine = new EvaluationEngine();
