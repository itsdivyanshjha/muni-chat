import { useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, BarChart3 } from 'lucide-react';
import { VegaLiteSpec, DataPreview } from '@/lib/types';
import { toast } from '@/hooks/use-toast';

interface ChartRendererProps {
  spec: VegaLiteSpec;
  dataPreview: DataPreview;
}

export function ChartRenderer({ spec, dataPreview }: ChartRendererProps) {
  const [processedSpec, setProcessedSpec] = useState<any>(null);

  useEffect(() => {
    if (spec?.spec) {
      let newSpec = { ...spec.spec };
      
      // Replace inline data placeholder with actual data
      if (newSpec.data?.values === "__INLINE_DATA__") {
        const data = dataPreview.rows.map(row => {
          const obj: any = {};
          dataPreview.columns.forEach((col, index) => {
            obj[col] = row[index];
          });
          return obj;
        });
        newSpec.data = { values: data };
      }
      
      // Ensure proper theming
      newSpec.config = {
        ...newSpec.config,
        background: 'transparent',
        font: 'Inter, system-ui, sans-serif',
        axis: {
          labelFont: 'Inter, system-ui, sans-serif',
          titleFont: 'Inter, system-ui, sans-serif',
          labelFontSize: 11,
          titleFontSize: 12,
        },
        legend: {
          labelFont: 'Inter, system-ui, sans-serif',
          titleFont: 'Inter, system-ui, sans-serif',
          labelFontSize: 11,
          titleFontSize: 12,
        }
      };
      
      setProcessedSpec(newSpec);
    }
  }, [spec, dataPreview]);

  const handleDownload = () => {
    // This would typically export the chart as PNG
    // For now, we'll show a placeholder toast
    toast({
      title: "Download feature",
      description: "Chart download functionality would be implemented here"
    });
  };

  if (!processedSpec) {
    return (
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Visualization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 bg-muted/30 rounded-lg">
            <p className="text-muted-foreground">No chart data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-card">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Visualization
        </CardTitle>
        <Button variant="outline" size="sm" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Export PNG
        </Button>
      </CardHeader>
      <CardContent>
        <div className="w-full overflow-x-auto">
          <VegaLite
            spec={processedSpec}
            actions={{
              export: false,
              source: false,
              compiled: false,
              editor: false
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
}