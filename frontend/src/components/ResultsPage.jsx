import React from 'react';
import ExcelViewer from './ExcelViewer';
import DownloadButton from './DownloadButton';
import '../styles/ResultsPage.css';

const ResultsPage = ({ filename, onStartNew, onCompare }) => {
  return (
    <div className="results-page">
      <div className="results-container">
        {/* Success Header */}
        <div className="success-header">
          <div className="success-animation">
            <div className="success-circle">
              <svg className="checkmark" viewBox="0 0 52 52">
                <circle className="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                <path className="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
              </svg>
            </div>
          </div>
          <h2 className="success-title">Extraction Complete! 🎉</h2>
          <p className="success-message">
            Your PDF has been successfully processed and converted to a structured Excel file.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-info">
              <div className="stat-label">Format</div>
              <div className="stat-value">Excel (.xlsx)</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✨</div>
            <div className="stat-info">
              <div className="stat-label">Quality</div>
              <div className="stat-value">AI Verified</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-info">
              <div className="stat-label">Status</div>
              <div className="stat-value">Ready</div>
            </div>
          </div>
        </div>

        {/* Excel Preview */}
        <div className="excel-preview-section">
          <ExcelViewer filename={filename} />
        </div>

        {/* Action Buttons */}
        <div className="results-actions">
          <DownloadButton jobId={filename} />
          <button onClick={onCompare} className="compare-output-btn">
            <svg className="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Compare with Expected Output
          </button>
          <button onClick={onStartNew} className="new-extraction-btn">
            <svg className="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Extract Another Document
          </button>
        </div>

        {/* Info Footer */}
        <div className="results-footer">
          <div className="footer-tip">
            <span className="tip-icon">💡</span>
            <span className="tip-text">
              Tip: You can switch between sheets using the tabs above to view all extracted data.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
