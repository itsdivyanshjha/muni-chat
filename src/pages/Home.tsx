import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, Database, MessageSquare } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { ChatInput } from '@/components/chat/ChatInput';
import { HistoryList } from '@/components/chat/HistoryList';
import { FilterBar } from '@/components/filters/FilterBar';
import { InsightCard } from '@/components/results/InsightCard';
import { ChartRenderer } from '@/components/results/ChartRenderer';
import { DataPreviewTable } from '@/components/results/DataPreviewTable';
import { SqlAccordion } from '@/components/results/SqlAccordion';
import { CitationsList } from '@/components/results/CitationsList';
import { GovernmentDatasets } from '@/components/datasets/GovernmentDatasets';
import { api } from '@/lib/api';
import { useFilters } from '@/stores/filters';
import { useHistory } from '@/stores/history';
import { HistoryItem, InsightResponse } from '@/lib/types';
import { toast } from '@/hooks/use-toast';

export default function Home() {
  const { filters } = useFilters();
  const { items, currentItem, addItem, setCurrentItem } = useHistory();
  const [currentResponse, setCurrentResponse] = useState<InsightResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'datasets'>('chat');

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
        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-background rounded-lg p-1 shadow-sm border">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activeTab === 'chat'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            Chat & Analysis
          </button>
          <button
            onClick={() => setActiveTab('datasets')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activeTab === 'datasets'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Database className="h-4 w-4" />
            Government Datasets
          </button>
        </div>

        {activeTab === 'chat' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-12rem)]">
            {/* Left Column - Chat */}
            <div className="lg:col-span-4 flex flex-col">
              <div className="bg-background rounded-xl shadow-card border h-full flex flex-col">
                {/* Chat Input */}
                <div className="p-6 border-b">
                  <h2 className="text-lg font-semibold mb-4">Ask a Question</h2>
                  <ChatInput 
                    onSend={handleSendMessage}
                    isLoading={isLoading}
                    placeholder="Ask about GDP trends, inflation rates, infrastructure data, or social indicators..."
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
                          <li>• "Show me GDP growth trends from 2020-2023"</li>
                          <li>• "What's the retail inflation rate trend?"</li>
                          <li>• "Show PMGSY road development progress by district"</li>
                          <li>• "Display literacy rates by state"</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-background rounded-xl shadow-card border p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-2">Government Datasets</h2>
              <p className="text-muted-foreground">
                Explore 25+ official government datasets from India's data portal, including economic indicators, 
                infrastructure data, social statistics, and environmental metrics.
              </p>
            </div>
            <GovernmentDatasets />
          </div>
        )}
      </div>
    </div>
  );
}