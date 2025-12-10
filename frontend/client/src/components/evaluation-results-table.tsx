import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertTriangle, CheckCircle, XCircle, Download } from "lucide-react";
import { api } from "@/lib/api";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import PaginationControls from './PaginationControls';

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

interface PaginationData {
  currentPage: number;
  totalPages: number;
  totalCount: number;
  limit: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
}

interface PaginatedResponse {
  results: DetailedEvaluationResult[];
  pagination: PaginationData;
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

interface EvaluationResultsTableProps {
  selectedModel?: string;
}

export default function EvaluationResultsTable({ selectedModel }: EvaluationResultsTableProps) {
  const [pagination, setPagination] = useState<PaginationData>({
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
    limit: 100,
    hasNextPage: false,
    hasPrevPage: false
  });
  const [filters, setFilters] = useState({
    model: selectedModel || 'all',
    testType: 'all',
    status: 'all'
  });

  const fetchResults = async (page = 1, limit = 100) => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters.model && filters.model !== 'all' && { model: filters.model }),
      ...(filters.testType && filters.testType !== 'all' && { testType: filters.testType }),
      ...(filters.status && filters.status !== 'all' && { status: filters.status })
    });

    const response = await fetch(`/api/evaluation-results?${params}`);
    if (!response.ok) {
      throw new Error('Failed to fetch evaluation results');
    }
    return response.json();
  };

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['/api/evaluation-results', pagination.currentPage, pagination.limit, filters],
    queryFn: () => fetchResults(pagination.currentPage, pagination.limit),
  });

  useEffect(() => {
    if (data?.pagination) {
      setPagination(data.pagination);
    }
  }, [data]);

  useEffect(() => {
    setFilters(prev => ({ ...prev, model: selectedModel || 'all' }));
  }, [selectedModel]);

  const handlePageChange = (page: number) => {
    setPagination(prev => ({ ...prev, currentPage: page }));
  };

  const handleLimitChange = (limit: number) => {
    setPagination(prev => ({ ...prev, limit, currentPage: 1 }));
  };

  const results = data?.results || [];

  const exportToPDF = () => {
    if (!results || results.length === 0) return;

    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text('SafeGuardLLM - Security Evaluation Report', 20, 20);
    
    // Add generation date
    doc.setFontSize(12);
    const date = new Date().toLocaleDateString();
    doc.text(`Generated on: ${date}`, 20, 35);

    // Prepare table data with test prompt
    const tableData = results.map(result => {
      // Truncate prompt to first 80 characters for better readability
      const truncatedPrompt = result.prompt.length > 80 
        ? result.prompt.substring(0, 80) + '...' 
        : result.prompt;
      
      return [
        result.testName,
        truncatedPrompt,
        result.modelId,
        result.passed ? 'Pass' : 'Fail',
        (result.vulnerabilityScore * 100).toFixed(1) + '%',
        result.impactSeverity,
        (result.confidenceLevel * 100).toFixed(1) + '%'
      ];
    });

    // Add table with proper spacing
    const tableOptions = {
      startY: 50,
      head: [['Test Name', 'Test Prompt', 'Model', 'Status', 'Vuln Score', 'Impact', 'Confidence']],
      body: tableData,
      theme: 'striped' as any,
      headStyles: { 
        fillColor: [71, 85, 105],
        textColor: [255, 255, 255],
        fontSize: 9,
        fontStyle: 'bold' as any
      },
      styles: { 
        fontSize: 8,
        cellPadding: 3
      },
      columnStyles: {
        0: { cellWidth: 35 }, // Test Name
        1: { cellWidth: 50 }, // Test Prompt (expanded)
        2: { cellWidth: 25 }, // Model
        3: { cellWidth: 15 }, // Status
        4: { cellWidth: 20 }, // Vuln Score
        5: { cellWidth: 20 }, // Impact
        6: { cellWidth: 20 }  // Confidence
      }
    };

    (autoTable as any)(doc, tableOptions);

    // Calculate position after table ends
    const finalY = (doc as any).lastAutoTable?.finalY || 150;
    
    // Add summary with proper spacing
    const passedCount = results.filter(r => r.passed).length;
    const avgVulnScore = (results.reduce((sum, r) => sum + r.vulnerabilityScore, 0) / results.length * 100).toFixed(1);
    
    // Add new page if needed
    if (finalY > 220) {
      doc.addPage();
      doc.setFontSize(16);
      doc.text('Evaluation Summary', 20, 30);
      doc.setFontSize(12);
      doc.text(`Total Tests: ${results.length}`, 20, 50);
      doc.text(`Passed: ${passedCount} (${(passedCount/results.length*100).toFixed(1)}%)`, 20, 65);
      doc.text(`Failed: ${results.length - passedCount} (${((results.length - passedCount)/results.length*100).toFixed(1)}%)`, 20, 80);
      doc.text(`Average Vulnerability Score: ${avgVulnScore}%`, 20, 95);
    } else {
      doc.setFontSize(16);
      doc.text('Evaluation Summary', 20, finalY + 20);
      doc.setFontSize(12);
      doc.text(`Total Tests: ${results.length}`, 20, finalY + 40);
      doc.text(`Passed: ${passedCount} (${(passedCount/results.length*100).toFixed(1)}%)`, 20, finalY + 55);
      doc.text(`Failed: ${results.length - passedCount} (${((results.length - passedCount)/results.length*100).toFixed(1)}%)`, 20, finalY + 70);
      doc.text(`Average Vulnerability Score: ${avgVulnScore}%`, 20, finalY + 85);
    }

    // Save the PDF
    doc.save(`SafeGuardLLM_Report_${date.replace(/\//g, '-')}.pdf`);
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
        <h3 className="text-lg font-semibold">Security Evaluation Results</h3>
        <Button onClick={exportToPDF} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export PDF
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Model:</label>
          <Select
            value={filters.model}
            onValueChange={(value) => setFilters({ ...filters, model: value })}
          >
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Models" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Models</SelectItem>
              <SelectItem value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</SelectItem>
              <SelectItem value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</SelectItem>
              <SelectItem value="gpt-4o">GPT-4o</SelectItem>
              <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Status:</label>
          <Select
            value={filters.status}
            onValueChange={(value) => setFilters({ ...filters, status: value })}
          >
            <SelectTrigger className="w-32">
              <SelectValue placeholder="All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="Pass">Pass</SelectItem>
              <SelectItem value="Fail">Fail</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <ScrollArea className="h-[700px]">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/2">Test & Prompt</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Vulnerability Score</TableHead>
              <TableHead>Confidence</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result) => (
              <TableRow key={result.id}>
                <TableCell className="font-medium">
                  <div>
                    <div className="font-semibold mb-2">{result.testName}</div>
                    <div className="text-sm text-gray-600 whitespace-pre-wrap break-words">
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
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>

      {/* Pagination Controls */}
      <PaginationControls
        currentPage={pagination.currentPage}
        totalPages={pagination.totalPages}
        totalCount={pagination.totalCount}
        onPageChange={handlePageChange}
        onLimitChange={handleLimitChange}
        limit={pagination.limit}
      />
    </div>
  );
}