import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { ChatInput } from '@/components/chat/ChatInput';
import { HistoryList } from '@/components/chat/HistoryList';
import { FilterBar } from '@/components/filters/FilterBar';
import { InsightCard } from '@/components/results/InsightCard';
import { ChartRenderer } from '@/components/results/ChartRenderer';
import { DataPreviewTable } from '@/components/results/DataPreviewTable';
import { SqlAccordion } from '@/components/results/SqlAccordion';
import { CitationsList } from '@/components/results/CitationsList';
import { api } from '@/lib/api';
import { useFilters } from '@/stores/filters';
import { useHistory } from '@/stores/history';
import { HistoryItem, InsightResponse } from '@/lib/types';
import { toast } from '@/hooks/use-toast';

export default function Home() {
  const { filters } = useFilters();
  const { items, currentItem, addItem, setCurrentItem } = useHistory();
  const [currentResponse, setCurrentResponse] = useState<InsightResponse | null>(null);

  const insightMutation = useMutation({
    mutationFn: api.getInsight,
    onSuccess: (response, variables) => {
      const historyItem: HistoryItem = {
        id: crypto.randomUUID(),
        prompt: variables.prompt,
        filters: variables.filters,
        createdAt: new Date(),
        response
      };
      
      addItem(historyItem);
      setCurrentResponse(response);
      
      toast({
        title: "Insight generated",
        description: "Your municipal data analysis is ready"
      });
    },
    onError: (error) => {
      toast({
        title: "Analysis failed",
        description: error.message || "Unable to generate insight",
        variant: "destructive"
      });
    }
  });

  const handleSendMessage = (prompt: string) => {
    insightMutation.mutate({ prompt, filters });
  };

  const handleHistoryItemClick = (item: HistoryItem) => {
    setCurrentItem(item);
    setCurrentResponse(item.response || null);
  };

  const displayResponse = currentResponse || currentItem?.response;
  const isLoading = insightMutation.isPending;

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Header />
      
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
          {/* Left Column - Chat */}
          <div className="lg:col-span-4 flex flex-col">
            <div className="bg-background rounded-xl shadow-card border h-full flex flex-col">
              {/* Chat Input */}
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold mb-4">Ask a Question</h2>
                <ChatInput 
                  onSend={handleSendMessage}
                  isLoading={isLoading}
                  placeholder="What would you like to know about municipal data?"
                />
              </div>
              
              {/* History */}
              <div className="flex-1 overflow-hidden">
                <div className="p-4 border-b">
                  <h3 className="font-medium text-sm text-muted-foreground">Recent Conversations</h3>
                </div>
                <HistoryList 
                  items={items}
                  onItemClick={handleHistoryItemClick}
                  currentItemId={currentItem?.id}
                />
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-8 flex flex-col">
            <FilterBar />
            
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="flex items-center gap-3">
                    <Loader2 className="h-6 w-6 animate-spin" />
                    <span className="text-lg">Analyzing municipal data...</span>
                  </div>
                </div>
              ) : displayResponse ? (
                <div className="space-y-6 pb-6">
                  <InsightCard insight={displayResponse} />
                  <ChartRenderer 
                    spec={displayResponse.viz} 
                    dataPreview={displayResponse.data_preview} 
                  />
                  <DataPreviewTable dataPreview={displayResponse.data_preview} />
                  <SqlAccordion sql={displayResponse.sql_used} />
                  <CitationsList citations={displayResponse.doc_citations} />
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <div className="max-w-md">
                    <h3 className="text-xl font-semibold mb-2">Welcome to Municipal AI Insights</h3>
                    <p className="text-muted-foreground mb-4">
                      Start by asking a question about municipal data or adjust the filters to explore specific areas and time periods.
                    </p>
                    <div className="text-sm text-muted-foreground">
                      <p>💡 Try asking about:</p>
                      <ul className="mt-2 space-y-1">
                        <li>• "Show me transportation data for last month"</li>
                        <li>• "What are the trends in public safety?"</li>
                        <li>• "Compare utility usage across wards"</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}