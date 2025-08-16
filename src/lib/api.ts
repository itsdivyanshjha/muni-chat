import { InsightRequest, InsightResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  async getInsight(payload: InsightRequest): Promise<InsightResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/insights`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      
      // Return mock data for development
      return getMockInsight(payload);
    }
  },

  async getSchema(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/schema`);
      
      if (!response.ok) {
        throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
      }

      return await response.json();
    } catch (error) {
      return getMockSchema();
    }
  }
};

// Mock data for development
function getMockInsight(request: InsightRequest): InsightResponse {
  return {
    insight_text: `Based on your query "${request.prompt}", here are the key findings from the municipal data. The analysis shows interesting patterns in the selected time period and geographical area.`,
    sql_used: `SELECT 
  category,
  COUNT(*) as count,
  AVG(value) as avg_value
FROM municipal_data 
WHERE date BETWEEN '${request.filters.time.from}' AND '${request.filters.time.to}'
${request.filters.place.ward ? `AND ward = '${request.filters.place.ward}'` : ''}
GROUP BY category
ORDER BY count DESC;`,
    data_preview: {
      columns: ['Category', 'Count', 'Average Value', 'Percentage'],
      rows: [
        ['Parks & Recreation', 45, 8.2, '35%'],
        ['Transportation', 32, 7.8, '25%'],
        ['Public Safety', 28, 9.1, '22%'],
        ['Utilities', 23, 6.5, '18%']
      ]
    },
    viz: {
      type: 'vega-lite',
      spec: {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Municipal Data Analysis",
        "data": {"values": "__INLINE_DATA__"},
        "mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
        "encoding": {
          "x": {"field": "Category", "type": "nominal", "axis": {"labelAngle": -45}},
          "y": {"field": "Count", "type": "quantitative"},
          "color": {
            "field": "Category",
            "type": "nominal",
            "scale": {"scheme": "blues"}
          }
        },
        "width": 400,
        "height": 300
      }
    },
    doc_citations: [
      {
        title: "Municipal Budget Report 2024",
        url: "https://example.com/budget-2024",
        excerpt: "This comprehensive report outlines the city's budget allocation across various departments, highlighting significant investments in infrastructure and public services."
      },
      {
        title: "Public Safety Annual Review",
        url: "https://example.com/safety-review",
        excerpt: "An in-depth analysis of public safety metrics, response times, and community engagement initiatives implemented throughout the year."
      }
    ],
    filters_applied: request.filters,
    disclaimers: [
      "Data is aggregated from multiple municipal sources",
      "Some data points may be estimates based on available information",
      "Results are subject to ongoing data validation processes"
    ]
  };
}

function getMockSchema(): any {
  return {
    tables: [
      {
        name: "municipal_data",
        columns: [
          { name: "id", type: "integer" },
          { name: "category", type: "text" },
          { name: "date", type: "date" },
          { name: "ward", type: "text" },
          { name: "zone", type: "text" },
          { name: "value", type: "numeric" }
        ]
      }
    ]
  };
}