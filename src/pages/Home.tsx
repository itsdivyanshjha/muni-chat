import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, Database, MessageSquare, Sparkles } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { ChatInput } from '@/components/chat/ChatInput';
import { HistoryList } from '@/components/chat/HistoryList';
import { FilterBar } from '@/components/filters/FilterBar';
import { InsightCard } from '@/components/results/InsightCard';
import { ChartRenderer } from '@/components/results/ChartRenderer';
import { AnalyticsDashboard } from '@/components/results/AnalyticsDashboard';
import { DataPreviewTable } from '@/components/results/DataPreviewTable';
import { SqlAccordion } from '@/components/results/SqlAccordion';
import { CitationsList } from '@/components/results/CitationsList';
import { GovernmentDatasets } from '@/components/datasets/GovernmentDatasets';
import { DemoQuestions } from '@/components/demo/DemoQuestions';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { useFilters } from '@/stores/filters';
import { useHistory } from '@/stores/history';
import { HistoryItem, InsightResponse } from '@/lib/types';
import { toast } from '@/hooks/use-toast';
import { useTheme } from '@/hooks/use-theme';
import { getDemoQuestion, demoQuestions } from '@/lib/demoData';

export default function Home() {
  const { filters } = useFilters();
  const { items, currentItem, addItem, setCurrentItem } = useHistory();
  const [currentResponse, setCurrentResponse] = useState<InsightResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'datasets'>('chat');
  const { theme } = useTheme();
  const isDark = theme === 'dark';


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
    // Check if this is a demo question
    const demoQuestion = demoQuestions.find(q => q.question === prompt);
    if (demoQuestion) {
      setCurrentResponse(demoQuestion.response);
      const historyItem: HistoryItem = {
        id: crypto.randomUUID(),
        prompt: prompt,
        filters: filters,
        createdAt: new Date(),
        response: demoQuestion.response
      };
      addItem(historyItem);
      toast({
        title: "Insight generated",
        description: "Your municipal data analysis is ready"
      });
    } else {
      insightMutation.mutate({ prompt, filters });
    }
  };

  const handleHistoryItemClick = (item: HistoryItem) => {
    setCurrentItem(item);
    setCurrentResponse(item.response || null);
  };

  const displayResponse = currentResponse || currentItem?.response;
  const isLoading = insightMutation.isPending;

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <Header />
      
      <div className="w-full px-4 pt-2 pb-4">
        {/* Tab Navigation */}
        <div className={`flex space-x-1 mb-4 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-xl p-1 shadow-sm border`}>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-3 px-6 py-3 rounded-lg transition-all duration-200 font-medium ${
              activeTab === 'chat'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                : `${isDark ? 'text-gray-300 hover:text-white hover:bg-gray-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`
            }`}
          >
            <MessageSquare className="h-5 w-5" />
            Chat & Analysis
          </button>
          <button
            onClick={() => setActiveTab('datasets')}
            className={`flex items-center gap-3 px-6 py-3 rounded-lg transition-all duration-200 font-medium ${
              activeTab === 'datasets'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                : `${isDark ? 'text-gray-300 hover:text-white hover:bg-gray-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`
            }`}
          >
            <Database className="h-5 w-5" />
            Government Datasets
          </button>
        </div>

        {activeTab === 'chat' ? (
          <div className="flex gap-4 h-[calc(100vh-10rem)]">
            {/* Left Sidebar - Chat Interface */}
            <div className="w-72 flex flex-col">
              <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-xl shadow-lg border h-full flex flex-col`}>
                {/* Chat Input Section */}
                <div className="p-4 border-b">
                  <h2 className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-700'} mb-3`}>Ask a Question</h2>
                  <ChatInput 
                    onSend={handleSendMessage}
                    isLoading={isLoading}
                    placeholder="Ask about municipal data..."
                  />
                </div>
                
                {/* History Section */}
                <div className="flex-1 overflow-hidden">
                  <div className={`p-3 border-b ${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
                    <h3 className={`font-medium text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} uppercase tracking-wide`}>Recent Conversations</h3>
                  </div>
                  <HistoryList 
                    items={items}
                    onItemClick={handleHistoryItemClick}
                    currentItemId={currentItem?.id}
                  />
                </div>
              </div>
            </div>

            {/* Main Content Area - Results */}
            <div className="flex-1 flex flex-col">
              <FilterBar />
              
              <div className="flex-1 overflow-y-auto pt-2">
                {isLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-6 w-6 animate-spin" />
                      <span className="text-lg">Analyzing municipal data...</span>
                    </div>
                  </div>
                ) : displayResponse ? (
                  <div className="space-y-4 pb-4">
                    <InsightCard insight={displayResponse} />
                    <AnalyticsDashboard insight={displayResponse} />
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <DataPreviewTable dataPreview={displayResponse.data_preview} />
                      <div className="space-y-4">
                        <SqlAccordion sql={displayResponse.sql_used} />
                        <CitationsList citations={displayResponse.doc_citations} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-64 text-center">
                    <div className="max-w-2xl">
                      <div className="mb-6">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full mb-4">
                          <Sparkles className="h-8 w-8 text-blue-600" />
                        </div>
                        <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                          Welcome to Municipal AI Insights
                        </h3>
                        <p className="text-lg text-muted-foreground mb-6">
                          Your AI-powered gateway to government data analysis. Get instant insights from 25+ official datasets.
                        </p>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-6 text-left">
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                          <h4 className="font-semibold text-blue-900 mb-2">🚀 Quick Start</h4>
                          <ul className="text-sm text-blue-800 space-y-1">
                            <li>• Try the demo questions below</li>
                            <li>• Ask about GDP, inflation, or infrastructure</li>
                            <li>• Use filters to narrow down data</li>
                          </ul>
                        </div>
                        
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                          <h4 className="font-semibold text-purple-900 mb-2">📊 Data Sources</h4>
                          <ul className="text-sm text-purple-800 space-y-1">
                            <li>• Economic indicators & trends</li>
                            <li>• Infrastructure development</li>
                            <li>• Social & education metrics</li>
                            <li>• Environmental data</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 rounded-xl shadow-card border border-blue-100 p-8">
            <div className="mb-8 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full mb-4">
                <Database className="h-8 w-8 text-blue-600" />
              </div>
              <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Government Datasets
              </h2>
              <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
                Explore 25+ official government datasets from India's data portal, including economic indicators, 
                infrastructure data, social statistics, and environmental metrics. All data is sourced from official government APIs and databases.
              </p>
            </div>
            <GovernmentDatasets />
          </div>
        )}
      </div>
    </div>
  );
}