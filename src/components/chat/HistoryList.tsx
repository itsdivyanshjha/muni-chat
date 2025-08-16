import { Clock, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { HistoryItem } from '@/lib/types';
import { cn } from '@/lib/utils';

interface HistoryListProps {
  items: HistoryItem[];
  onItemClick: (item: HistoryItem) => void;
  currentItemId?: string;
}

export function HistoryList({ items, onItemClick, currentItemId }: HistoryListProps) {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <MessageSquare className="h-12 w-12 text-muted-foreground/50 mb-4" />
        <p className="text-sm text-muted-foreground">No conversation history yet</p>
        <p className="text-xs text-muted-foreground">Start by asking a question</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-2 p-2">
        {items.map((item) => (
          <Button
            key={item.id}
            variant="ghost"
            onClick={() => onItemClick(item)}
            className={cn(
              "w-full justify-start text-left h-auto p-3",
              "hover:bg-accent transition-colors",
              currentItemId === item.id && "bg-accent"
            )}
          >
            <div className="flex-1 min-w-0">
              <div className="truncate text-sm font-medium mb-1">
                {item.prompt}
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {item.createdAt.toLocaleDateString()} {item.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </Button>
        ))}
      </div>
    </ScrollArea>
  );
}