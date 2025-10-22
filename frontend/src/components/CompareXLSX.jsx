import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import toast from 'react-hot-toast';
import '../styles/CompareXLSX.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const CompareXLSX = ({ mode = 'dual', outputFile = null, onBack }) => {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedSheet, setSelectedSheet] = useState(0);

  // Normalize value for comparison - treat empty, null, 0, "Not found", "Null" as equivalent
  const normalizeValue = (value) => {
    if (value === null || value === undefined) return null;
    
    const strValue = String(value).trim().toLowerCase();
    
    // List of values to consider as "empty"
    const emptyValues = ['', '0', 'not found', 'null', 'n/a', 'na', 'none', '-'];
    
    if (emptyValues.includes(strValue)) {
      return null;
    }
    
    return value;
  };

  // Check if two values are equivalent
  const areValuesEquivalent = (val1, val2) => {
    const norm1 = normalizeValue(val1);
    const norm2 = normalizeValue(val2);
    
    // Both are considered "empty"
    if (norm1 === null && norm2 === null) return true;
    
    // One is empty and other is not
    if (norm1 === null || norm2 === null) return false;
    
    // Compare as strings (case insensitive)
    return String(norm1).toLowerCase().trim() === String(norm2).toLowerCase().trim();
  };

  const handleFileChange = (event, fileNumber) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validExtensions = ['.xlsx', '.xls'];
      const fileName = file.name.toLowerCase();
      const isValidType = validExtensions.some(ext => fileName.endsWith(ext));
      
      if (!isValidType) {
        toast.error(`Invalid file type. Please upload only Excel files (.xlsx or .xls)`, {
          duration: 4000,
          icon: '📊'
        });
        // Clear the file input
        event.target.value = '';
        return;
      }

      // Validate file size (max 10MB for Excel files)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        toast.error(`File is too large. Maximum size is 10MB.`, {
          duration: 4000,
          icon: '⚠️'
        });
        // Clear the file input
        event.target.value = '';
        return;
      }

      if (fileNumber === 1) {
        setFile1(file);
      } else {
        setFile2(file);
      }
      setError(null);
    }
  };

  const readExcelFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          
          const sheets = {};
          workbook.SheetNames.forEach(sheetName => {
            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
            sheets[sheetName] = jsonData;
          });
          
          resolve({
            sheetNames: workbook.SheetNames,
            sheets: sheets
          });
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  };

  const fetchOutputFile = async (filename) => {
    try {
      const response = await fetch(`${API_BASE_URL}/download/${filename}`);
      if (!response.ok) throw new Error('Failed to fetch output file');
      return await response.blob();
    } catch (err) {
      throw new Error('Could not load output file: ' + err.message);
    }
  };

  const compareSheets = (sheet1Data, sheet2Data) => {
    const maxRows = Math.max(sheet1Data.length, sheet2Data.length);
    const maxCols = Math.max(
      ...sheet1Data.map(row => row.length),
      ...sheet2Data.map(row => row.length)
    );

    const comparison = [];
    let differences = 0;
    let matches = 0;

    for (let i = 0; i < maxRows; i++) {
      const row1 = sheet1Data[i] || [];
      const row2 = sheet2Data[i] || [];
      const compRow = [];

      for (let j = 0; j < maxCols; j++) {
        const val1 = row1[j] !== undefined ? row1[j] : '';
        const val2 = row2[j] !== undefined ? row2[j] : '';
        
        const isEqual = areValuesEquivalent(val1, val2);
        
        if (!isEqual) {
          differences++;
        } else {
          matches++;
        }

        compRow.push({
          value1: val1,
          value2: val2,
          isEqual: isEqual,
          isDifferent: !isEqual
        });
      }

      comparison.push(compRow);
    }

    return {
      data: comparison,
      stats: {
        totalCells: maxRows * maxCols,
        matches,
        differences,
        accuracy: maxRows * maxCols > 0 ? ((matches / (maxRows * maxCols)) * 100).toFixed(2) : 0
      }
    };
  };

  const handleCompare = async () => {
    setLoading(true);
    setError(null);

    try {
      let data1, data2;

      if (mode === 'single') {
        // Compare mode from results page - one file selected, one is output
        if (!file1 || !outputFile) {
          throw new Error('Please select an expected output file');
        }

        // Read selected file
        data1 = await readExcelFile(file1);

        // Fetch and read output file
        const outputBlob = await fetchOutputFile(outputFile);
        const outputFileObj = new File([outputBlob], outputFile);
        data2 = await readExcelFile(outputFileObj);

      } else {
        // Dual mode from header - both files need to be selected
        if (!file1 || !file2) {
          throw new Error('Please select both Excel files');
        }

        data1 = await readExcelFile(file1);
        data2 = await readExcelFile(file2);
      }

      // Compare all sheets
      const allComparisons = {};
      const allSheets = new Set([...data1.sheetNames, ...data2.sheetNames]);

      allSheets.forEach(sheetName => {
        const sheet1 = data1.sheets[sheetName] || [];
        const sheet2 = data2.sheets[sheetName] || [];
        allComparisons[sheetName] = compareSheets(sheet1, sheet2);
      });

      setComparison({
        sheetNames: Array.from(allSheets),
        sheets: allComparisons,
        file1Name: file1.name,
        file2Name: mode === 'single' ? outputFile : file2.name
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderComparisonTable = () => {
    if (!comparison) return null;

    // Calculate overall statistics across all sheets
    const overallStats = {
      totalCells: 0,
      matches: 0,
      differences: 0,
      accuracy: 0
    };

    Object.values(comparison.sheets).forEach(sheet => {
      overallStats.totalCells += sheet.stats.totalCells;
      overallStats.matches += sheet.stats.matches;
      overallStats.differences += sheet.stats.differences;
    });

    overallStats.accuracy = overallStats.totalCells > 0 
      ? ((overallStats.matches / overallStats.totalCells) * 100).toFixed(2) 
      : 0;

    const currentSheetName = comparison.sheetNames[selectedSheet];
    const currentComparison = comparison.sheets[currentSheetName];

    return (
      <div className="comparison-results">
        {/* Overall Comparison Stats */}
        <div className="overall-comparison">
          <h3 className="overall-title">Overall Comparison</h3>
          <div className="comparison-stats">
            <div className="stat-card match">
              <span className="stat-label">MATCHES</span>
              <span className="stat-value">{overallStats.matches}</span>
            </div>
            <div className="stat-card diff">
              <span className="stat-label">DIFFERENCES</span>
              <span className="stat-value">{overallStats.differences}</span>
            </div>
            <div className="stat-card accuracy">
              <span className="stat-label">ACCURACY</span>
              <span className="stat-value">{overallStats.accuracy}%</span>
            </div>
          </div>
        </div>

        {/* Sheet Tabs */}
        <div className="sheet-tabs">
          {comparison.sheetNames.map((sheetName, index) => (
            <button
              key={sheetName}
              className={`sheet-tab ${selectedSheet === index ? 'active' : ''}`}
              onClick={() => setSelectedSheet(index)}
            >
              {sheetName}
            </button>
          ))}
        </div>

        {/* Per-Sheet Stats */}
        <div className="comparison-stats">
          <div className="stat-card match">
            <span className="stat-label">MATCHES</span>
            <span className="stat-value">{currentComparison.stats.matches}</span>
          </div>
          <div className="stat-card diff">
            <span className="stat-label">DIFFERENCES</span>
            <span className="stat-value">{currentComparison.stats.differences}</span>
          </div>
          <div className="stat-card accuracy">
            <span className="stat-label">ACCURACY</span>
            <span className="stat-value">{currentComparison.stats.accuracy}%</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="compare-xlsx-page">
      <div className="compare-container">
        <div className="compare-header">
          <h2>
            {mode === 'single' ? '📊 Compare with Expected Output' : '📊 Compare Excel Files'}
          </h2>
          <p className="compare-description">
            {mode === 'single' 
              ? 'Upload your expected output to compare with the extracted result'
              : 'Upload two Excel files to compare their contents'
            }
          </p>
        </div>

        {/* File Upload Section */}
        <div className="file-inputs">
          <div className="file-input-group">
            <label htmlFor="file1" className="file-label">
              {mode === 'single' ? 'Expected Output File' : 'First Excel File'}
            </label>
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file1"
                onChange={(e) => handleFileChange(e, 1)}
                className="file-input"
              />
              <label htmlFor="file1" className="file-input-btn">
                {file1 ? file1.name : 'Choose File'}
              </label>
            </div>
          </div>

          {mode === 'dual' && (
            <div className="file-input-group">
              <label htmlFor="file2" className="file-label">
                Second Excel File
              </label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="file2"
                  onChange={(e) => handleFileChange(e, 2)}
                  className="file-input"
                />
                <label htmlFor="file2" className="file-input-btn">
                  {file2 ? file2.name : 'Choose File'}
                </label>
              </div>
            </div>
          )}

          {mode === 'single' && outputFile && (
            <div className="file-input-group">
              <label className="file-label">Extracted Output</label>
              <div className="output-file-display">
                <span className="output-filename">{outputFile}</span>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="compare-actions">
          <button
            onClick={handleCompare}
            disabled={loading || !file1 || (mode === 'dual' && !file2)}
            className="compare-btn"
          >
            {loading ? 'Comparing...' : 'Compare Files'}
          </button>
          {onBack && (
            <button onClick={onBack} className="back-btn">
              Back to Results
            </button>
          )}
        </div>

        {/* Comparison Results */}
        {comparison && renderComparisonTable()}
      </div>
    </div>
  );
};

export default CompareXLSX;
