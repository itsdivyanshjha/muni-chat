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
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className={cn(
            "min-h-[100px] resize-none pr-12 shadow-card",
            "focus:ring-2 focus:ring-primary/20"
          )}
        />
        <Button
          type="submit"
          size="sm"
          disabled={!message.trim() || isLoading}
          className={cn(
            "absolute bottom-3 right-3 h-8 w-8 bg-gradient-municipal hover:opacity-90",
            "disabled:opacity-50"
          )}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
      <div className="text-xs text-muted-foreground">
        Press <kbd className="px-1 py-0.5 bg-muted rounded">Enter</kbd> to send, <kbd className="px-1 py-0.5 bg-muted rounded">Shift + Enter</kbd> for new line
      </div>
    </form>
  );
}