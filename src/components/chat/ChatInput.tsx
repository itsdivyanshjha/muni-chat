import { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, isLoading = false, placeholder = "Ask a question about municipal data..." }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className={cn(
            "min-h-[80px] resize-none pr-12 text-sm border-gray-200",
            "focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          )}
        />
        <Button
          type="submit"
          size="sm"
          disabled={!message.trim() || isLoading}
          className={cn(
            "absolute bottom-2 right-2 h-7 w-7 bg-blue-600 hover:bg-blue-700",
            "disabled:opacity-50"
          )}
        >
          <Send className="h-3 w-3" />
        </Button>
      </div>
      <div className="text-xs text-gray-500">
        <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">↵</kbd> send • <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">⇧↵</kbd> new line
      </div>
    </form>
  );
}