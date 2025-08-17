import { useState } from 'react';
import { Copy, Database, ChevronDown, ChevronRight, Play, RotateCcw, Download, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface SqlAccordionProps {
  sql: string;
}

const rowLimits = [
  { value: '50', label: '50 rows' },
  { value: '100', label: '100 rows' },
  { value: '500', label: '500 rows' },
  { value: '1000', label: '1,000 rows' },
  { value: '5000', label: '5,000 rows' }
];

export function SqlAccordion({ sql }: SqlAccordionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedLimit, setSelectedLimit] = useState('50');
  const [isExecuting, setIsExecuting] = useState(false);

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

  const handleExecuteQuery = async () => {
    setIsExecuting(true);
    try {
      // Simulate query execution - in real app, this would call the backend
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast({
        title: "Query executed",
        description: `Fetched ${selectedLimit} rows successfully`,
      });
    } catch (error) {
      toast({
        title: "Query failed",
        description: "Unable to execute query",
        variant: "destructive"
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const formatSql = (sqlString: string) => {
    return sqlString
      .replace(/\b(SELECT|FROM|WHERE|JOIN|GROUP BY|ORDER BY|HAVING|LIMIT)\b/gi, '\n$1')
      .replace(/\s+/g, ' ')
      .trim();
  };

  return (
    <Card className="shadow-xl border-0 bg-gradient-to-br from-gray-50 to-slate-50">
      <CardHeader className="bg-gradient-to-r from-slate-600 to-gray-700 text-white">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 p-0 h-auto hover:bg-white/10 text-white"
          >
            <Database className="h-5 w-5 text-blue-300" />
            <CardTitle className="text-lg">SQL Query Explorer</CardTitle>
            {isOpen ? (
              <ChevronDown className="h-4 w-4 ml-2" />
            ) : (
              <ChevronRight className="h-4 w-4 ml-2" />
            )}
          </Button>
          
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
              <Eye className="h-3 w-3 mr-1" />
              Database Query
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      {isOpen && (
        <CardContent className="p-6">
          {/* Query Controls */}
          <div className="flex flex-wrap items-center gap-3 mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Row Limit:</span>
              <Select value={selectedLimit} onValueChange={setSelectedLimit}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {rowLimits.map((limit) => (
                    <SelectItem key={limit.value} value={limit.value}>
                      {limit.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <Button
              onClick={handleExecuteQuery}
              disabled={isExecuting}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              {isExecuting ? (
                <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              {isExecuting ? 'Executing...' : 'Run Query'}
            </Button>
            
            <Button variant="outline" onClick={handleCopy}>
              <Copy className="h-4 w-4 mr-2" />
              Copy SQL
            </Button>
            
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Results
            </Button>
          </div>

          {/* Formatted SQL Display */}
          <div className="relative">
            <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-green-300 font-mono leading-relaxed">
                <code>{formatSql(sql)}</code>
              </pre>
            </div>
            
            {/* Query Info */}
            <div className="mt-3 flex items-center gap-4 text-xs text-gray-600">
              <span>Query Type: SELECT</span>
              <span>•</span>
              <span>Estimated rows: {selectedLimit}</span>
              <span>•</span>
              <span>Format: PostgreSQL</span>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}