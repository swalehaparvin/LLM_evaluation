import { pgTable, text, serial, integer, boolean, timestamp, jsonb, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const llmModels = pgTable("llm_models", {
  id: serial("id").primaryKey(),
  modelId: text("model_id").notNull().unique(),
  provider: text("provider").notNull(), // 'openai', 'anthropic', 'google'
  name: text("name").notNull(),
  description: text("description"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const testSuites = pgTable("test_suites", {
  id: serial("id").primaryKey(),
  name: text("name").notNull().unique(),
  description: text("description"),
  category: text("category").notNull(),
  severity: text("severity").notNull(), // 'low', 'medium', 'high', 'critical'
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const testCases = pgTable("test_cases", {
  id: serial("id").primaryKey(),
  testSuiteId: integer("test_suite_id").references(() => testSuites.id),
  testId: text("test_id").notNull().unique(),
  name: text("name").notNull(),
  description: text("description"),
  prompt: text("prompt").notNull(),
  systemPrompt: text("system_prompt"),
  evaluationCriteria: jsonb("evaluation_criteria"),
  expectedOutcome: text("expected_outcome"),
  // New fields for comprehensive datasets
  userInput: text("user_input"),
  judgeQuestion: text("judge_question"),
  injectionType: text("injection_type"),
  injectionVariant: text("injection_variant"),
  riskCategory: text("risk_category"),
  speakingLanguage: text("speaking_language").default("English"),
  mitreCategory: text("mitre_category"),
  ttpId: text("ttp_id"),
  ttpName: text("ttp_name"),
  basePrompt: text("base_prompt"),
  mutatedPrompt: text("mutated_prompt"),
  // Memory corruption specific fields
  challengeType: text("challenge_type"), // 'buffer_overflow', 'memory_corruption', 'constraint_satisfaction'
  language: text("language"), // 'c', 'javascript', 'python', 'sqlite'
  code: text("code"), // The vulnerable code to analyze
  expectedAnswer: text("expected_answer"), // Expected byte sequence or solution
  difficultyLevel: text("difficulty_level"), // 'basic', 'intermediate', 'advanced'
  exploitType: text("exploit_type"), // 'stack_overflow', 'heap_overflow', 'format_string', etc.
  createdAt: timestamp("created_at").defaultNow(),
});

export const evaluations = pgTable("evaluations", {
  id: serial("id").primaryKey(),
  modelId: text("model_id").notNull(),
  testSuiteId: integer("test_suite_id").references(() => testSuites.id),
  status: text("status").notNull(), // 'pending', 'running', 'completed', 'failed'
  overallScore: real("overall_score"),
  startedAt: timestamp("started_at").defaultNow(),
  completedAt: timestamp("completed_at"),
  configuration: jsonb("configuration"),
});

export const evaluationResults = pgTable("evaluation_results", {
  id: serial("id").primaryKey(),
  evaluationId: integer("evaluation_id").references(() => evaluations.id),
  testCaseId: integer("test_case_id").references(() => testCases.id),
  modelResponse: text("model_response"),
  passed: boolean("passed"),
  vulnerabilityScore: real("vulnerability_score"),
  attackComplexity: text("attack_complexity"),
  detectionDifficulty: text("detection_difficulty"),
  impactSeverity: text("impact_severity"),
  remediationComplexity: text("remediation_complexity"),
  confidenceLevel: real("confidence_level"),
  compositeScore: real("composite_score"),
  metadata: jsonb("metadata"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Insert schemas
export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertLlmModelSchema = createInsertSchema(llmModels).omit({
  id: true,
  createdAt: true,
});

export const insertTestSuiteSchema = createInsertSchema(testSuites).omit({
  id: true,
  createdAt: true,
});

export const insertTestCaseSchema = createInsertSchema(testCases).omit({
  id: true,
  createdAt: true,
});

export const insertEvaluationSchema = createInsertSchema(evaluations).omit({
  id: true,
  startedAt: true,
  completedAt: true,
});

export const insertEvaluationResultSchema = createInsertSchema(evaluationResults).omit({
  id: true,
  createdAt: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;

export type LlmModel = typeof llmModels.$inferSelect;
export type InsertLlmModel = z.infer<typeof insertLlmModelSchema>;

export type TestSuite = typeof testSuites.$inferSelect;
export type InsertTestSuite = z.infer<typeof insertTestSuiteSchema>;

export type TestCase = typeof testCases.$inferSelect;
export type InsertTestCase = z.infer<typeof insertTestCaseSchema>;

export type Evaluation = typeof evaluations.$inferSelect;
export type InsertEvaluation = z.infer<typeof insertEvaluationSchema>;

export type EvaluationResult = typeof evaluationResults.$inferSelect;
export type InsertEvaluationResult = z.infer<typeof insertEvaluationResultSchema>;
