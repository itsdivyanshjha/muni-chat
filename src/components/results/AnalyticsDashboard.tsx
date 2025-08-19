import { useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, BarChart3, Activity, DollarSign, Users, MapPin, Calendar } from 'lucide-react';
import { InsightResponse } from '@/lib/types';
import { colors, financialColors } from '@/lib/colors';
import { useTheme } from '@/hooks/use-theme';

interface AnalyticsDashboardProps {
  insight: InsightResponse;
}

export function AnalyticsDashboard({ insight }: AnalyticsDashboardProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  // Extract data for charts
  const data = insight.data_preview.rows.map(row => {
    const obj: any = {};
    insight.data_preview.columns.forEach((col, index) => {
      let value = row[index];
      // Parse numeric values from strings
      if (typeof value === 'string' && value.includes('₹')) {
        const numMatch = value.match(/[\d,]+/);
        if (numMatch) {
          obj[`${col}_numeric`] = parseFloat(numMatch[0].replace(/,/g, ''));
          obj[`${col}_display`] = value;
        }
      } else if (typeof value === 'string' && value.includes('%')) {
        const numMatch = value.match(/[\d.]+/);
        if (numMatch) {
          obj[`${col}_numeric`] = parseFloat(numMatch[0]);
          obj[`${col}_display`] = value;
        }
      } else {
        obj[col] = value;
      }
    });
    return obj;
  });

  // KPI Cards Data
  const kpis = [
    {
      title: 'Total Budget',
      value: '₹2,50,000 Cr',
      change: '+12.5%',
      trend: 'up',
      icon: DollarSign,
      color: financialColors.profit
    },
    {
      title: 'Citizens Served',
      value: '2.1M',
      change: '+5.2%',
      trend: 'up',
      icon: Users,
      color: financialColors.growth
    },
    {
      title: 'Service Coverage',
      value: '89%',
      change: '+3.1%',
      trend: 'up',
      icon: MapPin,
      color: colors.pacificCyan
    },
    {
      title: 'Project Completion',
      value: '78%',
      change: '-2.1%',
      trend: 'down',
      icon: Activity,
      color: financialColors.decline
    }
  ];

  // Revenue and Cost Chart
  const revenueChart = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {
      "values": [
        {"month": "Jan", "revenue": 21000, "costs": 18000, "profit": 3000},
        {"month": "Feb", "revenue": 23000, "costs": 19000, "profit": 4000},
        {"month": "Mar", "revenue": 25000, "costs": 20000, "profit": 5000},
        {"month": "Apr", "revenue": 24000, "costs": 21000, "profit": 3000},
        {"month": "May", "revenue": 27000, "costs": 22000, "profit": 5000},
        {"month": "Jun", "revenue": 29000, "costs": 23000, "profit": 6000}
      ]
    },
    "width": "container",
    "height": 250,
    "background": "transparent",
    "config": {
      "font": "Inter, system-ui, sans-serif",
      "axis": {
        "labelColor": isDark ? colors.dark.textMuted : colors.light.textMuted,
        "titleColor": isDark ? colors.dark.text : colors.light.text,
        "gridColor": isDark ? colors.dark.border : colors.light.border,
        "gridOpacity": 0.3
      },
      "legend": {
        "labelColor": isDark ? colors.dark.text : colors.light.text,
        "titleColor": isDark ? colors.dark.text : colors.light.text
      }
    },
    "layer": [
      {
        "mark": {"type": "line", "point": true, "strokeWidth": 3},
        "encoding": {
          "x": {"field": "month", "type": "ordinal", "title": "Month"},
          "y": {"field": "revenue", "type": "quantitative", "title": "Amount (₹ Cr)"},
          "color": {"value": financialColors.profit}
        }
      },
      {
        "mark": {"type": "line", "point": true, "strokeWidth": 3},
        "encoding": {
          "x": {"field": "month", "type": "ordinal"},
          "y": {"field": "costs", "type": "quantitative"},
          "color": {"value": financialColors.loss}
        }
      },
      {
        "mark": {"type": "area", "opacity": 0.3},
        "encoding": {
          "x": {"field": "month", "type": "ordinal"},
          "y": {"field": "profit", "type": "quantitative"},
          "color": {"value": financialColors.growth}
        }
      }
    ]
  };

  // Performance Metrics Chart
  const performanceChart = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {
      "values": data.slice(0, 5)
    },
    "width": "container",
    "height": 200,
    "background": "transparent",
    "config": {
      "font": "Inter, system-ui, sans-serif",
      "axis": {
        "labelColor": isDark ? colors.dark.textMuted : colors.light.textMuted,
        "titleColor": isDark ? colors.dark.text : colors.light.text,
        "gridColor": isDark ? colors.dark.border : colors.light.border
      }
    },
    "mark": {
      "type": "bar",
      "cornerRadiusTopLeft": 4,
      "cornerRadiusTopRight": 4,
      "tooltip": true
    },
    "encoding": {
      "x": {
        "field": insight.data_preview.columns[0],
        "type": "nominal",
        "axis": {"labelAngle": -45}
      },
      "y": {
        "field": insight.data_preview.columns[1],
        "type": "quantitative"
      },
      "color": {
        "field": insight.data_preview.columns[0],
        "type": "nominal",
        "scale": {"range": chartColors}
      }
    }
  };

  // Balance and Costs Donut Chart
  const balanceChart = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {
      "values": [
        {"category": "Infrastructure", "value": 40, "color": colors.honoluluBlue},
        {"category": "Social Services", "value": 30, "color": colors.pacificCyan},
        {"category": "Administration", "value": 20, "color": colors.vividSkyBlue},
        {"category": "Development", "value": 10, "color": colors.nonPhotoBlue}
      ]
    },
    "width": 180,
    "height": 180,
    "background": "transparent",
    "config": {
      "font": "Inter, system-ui, sans-serif",
      "legend": {
        "labelColor": isDark ? colors.dark.text : colors.light.text,
        "titleColor": isDark ? colors.dark.text : colors.light.text
      }
    },
    "mark": {"type": "arc", "innerRadius": 50, "outerRadius": 90, "tooltip": true},
    "encoding": {
      "theta": {"field": "value", "type": "quantitative"},
      "color": {
        "field": "category",
        "type": "nominal",
        "scale": {"range": chartColors}
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <Card key={index} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg hover:shadow-xl transition-shadow`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                    <kpi.icon className="h-5 w-5" style={{ color: kpi.color }} />
                  </div>
                  <div>
                    <p className={`text-xs font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                      {kpi.title}
                    </p>
                    <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                      {kpi.value}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`flex items-center space-x-1 ${kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                    {kpi.trend === 'up' ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    <span className="text-xs font-medium">{kpi.change}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue and Costs Chart */}
        <Card className={`lg:col-span-2 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
              <Activity className="h-5 w-5" style={{ color: financialColors.profit }} />
              Revenue and Costs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <VegaLite spec={revenueChart} actions={false} />
          </CardContent>
        </Card>

        {/* Balance and Costs Donut */}
        <Card className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
              <BarChart3 className="h-5 w-5" style={{ color: colors.pacificCyan }} />
              Budget Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <VegaLite spec={balanceChart} actions={false} />
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className={`flex items-center gap-2 text-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
              <TrendingUp className="h-5 w-5" style={{ color: colors.honoluluBlue }} />
              Performance Metrics
            </CardTitle>
            <div className="flex space-x-2">
              <Badge variant="secondary" className={`${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-700'}`}>
                Live Data
              </Badge>
              <Badge variant="outline" style={{ borderColor: financialColors.profit, color: financialColors.profit }}>
                +5.2% Growth
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <VegaLite spec={performanceChart} actions={false} />
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
          <CardContent className="p-4">
            <div className="text-center">
              <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>98.5%</p>
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Service Uptime</p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '98.5%' }}></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
          <CardContent className="p-4">
            <div className="text-center">
              <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>1,352</p>
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Active Projects</p>
              <div className="flex items-center justify-center mt-2 space-x-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                <span className="text-xs text-green-500 font-medium">+8.2%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-lg`}>
          <CardContent className="p-4">
            <div className="text-center">
              <p className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>₹64K</p>
              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Avg Cost per Citizen</p>
              <div className="flex items-center justify-center mt-2 space-x-1">
                <TrendingDown className="h-3 w-3 text-red-500" />
                <span className="text-xs text-red-500 font-medium">-1.5%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
