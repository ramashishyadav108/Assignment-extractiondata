import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUpload from './components/FileUpload';
import ProcessingPage from './components/ProcessingPage';
import ResultsPage from './components/ResultsPage';
import HistoryPage from './components/HistoryPage';
import CompareXLSX from './components/CompareXLSX';
import { uploadFiles } from './services/api';
import './App.css';

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [outputFilename, setOutputFilename] = useState(null);
  const [error, setError] = useState(null);
  const [processingComplete, setProcessingComplete] = useState(false);

  // Determine current page from URL
  const getCurrentPage = () => {
    const path = location.pathname;
    if (path === '/') return 'upload';
    if (path === '/processing') return 'processing';
    if (path === '/results') return 'results';
    if (path === '/history') return 'history';
    if (path === '/compare') return 'compare';
    if (path === '/compare-output') return 'compare';
    return 'upload';
  };

  const currentPage = getCurrentPage();

  const handleFilesSelected = (files) => {
    setSelectedFiles(files);
    setError(null);
    if (files.length > 0) {
      toast.success(`${files.length} file${files.length > 1 ? 's' : ''} selected`);
    }
  };

  const handleProgressComplete = (progress) => {
    if (progress === 100) {
      setProcessingComplete(true);
      toast.success('Extraction completed successfully! 🎉');
      // Wait a moment at 100% before showing results
      setTimeout(() => {
        navigate('/results');
      }, 800);
    }
  };

  const handleStartExtraction = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one PDF file');
      setError('Please select at least one PDF file');
      return;
    }

    toast.loading('Starting extraction...', { id: 'extraction' });
    navigate('/processing');
    setError(null);
    setProcessingComplete(false);

    try {
      // The new backend returns results immediately (synchronous)
      const response = await uploadFiles(selectedFiles, 'fund_report_v1');
      
      if (response.success) {
        // Store the output filename
        setOutputFilename(response.output_file);
        toast.success('File uploaded successfully!', { id: 'extraction' });
        // Results will be shown after progress reaches 100%
      } else {
        throw new Error(response.message || 'Extraction failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed. Please try again.';
      toast.error(errorMessage, { id: 'extraction' });
      setError(errorMessage);
      navigate('/');
    }
  };

  const handleStartNew = () => {
    navigate('/');
    setSelectedFiles([]);
    setOutputFilename(null);
    setError(null);
    setProcessingComplete(false);
    toast.success('Ready for new extraction');
  };

  const handleNavigateHistory = () => {
    navigate('/history');
  };

  const handleNavigateCompare = () => {
    navigate('/compare');
    toast.success('Select two Excel files to compare');
  };

  const handleCompareOutput = () => {
    navigate('/compare-output');
    toast.success('Select expected output file to compare');
  };

  const handleBackToResults = () => {
    navigate('/results');
  };

  const handleViewHistoryFile = (filename) => {
    setOutputFilename(filename);
    navigate('/results');
    toast.success('Loading extraction results');
  };

  return (
    <div className="app">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: 'var(--surface)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            padding: '16px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
          },
          success: {
            iconTheme: {
              primary: 'var(--success-color)',
              secondary: 'white',
            },
          },
          error: {
            iconTheme: {
              primary: 'var(--error-color)',
              secondary: 'white',
            },
          },
          loading: {
            iconTheme: {
              primary: 'var(--primary-color)',
              secondary: 'white',
            },
          },
        }}
      />
      
      <Header 
        currentPage={currentPage} 
        onNavigateHome={handleStartNew}
        onNavigateHistory={handleNavigateHistory}
        onNavigateCompare={handleNavigateCompare}
      />

      <main className="app-main">
        <Routes>
          {/* Upload Page */}
          <Route path="/" element={
            <div className="upload-section">
              <FileUpload
                onFilesSelected={handleFilesSelected}
                disabled={false}
              />

              <button
                onClick={handleStartExtraction}
                disabled={selectedFiles.length === 0}
                className="start-btn"
              >
                Extract Data
              </button>
            </div>
          } />

          {/* Processing Page */}
          <Route path="/processing" element={
            <ProcessingPage 
              fileName={selectedFiles[0]?.name} 
              onProgressUpdate={handleProgressComplete}
            />
          } />

          {/* Results Page */}
          <Route path="/results" element={
            <ResultsPage 
              filename={outputFilename} 
              onStartNew={handleStartNew}
              onCompare={handleCompareOutput}
            />
          } />

          {/* History Page */}
          <Route path="/history" element={
            <HistoryPage onViewFile={handleViewHistoryFile} />
          } />

          {/* Compare XLSX Page (Dual mode - from header) */}
          <Route path="/compare" element={
            <CompareXLSX mode="dual" />
          } />

          {/* Compare Output Page (Single mode - from results) */}
          <Route path="/compare-output" element={
            <CompareXLSX 
              mode="single" 
              outputFile={outputFilename}
              onBack={handleBackToResults}
            />
          } />

          {/* Catch all other routes and redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

export default App;
