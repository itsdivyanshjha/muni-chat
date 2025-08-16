import { useState } from 'react';
import { Copy, Database, ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface SqlAccordionProps {
  sql: string;
}

export function SqlAccordion({ sql }: SqlAccordionProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql);
      toast({
        title: "Copied to clipboard",
        description: "SQL query has been copied to your clipboard"
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Unable to copy to clipboard",
        variant: "destructive"
      });
    }
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-3">
        <Button
          variant="ghost"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-between w-full p-0 h-auto hover:bg-transparent"
        >
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            <span className="font-semibold">SQL Query</span>
          </div>
          {isOpen ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
      </CardHeader>
      
      {isOpen && (
        <CardContent className="pt-0">
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="absolute top-2 right-2 z-10"
            >
              <Copy className="h-3 w-3 mr-1" />
              Copy
            </Button>
            <pre className={cn(
              "p-4 bg-muted rounded-lg text-sm overflow-x-auto",
              "font-mono leading-relaxed"
            )}>
              <code>{sql}</code>
            </pre>
          </div>
        </CardContent>
      )}
    </Card>
  );
}