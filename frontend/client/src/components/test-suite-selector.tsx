import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TestTube, Play } from "lucide-react";
import { api, type TestSuite } from "@/lib/api";

interface TestSuiteSelectorProps {
  selectedTestSuites: number[];
  onSelectionChange: (suiteIds: number[]) => void;
  onRunTests: () => void;
}

const severityColors = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-green-100 text-green-700",
};

export default function TestSuiteSelector({ 
  selectedTestSuites, 
  onSelectionChange, 
  onRunTests 
}: TestSuiteSelectorProps) {
  const { data: testSuites } = useQuery<TestSuite[]>({
    queryKey: ['/api/test-suites'],
  });

  const handleSuiteToggle = (suiteId: number, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedTestSuites, suiteId]);
    } else {
      onSelectionChange(selectedTestSuites.filter(id => id !== suiteId));
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TestTube className="h-5 w-5 mr-2 text-primary" />
          Test Suites
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {testSuites?.map((suite) => (
            <div key={suite.id} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Checkbox
                  checked={selectedTestSuites.includes(suite.id)}
                  onCheckedChange={(checked) => handleSuiteToggle(suite.id, !!checked)}
                />
                <div>
                  <p className="text-sm font-medium">{suite.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                  {suite.description && (
                    <p className="text-xs text-gray-500">{suite.description}</p>
                  )}
                </div>
              </div>
              <Badge 
                className={severityColors[suite.severity as keyof typeof severityColors]}
                variant="secondary"
              >
                {suite.severity}
              </Badge>
            </div>
          ))}
        </div>

        <Button 
          onClick={onRunTests} 
          className="w-full" 
          disabled={selectedTestSuites.length === 0}
        >
          <Play className="h-4 w-4 mr-2" />
          Run Selected Tests
        </Button>
      </CardContent>
    </Card>
  );
}
