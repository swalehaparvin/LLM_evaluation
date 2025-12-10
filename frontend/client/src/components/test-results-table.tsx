import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FileText } from "lucide-react";
import { api, type EvaluationResult } from "@/lib/api";

const statusColors = {
  true: "bg-green-100 text-green-800",
  false: "bg-red-100 text-red-800",
};

export default function TestResultsTable() {
  const { data: recentResults, isLoading } = useQuery<EvaluationResult[]>({
    queryKey: ['/api/recent-results', { limit: 10 }],
    refetchInterval: 10000,
  });

  const getTestName = (result: EvaluationResult) => {
    const metadata = result.metadata as any;
    return metadata?.test_subtype?.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) || 'Unknown Test';
  };

  const getTestId = (result: EvaluationResult) => {
    const metadata = result.metadata as any;
    return metadata?.test_type || `test_${result.id}`;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2 text-primary" />
            Recent Test Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500">Loading test results...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <FileText className="h-5 w-5 mr-2 text-primary" />
          Recent Test Results
        </CardTitle>
      </CardHeader>
      <CardContent>
        {recentResults && recentResults.length > 0 ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Test</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentResults.map((result) => (
                  <TableRow key={result.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{getTestName(result)}</div>
                        <div className="text-sm text-gray-500">{getTestId(result)}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        className={statusColors[result.passed.toString() as keyof typeof statusColors]}
                        variant="secondary"
                      >
                        {result.passed ? 'Passed' : 'Failed'}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      {Math.round(result.vulnerabilityScore)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No test results available</p>
            <p className="text-sm text-gray-400">Run evaluations to see test results</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
