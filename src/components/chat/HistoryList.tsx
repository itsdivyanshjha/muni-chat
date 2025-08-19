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
      <div className="flex flex-col items-center justify-center py-6 text-center px-4">
        <MessageSquare className="h-8 w-8 text-gray-400 mb-3" />
        <p className="text-xs text-gray-500 mb-1">No conversations yet</p>
        <p className="text-xs text-gray-400">Start by asking a question</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-1 p-2">
        {items.map((item) => (
          <Button
            key={item.id}
            variant="ghost"
            onClick={() => onItemClick(item)}
            className={cn(
              "w-full justify-start text-left h-auto p-2 rounded-lg",
              "hover:bg-blue-50 transition-colors text-gray-700",
              currentItemId === item.id && "bg-blue-100 border border-blue-200"
            )}
          >
            <div className="flex-1 min-w-0">
              <div className="truncate text-xs font-medium mb-1 leading-tight">
                {item.prompt}
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                {item.createdAt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} {item.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </Button>
        ))}
      </div>
    </ScrollArea>
  );
}