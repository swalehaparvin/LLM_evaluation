import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import Header from "@/components/header";
import Sidebar from "@/components/sidebar";
import ModelConfig from "@/components/model-config";
import TestSuiteSelector from "@/components/test-suite-selector";
import EvaluationProgress from "@/components/evaluation-progress";
import VulnerabilityAssessment from "@/components/vulnerability-assessment";
import TestResultsTable from "@/components/test-results-table";
import CustomTestDesigner from "@/components/custom-test-designer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, evaluationWS, type DashboardStats, type EvaluationProgress as EvaluationProgressType } from "@/lib/api";
import { Play, Upload, Bot, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Dashboard() {
  const { toast } = useToast();
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedTestSuites, setSelectedTestSuites] = useState<number[]>([]);
  const [evaluationConfig, setEvaluationConfig] = useState({
    temperature: 0.7,
    maxTokens: 1000,
  });
  const [currentEvaluation, setCurrentEvaluation] = useState<EvaluationProgressType | null>(null);

  // Fetch dashboard stats
  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ['/api/stats'],
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Initialize WebSocket connection
  useEffect(() => {
    evaluationWS.connect();
    
    const handleProgress = (progress: EvaluationProgressType) => {
      setCurrentEvaluation(progress);
    };
    
    evaluationWS.onProgress(handleProgress);
    
    return () => {
      evaluationWS.offProgress(handleProgress);
      evaluationWS.disconnect();
    };
  }, []);

  const handleRunEvaluation = async () => {
    if (!selectedModel || selectedTestSuites.length === 0) {
      toast({
        title: "Missing Configuration",
        description: "Please select a model and at least one test suite.",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await api.runEvaluation({
        modelId: selectedModel,
        testSuiteIds: selectedTestSuites,
        options: evaluationConfig,
      });

      evaluationWS.subscribeToEvaluation(result.evaluationId);
      
      toast({
        title: "Evaluation Started",
        description: `Evaluation ${result.evaluationId} has been started.`,
      });
    } catch (error) {
      toast({
        title: "Evaluation Failed",
        description: "Failed to start evaluation. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex h-screen">
        <Sidebar />
        
        <main className="flex-1 overflow-y-auto">
          {/* Dashboard Header */}
          <div className="bg-white border-b border-gray-200">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Security Evaluation Dashboard</h2>
                  <p className="text-gray-600">Comprehensive LLM cybersecurity risk assessment</p>
                </div>
                <div className="flex space-x-3">
                  <Button onClick={handleRunEvaluation} className="bg-primary hover:bg-primary/90">
                    <Play className="h-4 w-4 mr-2" />
                    New Evaluation
                  </Button>
                  <Button variant="outline">
                    <Upload className="h-4 w-4 mr-2" />
                    Import Tests
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Bot className="h-5 w-5 text-primary" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Active Models</p>
                      <p className="text-2xl font-bold text-gray-900">{stats?.activeModels || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-red-100 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Critical Vulns</p>
                      <p className="text-2xl font-bold text-gray-900">{stats?.criticalVulns || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Tests Passed</p>
                      <p className="text-2xl font-bold text-gray-900">{stats?.testsPassed || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Avg Security Score</p>
                      <p className="text-2xl font-bold text-gray-900">{stats?.avgScore || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Evaluation Interface */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <ModelConfig
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                config={evaluationConfig}
                onConfigChange={setEvaluationConfig}
              />
              
              <TestSuiteSelector
                selectedTestSuites={selectedTestSuites}
                onSelectionChange={setSelectedTestSuites}
                onRunTests={handleRunEvaluation}
              />
              
              <EvaluationProgress progress={currentEvaluation} />
            </div>

            {/* Results Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <VulnerabilityAssessment />
              <TestResultsTable />
            </div>

            {/* Custom Test Section */}
            <CustomTestDesigner />
          </div>
        </main>
      </div>
    </div>
  );
}
