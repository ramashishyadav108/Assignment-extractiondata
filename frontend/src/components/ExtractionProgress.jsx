import React, { useEffect, useState } from 'react';
import { getJobStatus } from '../services/api';

const ExtractionProgress = ({ jobId, onComplete, onError }) => {
  const [status, setStatus] = useState(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!jobId || !polling) return;

    const pollStatus = async () => {
      try {
        const data = await getJobStatus(jobId);
        setStatus(data);

        if (data.status === 'completed') {
          setPolling(false);
          onComplete(data);
        } else if (data.status === 'failed') {
          setPolling(false);
          onError(data.errors);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        setPolling(false);
        onError([error.message]);
      }
    };

    // Poll immediately
    pollStatus();

    // Then poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [jobId, polling, onComplete, onError]);

  if (!status) {
    return (
      <div className="progress-container">
        <div className="spinner"></div>
        <p>Initializing extraction...</p>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return (
          <svg className="status-icon success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="status-icon error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return <div className="spinner"></div>;
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'processing':
        return 'Extracting data...';
      case 'completed':
        return 'Extraction completed!';
      case 'failed':
        return 'Extraction failed';
      default:
        return 'Processing...';
    }
  };

  return (
    <div className="progress-container">
      <div className="status-header">
        {getStatusIcon()}
        <h3>{getStatusText()}</h3>
      </div>

      <div className="progress-info">
        <p>Files processed: {status.files_processed} / {status.total_files}</p>
        
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${status.progress}%` }}
          ></div>
        </div>
        
        <p className="progress-percentage">{status.progress.toFixed(0)}%</p>
      </div>

      {status.errors && status.errors.length > 0 && (
        <div className="error-messages">
          <h4>Errors:</h4>
          <ul>
            {status.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ExtractionProgress;
