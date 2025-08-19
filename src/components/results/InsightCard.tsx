import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { InsightResponse } from '@/lib/types';
import { Calendar, MapPin, Tag, Lightbulb, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';

interface InsightCardProps {
  insight: InsightResponse;
}

export function InsightCard({ insight }: InsightCardProps) {
  const { insight_text, filters_applied, disclaimers } = insight;
  
  // Debug logging
  console.log('InsightCard received:', { insight_text, filters_applied, disclaimers });

  // Parse the structured insight text
  const parseInsightText = (text: string) => {
    const sections = {
      summary: '',
      keyFindings: [],
      trends: '',
      observations: '',
      recommendations: []
    };

    // Handle case where text might be JSON or contain JSON
    let cleanText = text;
    
    // If the text contains JSON, extract the insight_text field
    if (text.includes('{') && text.includes('}')) {
      try {
        // Try to find and parse JSON in the text
        const jsonMatch = text.match(/\{.*\}/s);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.insight_text) {
            cleanText = parsed.insight_text;
          }
        }
      } catch (e) {
        console.warn('Failed to parse JSON in insight text:', e);
        // Fall back to original text
      }
    }

    // Simple parsing - in a real app, you'd want more robust parsing
    const lines = cleanText.split('\n').filter(line => line.trim());
    let currentSection = 'summary';
    
    lines.forEach(line => {
      if (line.includes('## Executive Summary')) {
        currentSection = 'summary';
      } else if (line.includes('## Key Findings')) {
        currentSection = 'keyFindings';
      } else if (line.includes('## Trend Analysis') || line.includes('Dataset Distribution Analysis')) {
        currentSection = 'trends';
      } else if (line.includes('## Notable Observations')) {
        currentSection = 'observations';
      } else if (line.includes('## Actionable Recommendations')) {
        currentSection = 'recommendations';
      } else if (line.trim() && !line.startsWith('##')) {
        if (currentSection === 'keyFindings' && line.startsWith('•')) {
          sections.keyFindings.push(line.substring(1).trim());
        } else if (currentSection === 'recommendations' && (line.startsWith('1.') || line.startsWith('2.') || line.startsWith('3.') || line.startsWith('4.'))) {
          sections.recommendations.push(line.substring(2).trim());
        } else if (currentSection === 'summary') {
          sections.summary += line + ' ';
        } else if (currentSection === 'trends') {
          sections.trends += line + ' ';
        } else if (currentSection === 'observations') {
          sections.observations += line + ' ';
        }
      }
    });

    return sections;
  };

  const sections = parseInsightText(insight_text);

  return (
    <Card className="shadow-xl border-0 bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <CardHeader className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Lightbulb className="h-6 w-6 text-yellow-300" />
            AI-Powered Insights
          </CardTitle>
          <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
            <TrendingUp className="h-3 w-3 mr-1" />
            Analysis Report
          </Badge>
        </div>
        
        {/* Filters Applied */}
        <div className="flex flex-wrap gap-2 mt-3">
          {filters_applied?.time?.from && (
            <Badge variant="outline" className="bg-white/10 text-white border-white/30">
              <Calendar className="h-3 w-3 mr-1" />
              {filters_applied.time.from} - {filters_applied.time.to}
            </Badge>
          )}
          {filters_applied?.place?.ward && (
            <Badge variant="outline" className="bg-white/10 text-white border-white/30">
              <MapPin className="h-3 w-3 mr-1" />
              {filters_applied.place.ward}
            </Badge>
          )}
          {filters_applied?.place?.zone && (
            <Badge variant="outline" className="bg-white/10 text-white border-white/30">
              <MapPin className="h-3 w-3 mr-1" />
              {filters_applied.place.zone}
            </Badge>
          )}
          {filters_applied?.extra?.category && (
            <Badge variant="outline" className="bg-white/10 text-white border-white/30">
              <Tag className="h-3 w-3 mr-1" />
              {filters_applied.extra.category}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="p-6">
        {/* Executive Summary */}
        {sections.summary && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Executive Summary
            </h3>
            <p className="text-blue-800 leading-relaxed">{sections.summary.trim()}</p>
          </div>
        )}

        {/* Key Findings */}
        {sections.keyFindings.length > 0 && (
          <div className="mb-6 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Key Findings
            </h3>
            <ul className="space-y-2">
              {sections.keyFindings.map((finding, index) => (
                <li key={index} className="flex items-start gap-2 text-green-800">
                  <span className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Trend Analysis */}
        {sections.trends && (
          <div className="mb-6 p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500">
            <h3 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Analysis Insights
            </h3>
            <p className="text-purple-800 leading-relaxed">{sections.trends.trim()}</p>
          </div>
        )}

        {/* Notable Observations */}
        {sections.observations && (
          <div className="mb-6 p-4 bg-orange-50 rounded-lg border-l-4 border-orange-500">
            <h3 className="font-semibold text-orange-900 mb-2 flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Notable Observations
            </h3>
            <p className="text-orange-800 leading-relaxed">{sections.observations.trim()}</p>
          </div>
        )}

        {/* Recommendations */}
        {sections.recommendations.length > 0 && (
          <div className="mb-6 p-4 bg-indigo-50 rounded-lg border-l-4 border-indigo-500">
            <h3 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Actionable Recommendations
            </h3>
            <ol className="space-y-2">
              {sections.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-3 text-indigo-800">
                  <span className="bg-indigo-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {index + 1}
                  </span>
                  <span>{rec}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Fallback for unstructured text */}
        {!sections.summary && !sections.keyFindings.length && (
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed text-lg">{insight_text}</p>
          </div>
        )}
        
        {/* Disclaimers */}
        {disclaimers && disclaimers.length > 0 && (
          <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <p className="text-sm font-semibold text-yellow-800">Important Disclaimers</p>
            </div>
            <ul className="text-sm text-yellow-700 space-y-1">
              {disclaimers.map((disclaimer, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-yellow-600">•</span>
                  <span>{disclaimer}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}