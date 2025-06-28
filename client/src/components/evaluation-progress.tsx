import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Clock, Server } from "lucide-react";
import type { EvaluationProgress as EvaluationProgressType } from "@/lib/api";

interface EvaluationProgressProps {
  progress: EvaluationProgressType | null;
}

const statusColors = {
  pending: "bg-gray-100 text-gray-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function EvaluationProgress({ progress }: EvaluationProgressProps) {
  const progressPercentage = progress 
    ? (progress.completedTests / progress.totalTests) * 100 
    : 0;

  const estimatedTimeRemaining = progress && progress.status === 'running'
    ? Math.ceil((progress.totalTests - progress.completedTests) * 0.5) // Rough estimate: 30 seconds per test
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-primary" />
          Current Evaluation
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {progress ? (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status</span>
              <Badge 
                className={statusColors[progress.status]}
                variant="secondary"
              >
                {progress.status}
              </Badge>
            </div>

            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{progress.completedTests}/{progress.totalTests}</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>

            {progress.currentTest && (
              <div>
                <span className="text-sm font-medium text-gray-600">Current Test:</span>
                <p className="text-sm">{progress.currentTest}</p>
              </div>
            )}

            <div className="pt-3 border-t border-gray-200 space-y-2">
              {progress.status === 'running' && (
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>Est. completion: {estimatedTimeRemaining} min</span>
                </div>
              )}
              <div className="flex items-center text-sm text-gray-600">
                <Server className="h-4 w-4 mr-2" />
                <span>Evaluation ID: {progress.evaluationId}</span>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <TrendingUp className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No active evaluation</p>
            <p className="text-sm text-gray-400">Start a new evaluation to see progress</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
