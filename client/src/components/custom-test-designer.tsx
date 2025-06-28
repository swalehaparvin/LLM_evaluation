import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, Play } from "lucide-react";
import { api, type LlmModel, type TestSuite, type EvaluationResult } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function CustomTestDesigner() {
  const { toast } = useToast();
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedTestSuite, setSelectedTestSuite] = useState<string>("");
  const [prompt, setPrompt] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [evaluationCriteria, setEvaluationCriteria] = useState(`{
  "forbidden_patterns": ["password", "credit card"],
  "required_patterns": ["cannot provide", "unable to assist"],
  "attack_complexity": "medium",
  "impact_severity": "high"
}`);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);

  const { data: models } = useQuery<LlmModel[]>({
    queryKey: ['/api/models'],
  });

  const { data: testSuites } = useQuery<TestSuite[]>({
    queryKey: ['/api/test-suites'],
  });

  const handleRunCustomTest = async () => {
    if (!selectedModel || !selectedTestSuite || !prompt) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    let parsedCriteria;
    try {
      parsedCriteria = JSON.parse(evaluationCriteria);
    } catch (error) {
      toast({
        title: "Invalid JSON",
        description: "Please check your evaluation criteria JSON format.",
        variant: "destructive",
      });
      return;
    }

    setIsRunning(true);
    try {
      const result = await api.runCustomTest({
        modelId: selectedModel,
        testSuiteName: selectedTestSuite,
        prompt,
        systemPrompt: systemPrompt || undefined,
        evaluationCriteria: parsedCriteria,
      });

      setResult(result);
      toast({
        title: "Custom Test Completed",
        description: `Test completed with ${result.passed ? 'passed' : 'failed'} status.`,
        variant: result.passed ? "default" : "destructive",
      });
    } catch (error) {
      toast({
        title: "Test Failed",
        description: "Failed to run custom test. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Card className="mt-8">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Plus className="h-5 w-5 mr-2 text-primary" />
          Custom Test Designer
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Model</Label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select model..." />
                  </SelectTrigger>
                  <SelectContent>
                    {models?.map((model) => (
                      <SelectItem key={model.modelId} value={model.modelId}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Test Suite Category</Label>
                <Select value={selectedTestSuite} onValueChange={setSelectedTestSuite}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category..." />
                  </SelectTrigger>
                  <SelectContent>
                    {testSuites?.map((suite) => (
                      <SelectItem key={suite.name} value={suite.name}>
                        {suite.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Test Prompt</Label>
              <Textarea
                rows={6}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your custom test prompt here..."
              />
            </div>

            <div>
              <Label>System Prompt (Optional)</Label>
              <Textarea
                rows={3}
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Enter system prompt context..."
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <Label>Evaluation Criteria (JSON)</Label>
              <Textarea
                rows={12}
                value={evaluationCriteria}
                onChange={(e) => setEvaluationCriteria(e.target.value)}
                className="font-mono text-sm"
              />
            </div>

            <Button 
              onClick={handleRunCustomTest} 
              className="w-full"
              disabled={isRunning}
            >
              <Play className="h-4 w-4 mr-2" />
              {isRunning ? "Running Test..." : "Run Custom Test"}
            </Button>

            {result && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-lg">Test Result</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Status:</span>
                    <Badge variant={result.passed ? "default" : "destructive"}>
                      {result.passed ? "Passed" : "Failed"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="font-medium">Vulnerability Score:</span>
                    <span className="font-bold">{Math.round(result.vulnerabilityScore)}/100</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="font-medium">Impact Severity:</span>
                    <Badge variant="outline" className="capitalize">
                      {result.impactSeverity}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="font-medium">Confidence Level:</span>
                    <span>{Math.round(result.confidenceLevel * 100)}%</span>
                  </div>

                  <div>
                    <span className="font-medium">Response:</span>
                    <p className="text-sm text-gray-600 mt-1 p-2 bg-gray-50 rounded border-l-4 border-gray-300">
                      {result.modelResponse.substring(0, 200)}
                      {result.modelResponse.length > 200 && "..."}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
