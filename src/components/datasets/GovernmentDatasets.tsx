import React, { useState, useEffect } from 'react';

export function GovernmentDatasets() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('GovernmentDatasets: Component mounted');
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      console.log('GovernmentDatasets: Loading datasets...');
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/datasets');
      console.log('GovernmentDatasets: Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('GovernmentDatasets: Data received:', data);
      
      setDatasets(data.datasets || []);
    } catch (error) {
      console.error('GovernmentDatasets: Error loading datasets:', error);
      setError(error instanceof Error ? error.message : 'Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  console.log('GovernmentDatasets: Render state:', { loading, error, datasetsCount: datasets.length });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-lg">Loading government datasets...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="text-lg text-red-600 mb-4">Error loading datasets</div>
        <div className="text-sm text-gray-600 mb-4">{error}</div>
        <button 
          onClick={loadDatasets}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Government Datasets</h3>
        <p className="text-sm text-gray-600">Found {datasets.length} datasets</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {datasets.map((dataset) => (
          <div key={dataset.id} className="p-4 border rounded-lg bg-white">
            <h4 className="font-semibold mb-2">{dataset.title}</h4>
            <p className="text-sm text-gray-600 mb-2">{dataset.category}</p>
            <p className="text-xs text-gray-500">
              Indicators: {dataset.indicators_count} | 
              Geographic: {dataset.geographic_level}
            </p>
          </div>
        ))}
      </div>

      {datasets.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No datasets available.
        </div>
      )}
    </div>
  );
}
