import { useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Download, BarChart3, LineChart, PieChart, ScatterChart, TrendingUp, Activity, Expand, Palette } from 'lucide-react';
import { VegaLiteSpec, DataPreview } from '@/lib/types';
import { toast } from '@/hooks/use-toast';

const chartTypes = [
  { value: 'auto', label: 'AI Generated', icon: TrendingUp, description: 'Let AI choose the best visualization' },
  { value: 'bar', label: 'Bar Chart', icon: BarChart3, description: 'Compare categories and values' },
  { value: 'line', label: 'Line Chart', icon: LineChart, description: 'Show trends over time' },
  { value: 'area', label: 'Area Chart', icon: Activity, description: 'Filled trend visualization' },
  { value: 'scatter', label: 'Scatter Plot', icon: ScatterChart, description: 'Show correlations' },
  { value: 'pie', label: 'Pie Chart', icon: PieChart, description: 'Show proportions' }
];

const colorSchemes = [
  { value: 'category10', label: 'Vibrant', colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'] },
  { value: 'set3', label: 'Pastel', colors: ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072'] },
  { value: 'dark2', label: 'Dark', colors: ['#1b9e77', '#d95f02', '#7570b3', '#e7298a'] },
  { value: 'tableau10', label: 'Professional', colors: ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2'] }
];

interface ChartRendererProps {
  spec: VegaLiteSpec;
  dataPreview: DataPreview;
}

export function ChartRenderer({ spec, dataPreview }: ChartRendererProps) {
  const [processedSpec, setProcessedSpec] = useState<any>(null);
  const [selectedChart, setSelectedChart] = useState<string>('auto');
  const [selectedColors, setSelectedColors] = useState<string>('category10');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const generateCustomSpec = (chartType: string, data: any[]) => {
    if (!data.length || !dataPreview.columns.length) return null;
    
    const xField = dataPreview.columns[0];
    const yField = dataPreview.columns[1];
    
    const baseSpec = {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "width": isFullscreen ? 700 : 500,
      "height": isFullscreen ? 450 : 350,
      "data": { "values": data },
      "background": "transparent",
      "config": {
        "font": "Inter, system-ui, sans-serif",
        "axis": {
          "labelFont": "Inter, system-ui, sans-serif",
          "titleFont": "Inter, system-ui, sans-serif",
          "labelFontSize": 11,
          "titleFontSize": 12,
          "grid": true,
          "gridOpacity": 0.3
        },
        "legend": {
          "labelFont": "Inter, system-ui, sans-serif",
          "titleFont": "Inter, system-ui, sans-serif",
          "labelFontSize": 11,
          "titleFontSize": 12
        }
      }
    };

    switch (chartType) {
      case 'bar':
        return {
          ...baseSpec,
          "mark": { 
            "type": "bar", 
            "cornerRadiusTopLeft": 4, 
            "cornerRadiusTopRight": 4,
            "tooltip": true,
            "opacity": 0.8
          },
          "encoding": {
            "x": { "field": xField, "type": "nominal", "axis": { "labelAngle": -45 } },
            "y": { "field": yField, "type": "quantitative" },
            "color": {
              "field": xField,
              "type": "nominal",
              "scale": { "scheme": selectedColors },
              "legend": null
            }
          }
        };
      
      case 'line':
        return {
          ...baseSpec,
          "mark": { 
            "type": "line", 
            "point": { "size": 60, "filled": true },
            "strokeWidth": 3, 
            "tooltip": true 
          },
          "encoding": {
            "x": { "field": xField, "type": "nominal" },
            "y": { "field": yField, "type": "quantitative" },
            "color": { "value": "#3b82f6" }
          }
        };
      
      case 'area':
        return {
          ...baseSpec,
          "mark": { "type": "area", "opacity": 0.7, "tooltip": true },
          "encoding": {
            "x": { "field": xField, "type": "nominal" },
            "y": { "field": yField, "type": "quantitative" },
            "color": { "value": "#10b981" }
          }
        };
      
      case 'scatter':
        return {
          ...baseSpec,
          "mark": { "type": "circle", "size": 100, "opacity": 0.8, "tooltip": true },
          "encoding": {
            "x": { "field": xField, "type": "quantitative" },
            "y": { "field": yField, "type": "quantitative" },
            "color": {
              "field": dataPreview.columns[2] || xField,
              "type": "nominal",
              "scale": { "scheme": selectedColors }
            }
          }
        };
      
      case 'pie':
        return {
          ...baseSpec,
          "mark": { "type": "arc", "innerRadius": 50, "tooltip": true },
          "encoding": {
            "theta": { "field": yField, "type": "quantitative" },
            "color": {
              "field": xField,
              "type": "nominal",
              "scale": { "scheme": selectedColors }
            }
          }
        };
      
      default:
        return null;
    }
  };

  useEffect(() => {
    const data = dataPreview.rows.map(row => {
      const obj: any = {};
      dataPreview.columns.forEach((col, index) => {
        obj[col] = row[index];
      });
      return obj;
    });

    let newSpec;

    if (selectedChart === 'auto' && spec?.spec) {
      newSpec = { ...spec.spec };
      if (newSpec.data?.values === "__INLINE_DATA__") {
        newSpec.data = { values: data };
      }
      
      // Apply theming and color scheme
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

      // Update color scheme if possible
      if (newSpec.encoding?.color?.scale) {
        newSpec.encoding.color.scale.scheme = selectedColors;
      }
    } else {
      newSpec = generateCustomSpec(selectedChart, data);
    }
    
    setProcessedSpec(newSpec);
  }, [spec, dataPreview, selectedChart, selectedColors, isFullscreen]);

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
      <Card className="shadow-lg border-0 bg-gradient-to-br from-blue-50 to-purple-50">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Visualization
          </CardTitle>
        </CardHeader>
        <CardContent className="p-8">
          <div className="flex flex-col items-center justify-center h-64 bg-white/70 rounded-lg border-2 border-dashed border-blue-300">
            <TrendingUp className="h-12 w-12 text-blue-400 mb-4" />
            <p className="text-blue-600 font-medium">No chart data available</p>
            <p className="text-blue-500 text-sm mt-2">Try adjusting your query to get visualizable data</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-xl border-0 bg-gradient-to-br from-white to-gray-50">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Interactive Visualization
          </CardTitle>
          
          <div className="flex flex-wrap items-center gap-3">
            <Select value={selectedChart} onValueChange={setSelectedChart}>
              <SelectTrigger className="w-40 bg-white/20 border-white/30 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {chartTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    <div className="flex items-center gap-2">
                      <type.icon className="h-4 w-4" />
                      <span>{type.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedColors} onValueChange={setSelectedColors}>
              <SelectTrigger className="w-32 bg-white/20 border-white/30 text-white">
                <Palette className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {colorSchemes.map((scheme) => (
                  <SelectItem key={scheme.value} value={scheme.value}>
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        {scheme.colors.map((color, i) => (
                          <div
                            key={i}
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                      <span>{scheme.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="bg-white/20 border-white/30 text-white hover:bg-white/30"
            >
              <Expand className="h-4 w-4 mr-2" />
              {isFullscreen ? 'Normal' : 'Expand'}
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={handleDownload}
              className="bg-white/20 border-white/30 text-white hover:bg-white/30"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
        
        {/* Chart Type Description */}
        <div className="mt-3 flex items-center gap-2">
          <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
            {chartTypes.find(t => t.value === selectedChart)?.description || 'Custom visualization'}
          </Badge>
          <Badge variant="outline" className="bg-white/10 text-white border-white/30">
            {dataPreview.rows.length} data points
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="p-6">
        <div className="w-full overflow-x-auto bg-white rounded-lg shadow-inner p-4">
          <VegaLite
            spec={processedSpec}
            actions={{
              export: true,
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