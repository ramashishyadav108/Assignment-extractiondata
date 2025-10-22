import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { getExtractionHistory, downloadFile } from '../services/api';
import '../styles/HistoryPage.css';

const HistoryPage = ({ onViewFile }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getExtractionHistory();
      setHistory(data.results || []);
      if (data.results && data.results.length > 0) {
        toast.success(`Loaded ${data.results.length} extraction${data.results.length > 1 ? 's' : ''}`);
      }
    } catch (err) {
      console.error('Error fetching history:', err);
      const errorMsg = 'Failed to load extraction history. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (filename) => {
    try {
      toast.loading('Preparing download...', { id: 'download' });
      await downloadFile(filename);
      toast.success('Download started!', { id: 'download' });
    } catch (err) {
      console.error('Error downloading file:', err);
      toast.error('Failed to download file. Please try again.', { id: 'download' });
    }
  };

  const handleView = (filename) => {
    if (onViewFile) {
      onViewFile(filename);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (seconds) => {
    if (!seconds) return 'N/A';
    return `${seconds.toFixed(2)}s`;
  };

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = history.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(history.length / itemsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  if (loading) {
    return (
      <div className="history-page">
        <div className="history-container">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading extraction history...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <div className="history-container">
          <div className="error-message">
            <svg className="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
          <button className="retry-button" onClick={fetchHistory}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="history-container">
        <div className="history-header">
          <h1>Extraction History</h1>
          <p className="history-subtitle">
            View and download all your previously extracted PDF files
          </p>
        </div>

        {history.length === 0 ? (
          <div className="empty-state">
            <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3>No extraction history yet</h3>
            <p>Upload and extract your first PDF to see it here</p>
          </div>
        ) : (
          <>
            <div className="history-stats">
              <div className="stat-card">
                <div className="stat-value">{history.length}</div>
                <div className="stat-label">Total Extractions</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {history.reduce((sum, item) => sum + (item.total_sheets_generated || 0), 0)}
                </div>
                <div className="stat-label">Total Sheets Generated</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {(history.reduce((sum, item) => sum + (item.processing_time || 0), 0) / history.length).toFixed(2)}s
                </div>
                <div className="stat-label">Avg Processing Time</div>
              </div>
            </div>

            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Original File</th>
                    <th>Extraction Date</th>
                    <th>Processing Time</th>
                    <th>Characters</th>
                    <th>Sheets</th>
                    <th>Model</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((item) => (
                    <tr key={item.id}>
                      <td className="filename-cell">
                        <svg className="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="filename">{item.original_filename || 'Unknown'}</span>
                      </td>
                      <td>{formatDate(item.extraction_timestamp)}</td>
                      <td>{formatTime(item.processing_time)}</td>
                      <td>{(item.total_characters_extracted || 0).toLocaleString()}</td>
                      <td>{item.total_sheets_generated || 0}</td>
                      <td className="model-cell">{item.gemini_model_used || 'N/A'}</td>
                      <td>
                        <div className="action-buttons">
                          <button
                            className="view-btn"
                            onClick={() => handleView(item.excel_filename)}
                            title="View Excel file"
                          >
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            View
                          </button>
                          <button
                            className="download-btn"
                            onClick={() => handleDownload(item.excel_filename)}
                            title="Download Excel file"
                          >
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            Download
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="pagination-btn"
                  onClick={() => paginate(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Previous
                </button>
                
                <div className="pagination-info">
                  Page {currentPage} of {totalPages}
                </div>

                <button
                  className="pagination-btn"
                  onClick={() => paginate(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
