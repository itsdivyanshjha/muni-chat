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