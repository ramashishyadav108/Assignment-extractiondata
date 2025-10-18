import React, { useEffect, useState } from 'react';
import { getExtractionResults } from '../services/api';
import './DataPreview.css';

const DataPreview = ({ jobId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await getExtractionResults(jobId);
        setData(result);
        setError(null);
      } catch (err) {
        console.error('Error fetching extraction results:', err);
        setError(err.response?.data?.detail || 'Failed to load extraction results');
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchData();
    }
  }, [jobId]);

  if (loading) {
    return (
      <div className="data-preview-container">
        <div className="spinner"></div>
        <p>Loading extracted data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-preview-container">
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      </div>
    );
  }

  if (!data || !data.extracted_data || data.extracted_data.length === 0) {
    return (
      <div className="data-preview-container">
        <p>No data available to display</p>
      </div>
    );
  }

  const renderDataTable = () => {
    const extractedItems = data.extracted_data;
    
    // For vertical display, we'll show Field | Value for each record
    return (
      <div className="vertical-tables-container">
        {extractedItems.map((item, itemIndex) => (
          <div key={itemIndex} className="vertical-table-wrapper">
            {extractedItems.length > 1 && (
              <h4 className="record-title">
                Record {itemIndex + 1}
                {item._source_file && (
                  <span className="source-file-badge">
                    📄 {item._source_file}
                  </span>
                )}
              </h4>
            )}
            <table className="vertical-data-table">
              <thead>
                <tr>
                  <th className="field-header">Field</th>
                  <th className="value-header">Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(item).map(([key, value]) => {
                  // Skip internal fields that start with underscore
                  if (key.startsWith('_')) return null;
                  
                  return (
                    <tr key={key}>
                      <td className="field-cell">
                        {key.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                      </td>
                      <td className="value-cell">
                        {formatCellValue(value)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    );
  };

  const formatCellValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return <span className="empty-value">—</span>;
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  return (
    <div className="data-preview-container">
      <div className="data-preview-header">
        <h3>📊 Extracted Data Preview</h3>
        <div className="data-info">
          <span className="info-badge">
            {data.extracted_data.length} Record{data.extracted_data.length !== 1 ? 's' : ''}
          </span>
          <span className="info-badge">
            Template: {data.template_id}
          </span>
        </div>
      </div>
      {renderDataTable()}
    </div>
  );
};

export default DataPreview;
