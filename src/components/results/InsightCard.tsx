import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { InsightResponse } from '@/lib/types';
import { Calendar, MapPin, Tag } from 'lucide-react';

interface InsightCardProps {
  insight: InsightResponse;
}

export function InsightCard({ insight }: InsightCardProps) {
  const { insight_text, filters_applied, disclaimers } = insight;

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-4">
        <div className="flex flex-wrap gap-2 mb-3">
          {filters_applied.time.from && (
            <Badge variant="secondary" className="gap-1">
              <Calendar className="h-3 w-3" />
              {filters_applied.time.from} - {filters_applied.time.to}
            </Badge>
          )}
          {filters_applied.place.ward && (
            <Badge variant="secondary" className="gap-1">
              <MapPin className="h-3 w-3" />
              {filters_applied.place.ward}
            </Badge>
          )}
          {filters_applied.place.zone && (
            <Badge variant="secondary" className="gap-1">
              <MapPin className="h-3 w-3" />
              {filters_applied.place.zone}
            </Badge>
          )}
          {filters_applied.extra.category && (
            <Badge variant="secondary" className="gap-1">
              <Tag className="h-3 w-3" />
              {filters_applied.extra.category}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="prose prose-sm max-w-none">
          <p className="text-foreground leading-relaxed">{insight_text}</p>
        </div>
        
        {disclaimers.length > 0 && (
          <div className="mt-4 p-3 bg-muted/50 rounded-lg">
            <p className="text-xs font-medium text-muted-foreground mb-2">Disclaimers:</p>
            <ul className="text-xs text-muted-foreground space-y-1">
              {disclaimers.map((disclaimer, index) => (
                <li key={index}>• {disclaimer}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}