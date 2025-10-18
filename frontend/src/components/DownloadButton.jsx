import React from 'react';
import { downloadResult } from '../services/api';

const DownloadButton = ({ jobId, disabled }) => {
  const handleDownload = () => {
    window.location.href = downloadResult(jobId);
  };

  return (
    <button
      onClick={handleDownload}
      disabled={disabled}
      className="download-btn"
    >
      <svg
        className="download-icon"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      Download Excel File
    </button>
  );
};

export default DownloadButton;
