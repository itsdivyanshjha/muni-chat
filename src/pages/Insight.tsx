import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/layout/Header';
import { InsightCard } from '@/components/results/InsightCard';
import { ChartRenderer } from '@/components/results/ChartRenderer';
import { DataPreviewTable } from '@/components/results/DataPreviewTable';
import { SqlAccordion } from '@/components/results/SqlAccordion';
import { CitationsList } from '@/components/results/CitationsList';
import { useHistory } from '@/stores/history';

export default function Insight() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { items } = useHistory();

  const insight = items.find(item => item.id === id);

  if (!insight?.response) {
    return (
      <div className="min-h-screen bg-gradient-subtle">
        <Header />
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center gap-4 mb-6">
            <Button variant="ghost" onClick={() => navigate('/')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </div>
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold mb-2">Insight not found</h2>
            <p className="text-muted-foreground">The requested insight could not be found.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Header />
      
      <div className="container mx-auto px-6 py-6">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Saved Insight</h1>
            <p className="text-sm text-muted-foreground">
              "{insight.prompt}" • {insight.createdAt.toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="max-w-4xl space-y-6">
          <InsightCard insight={insight.response} />
          <ChartRenderer 
            spec={insight.response.viz} 
            dataPreview={insight.response.data_preview} 
          />
          <DataPreviewTable dataPreview={insight.response.data_preview} />
          <SqlAccordion sql={insight.response.sql_used} />
          <CitationsList citations={insight.response.doc_citations} />
        </div>
      </div>
    </div>
  );
}