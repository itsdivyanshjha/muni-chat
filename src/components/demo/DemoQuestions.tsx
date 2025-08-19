import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lightbulb, TrendingUp, Database, Leaf, Building2, GraduationCap } from 'lucide-react';
import { demoQuestions, DemoQuestion } from '@/lib/demoData';

interface DemoQuestionsProps {
  onQuestionSelect: (question: string) => void;
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'Economic':
      return <TrendingUp className="h-5 w-5" />;
    case 'Infrastructure':
      return <Building2 className="h-5 w-5" />;
    case 'Social':
      return <GraduationCap className="h-5 w-5" />;
    case 'Environmental':
      return <Leaf className="h-5 w-5" />;
    default:
      return <Database className="h-5 w-5" />;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'Economic':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'Infrastructure':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'Social':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'Environmental':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export function DemoQuestions({ onQuestionSelect }: DemoQuestionsProps) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold mb-3 flex items-center justify-center gap-2">
          <Lightbulb className="h-6 w-6 text-yellow-500" />
          Try These Demo Questions
        </h3>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Explore our AI-powered insights with these curated questions covering key areas of government data. 
          Each question demonstrates different analytical capabilities and data sources.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {demoQuestions.map((question) => (
          <Card key={question.id} className="hover:shadow-lg transition-shadow duration-200 cursor-pointer group">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2 text-muted-foreground">
                  {getCategoryIcon(question.category)}
                  <Badge 
                    variant="outline" 
                    className={`${getCategoryColor(question.category)} border`}
                  >
                    {question.category}
                  </Badge>
                </div>
              </div>
              <CardTitle className="text-lg leading-tight group-hover:text-primary transition-colors">
                {question.question}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
                {question.description}
              </p>
              <Button 
                onClick={() => onQuestionSelect(question.question)}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
              >
                Ask This Question
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="text-center py-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm">
          <Lightbulb className="h-4 w-4" />
          <span>These are demo responses to showcase the platform's capabilities</span>
        </div>
      </div>
    </div>
  );
}
