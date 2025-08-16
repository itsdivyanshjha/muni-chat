import { ExternalLink, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DocCitation } from '@/lib/types';

interface CitationsListProps {
  citations: DocCitation[];
}

export function CitationsList({ citations }: CitationsListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Sources & Citations ({citations.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {citations.map((citation, index) => (
            <div key={index} className="border rounded-lg p-4 hover:bg-accent/50 transition-colors">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm mb-2 leading-tight">
                    {citation.title}
                  </h4>
                  <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                    {citation.excerpt}
                  </p>
                </div>
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-primary hover:text-primary/80 text-sm font-medium whitespace-nowrap"
                >
                  View
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}