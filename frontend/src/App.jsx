import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import TemplateSelector from './components/TemplateSelector';
import ExtractionProgress from './components/ExtractionProgress';
import DownloadButton from './components/DownloadButton';
import DataPreview from './components/DataPreview';
import { uploadFiles } from './services/api';
import './App.css';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('template_1');
  const [jobId, setJobId] = useState(null);
  const [extractionStatus, setExtractionStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleFilesSelected = (files) => {
    setSelectedFiles(files);
    setError(null);
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
  };

  const handleStartExtraction = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one PDF file');
      return;
    }

    if (!selectedTemplate) {
      setError('Please select a template');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await uploadFiles(selectedFiles, selectedTemplate);
      setJobId(response.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setIsProcessing(false);
    }
  };

  const handleExtractionComplete = (status) => {
    setExtractionStatus('completed');
    setIsProcessing(false);
  };

  const handleExtractionError = (errors) => {
    setError(errors.join(', '));
    setExtractionStatus('failed');
    setIsProcessing(false);
  };

  const handleReset = () => {
    setSelectedFiles([]);
    setSelectedTemplate('template_1');
    setJobId(null);
    setExtractionStatus(null);
    setIsProcessing(false);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📄 PDF Data Extraction System</h1>
        <p>Extract structured data from PDF documents using AI</p>
      </header>

      <main className="app-main">
        {!jobId ? (
          <div className="upload-section">
            <FileUpload
              onFilesSelected={handleFilesSelected}
              disabled={isProcessing}
            />

            <TemplateSelector
              selectedTemplate={selectedTemplate}
              onTemplateSelect={handleTemplateSelect}
              disabled={isProcessing}
            />

            {error && (
              <div className="error-message">
                <svg
                  className="error-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {error}
              </div>
            )}

            <button
              onClick={handleStartExtraction}
              disabled={selectedFiles.length === 0 || !selectedTemplate || isProcessing}
              className="start-btn"
            >
              {isProcessing ? 'Starting...' : 'Start Extraction'}
            </button>
          </div>
        ) : (
          <div className="extraction-section">
            <ExtractionProgress
              jobId={jobId}
              onComplete={handleExtractionComplete}
              onError={handleExtractionError}
            />

            {extractionStatus === 'completed' && (
              <div className="success-section">
                <DataPreview jobId={jobId} />
                <div className="action-buttons">
                  <DownloadButton jobId={jobId} />
                </div>
              </div>
            )}

            <button onClick={handleReset} className="reset-btn">
              Extract Another Document
            </button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by LLM Technology | Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
