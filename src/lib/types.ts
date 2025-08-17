export interface TimeFilter {
  from: string | null;
  to: string | null;
}

export interface PlaceFilter {
  ward: string | null;
  zone: string | null;
}

export interface ExtraFilter {
  category: string | null;
}

export interface Filters {
  time: TimeFilter;
  place: PlaceFilter;
  extra: ExtraFilter;
}

export interface DataPreview {
  columns: string[];
  rows: any[][];
}

export interface VegaLiteSpec {
  type: 'vega-lite';
  spec: any;
}

export interface DocCitation {
  title: string;
  url: string;
  excerpt: string;
}

export interface InsightResponse {
  insight_text: string;
  sql_used: string;
  data_preview: DataPreview;
  viz: VegaLiteSpec;
  doc_citations: DocCitation[];
  filters_applied: Filters;
  disclaimers: string[];
}

export interface InsightRequest {
  prompt: string;
  filters: Filters;
}

export interface HistoryItem {
  id: string;
  prompt: string;
  filters: Filters;
  createdAt: Date;
  response?: InsightResponse;
}

// Government Dataset Types
export interface GovernmentDataset {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  geographic_level: string;
  time_granularity: string;
  update_frequency: string | null;
  source_department: string | null;
  last_updated: string | null;
  is_active: boolean;
  indicators_count: number;
  supported_formats: string[] | null;
}

export interface DatasetCategory {
  categories: string[];
  total: number;
}

export interface DatasetSearchResult {
  query: string;
  category: string | null;
  total: number;
  datasets: GovernmentDataset[];
}

export interface DatasetIndicator {
  id: number;
  field_name: string;
  display_name: string;
  data_type: string;
  unit: string | null;
  description: string | null;
  is_filterable: boolean;
  is_measure: boolean;
}

export interface DataSource {
  id: number;
  source_type: string;
  source_url: string | null;
  last_sync: string | null;
  sync_status: string;
  records_count: number | null;
}

export interface DatasetDetails extends GovernmentDataset {
  api_endpoint: string;
  indicators: DatasetIndicator[];
  data_sources: DataSource[];
}