import Header from "@/components/header";
import EvaluationResultsTable from "@/components/evaluation-results-table";

export default function Results() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Evaluation Results
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Comprehensive security evaluation results and analytics
          </p>
        </div>
        
        <EvaluationResultsTable />
      </main>
    </div>
  );
}