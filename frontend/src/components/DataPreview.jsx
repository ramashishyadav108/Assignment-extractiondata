import React, { useEffect, useState } from 'react';
import { getJobStatus } from '../services/api';
import ExcelSheetViewer from './ExcelSheetViewer';
import '../styles/DataPreview.css';

const DataPreview = ({ jobId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('excel'); // 'excel' or 'table'

  console.log('DataPreview rendered with jobId:', jobId);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('Fetching data for job:', jobId);
        
        // Use status endpoint which now includes preview_data
        const status = await getJobStatus(jobId);
        console.log('Status received:', status);
        
        // Set data from either preview_data or extracted_data
        const dataToShow = {
          preview_data: status.preview_data,
          extracted_data: status.extracted_data,
          template_id: status.template_id || 'Unknown'
        };
        
        console.log('Data to show:', dataToShow);
        setData(dataToShow);
        setError(null);
      } catch (err) {
        console.error('Error fetching extraction results:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load extraction results');
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

  if (!data || (!data.extracted_data && !data.preview_data)) {
    return (
      <div className="data-preview-container">
        <div className="warning-message">
          ⚠️ No extracted data found
          <p style={{ fontSize: '14px', marginTop: '10px' }}>
            The extraction may still be processing or no data was extracted from the PDF.
          </p>
        </div>
      </div>
    );
  }

  const renderDataTable = () => {
    // Support both extracted_data (array) and preview_data (object)
    let extractedItems;
    let displayFormat = 'standard';
    
    if (data.preview_data) {
      // Handle preview_data format from accurate extraction
      // This has fund_summary and portfolio_companies_sample
      displayFormat = 'enhanced';
      extractedItems = [data.preview_data];
    } else if (Array.isArray(data.extracted_data)) {
      extractedItems = data.extracted_data;
    } else if (data.extracted_data) {
      extractedItems = [data.extracted_data];
    } else {
      extractedItems = [];
    }
    
    if (extractedItems.length === 0) {
      return <p>No data to display</p>;
    }
    
    // Enhanced display for accurate extraction
    if (displayFormat === 'enhanced' && extractedItems[0].fund_summary) {
      return renderEnhancedPreview(extractedItems[0]);
    }
    
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

  const renderEnhancedPreview = (previewData) => {
    const { fund_summary, portfolio_companies_sample, portfolio_companies_count, source_file, extraction_method } = previewData;
    
    return (
      <div className="enhanced-preview">
        {source_file && (
          <div className="source-info">
            <strong>Source File:</strong> {source_file}
          </div>
        )}
        {extraction_method && (
          <div className="extraction-info">
            <strong>Extraction Method:</strong> {extraction_method}
          </div>
        )}
        
        {/* Fund Summary Section */}
        {fund_summary && (
          <div className="preview-section">
            <h4>📊 Fund Summary ({Object.keys(fund_summary).length} fields extracted)</h4>
            <table className="vertical-data-table">
              <thead>
                <tr>
                  <th className="field-header">Field</th>
                  <th className="value-header">Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(fund_summary).map(([key, value]) => (
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
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Portfolio Companies Section */}
        {portfolio_companies_sample && portfolio_companies_sample.length > 0 && (
          <div className="preview-section">
            <h4>🏢 Portfolio Companies ({portfolio_companies_count || portfolio_companies_sample.length} total, showing {portfolio_companies_sample.length} sample)</h4>
            {portfolio_companies_sample.map((company, idx) => (
              <div key={idx} className="company-card">
                <h5>Company {idx + 1}: {company.Company || 'Unnamed'}</h5>
                <table className="vertical-data-table">
                  <tbody>
                    {Object.entries(company).map(([key, value]) => {
                      if (value === null || value === undefined) return null;
                      return (
                        <tr key={key}>
                          <td className="field-cell">{key}</td>
                          <td className="value-cell">{formatCellValue(value)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        )}
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
          {data.extracted_data && Array.isArray(data.extracted_data) && (
            <span className="info-badge">
              {data.extracted_data.length} Record{data.extracted_data.length !== 1 ? 's' : ''}
            </span>
          )}
          {data.preview_data && (
            <>
              <span className="info-badge">
                {data.preview_data.portfolio_companies_count || 0} Companies Extracted
              </span>
              <span className="info-badge">
                {Object.keys(data.preview_data.fund_summary || {}).length} Fund Fields
              </span>
            </>
          )}
          <span className="info-badge">
            Template: {data.template_id || 'Accurate Extraction'}
          </span>
        </div>
        <div className="view-mode-toggle">
          <button 
            className={`toggle-btn ${viewMode === 'excel' ? 'active' : ''}`}
            onClick={() => setViewMode('excel')}
          >
            📊 Excel View
          </button>
          <button 
            className={`toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
          >
            📋 Table View
          </button>
        </div>
      </div>
      
      {viewMode === 'excel' ? (
        <ExcelSheetViewer data={data} />
      ) : (
        renderDataTable()
      )}
    </div>
  );
};

export default DataPreview;
