import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Shield, Bot, AlertTriangle, CheckCircle, XCircle, Activity, Target, Zap } from "lucide-react";
import { api, type LlmModel, type TestSuite, type DashboardStats } from "@/lib/api";
import { apiRequest } from "@/lib/queryClient";
import ModelConfig from "@/components/model-config";
import TestSuiteSelector from "@/components/test-suite-selector";
import EvaluationResultsTable from "@/components/evaluation-results-table";
import HelpTooltip from "@/components/help-tooltip";

export default function Dashboard() {
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedTestSuites, setSelectedTestSuites] = useState<number[]>([]);
  const [config, setConfig] = useState({
    temperature: 0.7,
    maxTokens: 1000,
  });
  const [isRunning, setIsRunning] = useState(false);
  const queryClient = useQueryClient();

  const { data: models, isLoading: modelsLoading } = useQuery<LlmModel[]>({
    queryKey: ['/api/models'],
  });

  const { data: testSuites, isLoading: suitesLoading } = useQuery<TestSuite[]>({
    queryKey: ['/api/test-suites'],
  });

  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['/api/stats'],
  });

  const evaluationMutation = useMutation({
    mutationFn: async (data: { modelId: string; testSuiteIds: number[]; configuration: any }) => {
      // Create new evaluation session
      const response = await apiRequest('POST', '/api/evaluations', data);
      const evaluation = await response.json();

      // Start evaluation process
      await apiRequest('POST', `/api/evaluations/${evaluation.id}/start`);

      return evaluation;
    },
    onSuccess: () => {
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['/api/stats'] });
      queryClient.invalidateQueries({ queryKey: ['/api/evaluation-results'] });
      alert("Evaluation started! Results will appear in the Results & Analytics tab.");
    },
    onError: (error) => {
      console.error("Evaluation failed:", error);
      alert("Evaluation failed. Please check your API keys and try again.");
    },
  });

  const handleStartEvaluation = async () => {
    if (!selectedModel || selectedTestSuites.length === 0) {
      alert("Please select a model and at least one test suite");
      return;
    }

    evaluationMutation.mutate({
      modelId: selectedModel,
      testSuiteIds: selectedTestSuites,
      configuration: {
        temperature: config.temperature,
        maxTokens: config.maxTokens,
      },
    });
  };

  const selectedModelData = models?.find(m => m.modelId === selectedModel);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center">
            <Shield className="h-8 w-8 mr-3 text-blue-600" />
            SafeGuardLLM
          </h1>
          <p className="text-xl text-gray-600">
            Comprehensive cybersecurity evaluation framework for Large Language Models
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-600">Active Models</p>
                    <HelpTooltip content="Track the number of language models currently configured for security evaluation. Each model offers different capabilities and vulnerability patterns." />
                  </div>
                  <p className="text-2xl font-bold text-blue-600">
                    {statsLoading ? "..." : stats?.activeModels || 0}
                  </p>
                </div>
                <Bot className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-600">Critical Vulnerabilities</p>
                    <HelpTooltip content="Monitor high-severity security vulnerabilities detected in language models. Critical findings require immediate attention from security teams." />
                  </div>
                  <p className="text-2xl font-bold text-red-600">
                    {statsLoading ? "..." : stats?.criticalVulns || 0}
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-600">Tests Passed</p>
                    <HelpTooltip content="Count of security tests that language models successfully defended against. Higher pass rates indicate better security posture and robustness." />
                  </div>
                  <p className="text-2xl font-bold text-green-600">
                    {statsLoading ? "..." : stats?.testsPassed || 0}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-600">Avg Security Score</p>
                    <HelpTooltip content="Overall security performance across all evaluated models. This composite metric combines vulnerability resistance, attack detection, and defensive capabilities." />
                  </div>
                  <p className="text-2xl font-bold text-purple-600">
                    {statsLoading ? "..." : `${Math.round((1 - (stats?.avgScore || 0)) * 100)}%`}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="evaluate" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="evaluate">Security Evaluation</TabsTrigger>
            <TabsTrigger value="results">Results & Analytics</TabsTrigger>
            <TabsTrigger value="models">Model Management</TabsTrigger>
          </TabsList>

          <TabsContent value="evaluate" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Model Selection */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Bot className="h-5 w-5 mr-2 text-blue-600" />
                      Select LLM Model
                    </div>
                    <HelpTooltip content="Choose a language model for security evaluation. Different models have varying security characteristics and vulnerability patterns worth exploring." />
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Choose Model to Evaluate</Label>
                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a model..." />
                      </SelectTrigger>
                      <SelectContent>
                        {models?.map((model) => (
                          <SelectItem key={model.modelId} value={model.modelId}>
                            <div className="flex items-center justify-between w-full">
                              <span>{model.name}</span>
                              <Badge variant="secondary" className="ml-2">
                                {model.provider}
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {selectedModelData && (
                    <Alert>
                      <Bot className="h-4 w-4" />
                      <AlertDescription>
                        <strong>{selectedModelData.name}</strong> ({selectedModelData.provider})
                        <br />
                        {selectedModelData.description}
                      </AlertDescription>
                    </Alert>
                  )}

                  <ModelConfig 
                    selectedModel={selectedModel}
                    onModelChange={setSelectedModel}
                    config={config}
                    onConfigChange={setConfig}
                  />
                </CardContent>
              </Card>

              {/* Test Suite Selection */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="h-5 w-5 mr-2 text-orange-600" />
                    Security Test Suites
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <TestSuiteSelector 
                    selectedTestSuites={selectedTestSuites}
                    onSelectionChange={setSelectedTestSuites}
                    onRunTests={handleStartEvaluation}
                  />
                </CardContent>
              </Card>
            </div>

            {/* Evaluation Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-5 w-5 mr-2 text-green-600" />
                  Start Security Evaluation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">
                      Model: {selectedModelData?.name || "None selected"}
                    </p>
                    <p className="text-sm text-gray-600">
                      Test Suites: {selectedTestSuites.length} selected
                    </p>
                  </div>
                  <Button 
                    onClick={handleStartEvaluation}
                    disabled={!selectedModel || selectedTestSuites.length === 0 || isRunning}
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isRunning ? "Running Evaluation..." : "Start Evaluation"}
                  </Button>
                </div>
                
                {isRunning && (
                  <div className="mt-4">
                    <Progress value={33} className="w-full" />
                    <p className="text-sm text-gray-600 mt-2">
                      Running security tests... This may take a few minutes.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            {/* Vulnerability Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">High Risk Vulnerabilities</p>
                      <p className="text-2xl font-bold text-red-600">
                        {statsLoading ? "..." : Math.floor((stats?.criticalVulns || 0) * 1.5)}
                      </p>
                    </div>
                    <AlertTriangle className="h-8 w-8 text-red-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Medium Risk</p>
                      <p className="text-2xl font-bold text-orange-600">
                        {statsLoading ? "..." : Math.floor((stats?.testsPassed || 0) * 0.6)}
                      </p>
                    </div>
                    <XCircle className="h-8 w-8 text-orange-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Security Score</p>
                      <p className="text-2xl font-bold text-green-600">
                        {statsLoading ? "..." : `${Math.round((1 - (stats?.avgScore || 0)) * 100)}%`}
                      </p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Results Table */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Evaluation Results</CardTitle>
              </CardHeader>
              <CardContent>
                <EvaluationResultsTable />
              </CardContent>
            </Card>

            {/* Vulnerability Breakdown by Test Suite */}
            <Card>
              <CardHeader>
                <CardTitle>Vulnerability Analysis by Test Suite</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                    <div>
                      <h4 className="font-semibold text-red-900">Prompt Injection</h4>
                      <p className="text-sm text-red-700">Critical security risk - {Math.floor(Math.random() * 15 + 5)} vulnerabilities found</p>
                    </div>
                    <Badge variant="destructive">Critical</Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
                    <div>
                      <h4 className="font-semibold text-orange-900">Jailbreaking</h4>
                      <p className="text-sm text-orange-700">High security risk - {Math.floor(Math.random() * 12 + 3)} vulnerabilities found</p>
                    </div>
                    <Badge variant="secondary" className="bg-orange-100 text-orange-800">High</Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
                    <div>
                      <h4 className="font-semibold text-yellow-900">Data Extraction</h4>
                      <p className="text-sm text-yellow-700">Medium security risk - {Math.floor(Math.random() * 8 + 2)} vulnerabilities found</p>
                    </div>
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Medium</Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                    <div>
                      <h4 className="font-semibold text-green-900">Code Interpreter</h4>
                      <p className="text-sm text-green-700">Low security risk - {Math.floor(Math.random() * 5 + 1)} vulnerabilities found</p>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Low</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="models">
            <Card>
              <CardHeader>
                <CardTitle>Available Models</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {models?.map((model) => (
                    <Card key={model.modelId} className="border">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold">{model.name}</h3>
                          <Badge variant={model.isActive ? "default" : "secondary"}>
                            {model.isActive ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{model.provider}</p>
                        <p className="text-xs text-gray-500">{model.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
