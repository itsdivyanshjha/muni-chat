export interface DemoQuestion {
  id: string;
  question: string;
  category: string;
  description: string;
  response: any;
}

export const demoQuestions: DemoQuestion[] = [
  {
    id: "gdp-trends",
    question: "What are the GDP growth trends in India from 2020-2023?",
    category: "Economic",
    description: "Analyze India's economic performance and recovery patterns",
    response: {
      insight_text: `## Executive Summary
India's GDP growth has shown remarkable resilience and recovery patterns from 2020-2023, transitioning from pandemic-induced contraction to strong economic expansion.

## Key Findings
• **2020-21**: GDP contracted by -6.6% due to COVID-19 pandemic and lockdown measures
• **2021-22**: Strong recovery with 8.7% growth, driven by pent-up demand and vaccination rollout
• **2022-23**: Sustained growth at 7.2%, supported by domestic consumption and investment
• **2023-24**: Projected growth of 6.5-7.0%, indicating economic stabilization

## Trend Analysis
The data reveals a V-shaped recovery pattern with India emerging as one of the fastest-growing major economies. The recovery was driven by:
- Robust domestic demand and consumption
- Government stimulus measures and infrastructure spending
- Strong performance in manufacturing and services sectors
- Digital transformation acceleration

## Notable Observations
• India's recovery outpaced most major economies
• Manufacturing sector showed strong resilience
• Digital economy contribution increased significantly
• Rural-urban growth convergence improved

## Actionable Recommendations
1. **Sustain Momentum**: Continue infrastructure and manufacturing focus
2. **Digital Push**: Accelerate digital transformation initiatives
3. **Skill Development**: Invest in workforce upskilling for emerging sectors
4. **Export Promotion**: Leverage manufacturing capabilities for global markets`,
      sql_used: "SELECT year, gdp_growth_rate FROM economic_indicators WHERE indicator = 'GDP Growth' AND year BETWEEN 2020 AND 2023 ORDER BY year",
      data_preview: {
        columns: ["Year", "GDP Growth Rate (%)", "Economic Phase"],
        rows: [
          ["2020-21", "-6.6", "Pandemic Contraction"],
          ["2021-22", "8.7", "Strong Recovery"],
          ["2022-23", "7.2", "Sustained Growth"],
          ["2023-24", "6.8", "Stabilization"]
        ]
      },
      viz: {
        mark: "line",
        encoding: {
          x: { field: "Year", type: "nominal" },
          y: { field: "GDP Growth Rate (%)", type: "quantitative" }
        },
        data: { values: "__INLINE_DATA__" }
      },
      doc_citations: ["Ministry of Statistics and Programme Implementation", "Reserve Bank of India Economic Survey"],
      filters_applied: {
        time: { from: "2020-01-01", to: "2023-12-31" },
        extra: { category: "Economic" }
      },
      disclaimers: ["Data based on official government estimates", "2023-24 figures are projections"]
    }
  },
  {
    id: "inflation-analysis",
    question: "Show me the retail inflation rate trends and what's driving the changes?",
    category: "Economic",
    description: "Analyze inflation patterns and underlying factors",
    response: {
      insight_text: `## Executive Summary
India's retail inflation, measured by Consumer Price Index (CPI), has exhibited significant volatility with distinct phases of moderation and acceleration over the past decade.

## Key Findings
• **2019-2020**: Inflation averaged 4.8%, within RBI's target range of 2-6%
• **2021-2022**: Sharp spike to 6.2% due to supply chain disruptions and commodity price increases
• **2022-2023**: Peak inflation at 6.7% driven by global energy prices and food supply constraints
• **2023-2024**: Gradual moderation to 5.4% through monetary policy and supply-side measures

## Trend Analysis
The inflation trajectory shows three distinct phases:
1. **Pre-pandemic stability** (2019-2020): Well-anchored expectations
2. **Supply shock period** (2021-2022): External factors driving prices
3. **Policy response phase** (2022-2024): Gradual disinflation through coordinated measures

## Notable Observations
• Food inflation remains the primary driver, contributing 50-60% to headline inflation
• Core inflation (excluding food and fuel) has been more stable
• Rural-urban inflation differential has narrowed
• Seasonal patterns in food prices remain significant

## Actionable Recommendations
1. **Supply Chain Resilience**: Strengthen agricultural supply chains
2. **Price Monitoring**: Enhanced real-time price surveillance systems
3. **Policy Coordination**: Better alignment between monetary and fiscal policies
4. **Consumer Protection**: Targeted support for vulnerable population segments`,
      sql_used: "SELECT month, cpi_inflation, food_inflation, fuel_inflation FROM inflation_data WHERE year BETWEEN 2019 AND 2024 ORDER BY month",
      data_preview: {
        columns: ["Month", "CPI Inflation (%)", "Food Inflation (%)", "Fuel Inflation (%)"],
        rows: [
          ["Jan 2023", "6.5", "5.9", "8.2"],
          ["Feb 2023", "6.4", "5.9", "8.1"],
          ["Mar 2023", "6.7", "6.2", "8.8"],
          ["Apr 2023", "6.2", "5.8", "7.8"]
        ]
      },
      viz: {
        mark: "line",
        encoding: {
          x: { field: "Month", type: "temporal" },
          y: { field: "CPI Inflation (%)", type: "quantitative" }
        },
        data: { values: "__INLINE_DATA__" }
      },
      doc_citations: ["Ministry of Consumer Affairs", "Reserve Bank of India", "Labour Bureau"],
      filters_applied: {
        time: { from: "2019-01-01", to: "2024-12-31" },
        extra: { category: "Economic" }
      },
      disclaimers: ["Data based on official CPI calculations", "Monthly variations may be seasonal"]
    }
  },
  {
    id: "infrastructure-pmgsy",
    question: "What's the progress of PMGSY road development across different states?",
    category: "Infrastructure",
    description: "Analyze rural road connectivity development progress",
    response: {
      insight_text: `## Executive Summary
The Pradhan Mantri Gram Sadak Yojana (PMGSY) has significantly improved rural connectivity across India, with substantial progress in road construction and bridge development.

## Key Findings
• **Total Roads Sanctioned**: 7.8 lakh km across 36 states/UTs
• **Roads Completed**: 6.9 lakh km (88.5% completion rate)
• **Bridges Sanctioned**: 12,500+ critical river crossings
• **Investment**: ₹2.5 lakh crore allocated for rural connectivity

## Trend Analysis
State-wise performance shows:
- **Top Performers**: Madhya Pradesh, Rajasthan, Uttar Pradesh
- **Emerging States**: Bihar, Jharkhand, Odisha showing accelerated progress
- **North Eastern States**: Special focus areas with dedicated funding
- **Completion Rates**: 15 states achieved 90%+ completion

## Notable Observations
• Rural road density improved from 0.8 km/1000 people to 1.2 km/1000 people
• Last-mile connectivity enhanced in 95% of eligible habitations
• Digital monitoring systems improved transparency and accountability
• Women's mobility and economic participation increased significantly

## Actionable Recommendations
1. **Accelerate Completion**: Focus on remaining 11.5% of sanctioned roads
2. **Quality Maintenance**: Implement robust maintenance protocols
3. **Technology Integration**: Deploy smart monitoring and IoT solutions
4. **Last-Mile Connectivity**: Prioritize unconnected habitations`,
      sql_used: "SELECT state, roads_sanctioned, roads_completed, completion_percentage FROM pmgsy_progress ORDER BY completion_percentage DESC",
      data_preview: {
        columns: ["State", "Roads Sanctioned (km)", "Roads Completed (km)", "Completion (%)"],
        rows: [
          ["Madhya Pradesh", "45,000", "42,500", "94.4"],
          ["Rajasthan", "38,000", "35,200", "92.6"],
          ["Uttar Pradesh", "52,000", "47,800", "91.9"],
          ["Bihar", "28,000", "24,500", "87.5"]
        ]
      },
      viz: {
        mark: "bar",
        encoding: {
          x: { field: "State", type: "nominal" },
          y: { field: "Completion (%)", type: "quantitative" }
        },
        data: { values: "__INLINE_DATA__" }
      },
      doc_citations: ["Ministry of Rural Development", "National Rural Roads Development Agency"],
      filters_applied: {
        extra: { category: "Infrastructure" }
      },
      disclaimers: ["Data as of latest available reports", "Progress varies by terrain and accessibility"]
    }
  },
  {
    id: "education-literacy",
    question: "How has literacy improved across different states and what are the gender gaps?",
    category: "Social",
    description: "Analyze educational progress and gender equality in literacy",
    response: {
      insight_text: `## Executive Summary
India has made significant strides in literacy improvement, with notable progress in reducing gender gaps and achieving near-universal primary education access.

## Key Findings
• **National Literacy Rate**: Improved from 74% (2011) to 82% (2023)
• **Gender Gap Reduction**: Female literacy increased from 65% to 78%
• **State Variations**: Kerala leads at 96%, while some states still below 70%
• **Rural-Urban Divide**: Gap reduced from 20% to 15% over the decade

## Trend Analysis
Literacy improvement patterns show:
- **High Performers**: Kerala, Mizoram, Tripura maintaining 90%+ rates
- **Fast Improvers**: Bihar, Jharkhand, Rajasthan showing 15-20% growth
- **Gender Convergence**: Female literacy growing 1.5x faster than male
- **Age Group Progress**: 15-24 age group achieving 90%+ literacy

## Notable Observations
• Digital literacy programs accelerated during COVID-19
• Women's self-help groups contributed to adult literacy
• Mobile-based learning increased accessibility in remote areas
• Vocational training integration improved practical skills

## Actionable Recommendations
1. **Target Low-Performing States**: Focus on Bihar, Jharkhand, Rajasthan
2. **Digital Literacy**: Expand technology-enabled learning programs
3. **Adult Education**: Strengthen continuing education initiatives
4. **Quality Focus**: Shift from quantity to quality of education`,
      sql_used: "SELECT state, overall_literacy, male_literacy, female_literacy, gender_gap FROM literacy_data WHERE year = 2023 ORDER BY overall_literacy DESC",
      data_preview: {
        columns: ["State", "Overall Literacy (%)", "Male Literacy (%)", "Female Literacy (%)", "Gender Gap (%)"],
        rows: [
          ["Kerala", "96.2", "97.4", "95.1", "2.3"],
          ["Mizoram", "91.3", "93.7", "89.4", "4.3"],
          ["Tripura", "87.8", "92.2", "83.5", "8.7"],
          ["Goa", "87.4", "92.8", "81.8", "11.0"]
        ]
      },
      viz: {
        mark: "bar",
        encoding: {
          x: { field: "State", type: "nominal" },
          y: { field: "Overall Literacy (%)", type: "quantitative" }
        },
        data: { values: "__INLINE_DATA__" }
      },
      doc_citations: ["Ministry of Education", "National Sample Survey Office", "Census of India"],
      filters_applied: {
        extra: { category: "Social" }
      },
      disclaimers: ["Data based on latest available surveys", "State-wise variations exist due to socio-economic factors"]
    }
  },
  {
    id: "environmental-air-quality",
    question: "What's the air quality trend in major Indian cities and what factors influence it?",
    category: "Environmental",
    description: "Analyze air quality patterns and environmental factors",
    response: {
      insight_text: `## Executive Summary
Air quality in major Indian cities has shown mixed trends with seasonal variations, influenced by industrial activity, vehicular emissions, and agricultural practices.

## Key Findings
• **Delhi NCR**: AQI improved from 300+ (2020) to 180 (2023) through policy interventions
• **Mumbai**: Moderate improvement with AQI ranging 120-180 across seasons
• **Bangalore**: Best performing metro with AQI 80-120 range
• **Seasonal Patterns**: Winter months show 40-60% higher pollution levels

## Trend Analysis
Air quality improvements driven by:
- **Policy Measures**: BS-VI fuel standards, electric vehicle promotion
- **Industrial Controls**: Emission norms, monitoring systems
- **Green Initiatives**: Tree plantation, public transport expansion
- **Public Awareness**: Citizen participation in pollution control

## Notable Observations
• PM2.5 levels reduced by 25-30% in most cities
• Diwali celebrations still cause temporary spikes
• Construction activities contribute 20-25% to urban pollution
• Agricultural burning affects northern cities during harvest seasons

## Actionable Recommendations
1. **Emission Standards**: Strict enforcement of vehicle and industrial norms
2. **Green Infrastructure**: Expand urban forests and green corridors
3. **Public Transport**: Accelerate electric vehicle adoption
4. **Monitoring**: Real-time air quality monitoring and public alerts`,
      sql_used: "SELECT city, month, aqi_value, pm25_level, air_quality_category FROM air_quality_data WHERE year = 2023 ORDER BY city, month",
      data_preview: {
        columns: ["City", "Month", "AQI Value", "PM2.5 (μg/m³)", "Category"],
        rows: [
          ["Delhi", "Jan 2023", "285", "125", "Poor"],
          ["Delhi", "Feb 2023", "245", "105", "Poor"],
          ["Mumbai", "Jan 2023", "165", "75", "Moderate"],
          ["Mumbai", "Feb 2023", "145", "65", "Moderate"]
        ]
      },
      viz: {
        mark: "line",
        encoding: {
          x: { field: "Month", type: "temporal" },
          y: { field: "AQI Value", type: "quantitative" },
          color: { field: "City", type: "nominal" }
        },
        data: { values: "__INLINE_DATA__" }
      },
      doc_citations: ["Central Pollution Control Board", "Ministry of Environment", "State Pollution Control Boards"],
      filters_applied: {
        time: { from: "2020-01-01", to: "2023-12-31" },
        extra: { category: "Environmental" }
      },
      disclaimers: ["AQI values are daily averages", "Seasonal variations are significant", "Data based on monitoring station readings"]
    }
  }
];

export const getDemoQuestion = (id: string): DemoQuestion | undefined => {
  return demoQuestions.find(q => q.id === id);
};

export const getRandomDemoQuestion = (): DemoQuestion => {
  const randomIndex = Math.floor(Math.random() * demoQuestions.length);
  return demoQuestions[randomIndex];
};
