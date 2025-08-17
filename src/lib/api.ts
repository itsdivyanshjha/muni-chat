import { InsightRequest, InsightResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  async getInsight(payload: InsightRequest): Promise<InsightResponse> {
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
  },

  async getSchema(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/schema`);
    
    if (!response.ok) {
      throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
    }

    return await response.json();
  },

  async getGovernmentDatasets(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/datasets`);
    
    if (!response.ok) {
      throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
    }

    return await response.json();
  },

  async getDatasetCategories(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/datasets/categories`);
    
    if (!response.ok) {
      throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
    }

    return await response.json();
  },

  async searchDatasets(query: string, category?: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/datasets/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, category }),
    });

    if (!response.ok) {
      throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
    }

    return await response.json();
  },

  async getDatasetDetails(slug: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/datasets/${slug}`);
    
    if (!response.ok) {
      throw new ApiError(`HTTP error! status: ${response.status}`, response.status);
    }

    return await response.json();
  }
};