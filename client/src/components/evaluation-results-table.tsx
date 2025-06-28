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
import { AlertTriangle, CheckCircle, XCircle, Download } from "lucide-react";
import { api } from "@/lib/api";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// Extended result type with joined data
interface DetailedEvaluationResult {
  id: number;
  passed: boolean;
  vulnerabilityScore: number;
  attackComplexity: string;
  detectionDifficulty: string;
  impactSeverity: string;
  remediationComplexity: string;
  confidenceLevel: number;
  compositeScore: number;
  modelResponse: string;
  createdAt: string;
  modelId: string;
  testName: string;
  prompt: string;
  testDescription: string;
}

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
    case 'medium': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    case 'low': return <CheckCircle className="h-4 w-4 text-blue-500" />;
    default: return <XCircle className="h-4 w-4 text-gray-500" />;
  }
};

export default function EvaluationResultsTable() {
  const { data: results, isLoading } = useQuery<DetailedEvaluationResult[]>({
    queryKey: ['/api/evaluation-results'],
  });

  const exportToPDF = () => {
    if (!results || results.length === 0) return;

    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text('CyberSecEval Enhanced - Evaluation Results', 20, 20);
    
    // Add generation date
    doc.setFontSize(12);
    const date = new Date().toLocaleDateString();
    doc.text(`Generated on: ${date}`, 20, 35);

    // Prepare table data
    const tableData = results.map(result => [
      result.testName,
      result.modelId,
      result.passed ? 'Pass' : 'Fail',
      (result.vulnerabilityScore * 100).toFixed(1) + '%',
      result.impactSeverity,
      result.attackComplexity,
      (result.confidenceLevel * 100).toFixed(1) + '%',
      new Date(result.createdAt).toLocaleDateString()
    ]);

    // Add table
    autoTable(doc, {
      startY: 50,
      head: [['Test Name', 'Model', 'Status', 'Vuln Score', 'Impact', 'Complexity', 'Confidence', 'Date']],
      body: tableData,
      theme: 'striped',
      headStyles: { fillColor: [71, 85, 105] },
      styles: { fontSize: 8 },
      columnStyles: {
        0: { cellWidth: 35 },
        1: { cellWidth: 25 },
        2: { cellWidth: 15 },
        3: { cellWidth: 20 },
        4: { cellWidth: 20 },
        5: { cellWidth: 20 },
        6: { cellWidth: 20 },
        7: { cellWidth: 20 }
      }
    });

    // Add summary
    const passedCount = results.filter(r => r.passed).length;
    const avgVulnScore = (results.reduce((sum, r) => sum + r.vulnerabilityScore, 0) / results.length * 100).toFixed(1);
    
    doc.setFontSize(14);
    doc.text('Summary:', 20, 200);
    doc.setFontSize(12);
    doc.text(`Total Tests: ${results.length}`, 20, 220);
    doc.text(`Passed: ${passedCount} (${(passedCount/results.length*100).toFixed(1)}%)`, 20, 235);
    doc.text(`Failed: ${results.length - passedCount} (${((results.length - passedCount)/results.length*100).toFixed(1)}%)`, 20, 250);
    doc.text(`Average Vulnerability Score: ${avgVulnScore}%`, 20, 265);

    // Save the PDF
    doc.save(`CyberSecEval_Results_${date.replace(/\//g, '-')}.pdf`);
  };

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
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Recent Evaluation Results</h3>
        <Button onClick={exportToPDF} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export PDF
        </Button>
      </div>
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
              <TableHead>Date</TableHead>
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
                  <Badge variant="outline" className="text-xs">
                    {result.modelId}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {getSeverityIcon(result.impactSeverity, result.passed)}
                    <span className={result.passed ? "text-green-600" : "text-red-600"}>
                      {result.passed ? "Pass" : "Fail"}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={getSeverityColor(result.impactSeverity)} className="text-xs">
                    {result.impactSeverity}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          result.vulnerabilityScore > 0.7 ? 'bg-red-500' :
                          result.vulnerabilityScore > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${result.vulnerabilityScore * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-mono">
                      {(result.vulnerabilityScore * 100).toFixed(1)}%
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm font-mono">
                    {(result.confidenceLevel * 100).toFixed(1)}%
                  </span>
                </TableCell>
                <TableCell className="text-sm text-gray-500">
                  {new Date(result.createdAt).toLocaleDateString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>
    </div>
  );
}