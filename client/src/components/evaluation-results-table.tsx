import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ExternalLink, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { api, type EvaluationResult } from "@/lib/api";

const getSeverityColor = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'critical': return 'destructive';
    case 'high': return 'secondary';
    case 'medium': return 'outline';
    case 'low': return 'default';
    default: return 'outline';
  }
};

const getSeverityIcon = (severity: string, passed: boolean) => {
  if (passed) return <CheckCircle className="h-4 w-4 text-green-500" />;
  
  switch (severity?.toLowerCase()) {
    case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />;
    case 'high': return <XCircle className="h-4 w-4 text-orange-500" />;
    case 'medium': return <XCircle className="h-4 w-4 text-yellow-500" />;
    default: return <XCircle className="h-4 w-4 text-gray-500" />;
  }
};

export default function EvaluationResultsTable() {
  const { data: results, isLoading } = useQuery<EvaluationResult[]>({
    queryKey: ['/api/evaluation-results'],
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading evaluation results...</div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">No evaluation results found</div>
      </div>
    );
  }

  return (
    <ScrollArea className="h-96">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Test Case</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Vulnerability Score</TableHead>
            <TableHead>Confidence</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {results.map((result) => (
            <TableRow key={result.id}>
              <TableCell className="font-medium">
                <div>
                  <div className="font-semibold">{result.testName}</div>
                  <div className="text-sm text-gray-500 truncate max-w-48">
                    {result.prompt}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div className="text-sm">
                  <div>{result.modelId}</div>
                  <div className="text-gray-500">{result.category}</div>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {getSeverityIcon(result.impactSeverity, result.passed)}
                  <span className={result.passed ? "text-green-600" : "text-red-600"}>
                    {result.passed ? "Passed" : "Failed"}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant={getSeverityColor(result.impactSeverity)}>
                  {result.impactSeverity}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className={`w-16 h-2 rounded-full bg-gray-200`}>
                    <div 
                      className={`h-full rounded-full ${
                        result.vulnerabilityScore > 0.7 ? 'bg-red-500' :
                        result.vulnerabilityScore > 0.4 ? 'bg-orange-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${result.vulnerabilityScore * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {Math.round(result.vulnerabilityScore * 100)}%
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">
                  {Math.round(result.confidenceLevel * 100)}%
                </span>
              </TableCell>
              <TableCell>
                <Button variant="ghost" size="sm">
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </ScrollArea>
  );
}