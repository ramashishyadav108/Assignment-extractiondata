import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';
import '../styles/ExcelViewer.css';

const ExcelViewer = ({ filename }) => {
  const [workbook, setWorkbook] = useState(null);
  const [sheetNames, setSheetNames] = useState([]);
  const [activeSheet, setActiveSheet] = useState(0);
  const [sheetData, setSheetData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadExcelFile = async () => {
      try {
        setLoading(true);
        setError(null);

        const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        const response = await fetch(`${API_BASE_URL}/preview/${filename}`);
        
        if (!response.ok) {
          throw new Error('Failed to load Excel file');
        }

        const arrayBuffer = await response.arrayBuffer();
        const data = new Uint8Array(arrayBuffer);
        const wb = XLSX.read(data, { type: 'array' });
        
        setWorkbook(wb);
        setSheetNames(wb.SheetNames);
        
        // Load first sheet by default
        if (wb.SheetNames.length > 0) {
          loadSheet(wb, 0);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error loading Excel file:', err);
        setError(err.message || 'Failed to load Excel file');
        setLoading(false);
      }
    };

    if (filename) {
      loadExcelFile();
    }
  }, [filename]);

  const loadSheet = (wb, sheetIndex) => {
    const sheetName = wb.SheetNames[sheetIndex];
    const worksheet = wb.Sheets[sheetName];
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
    setSheetData(jsonData);
    setActiveSheet(sheetIndex);
  };

  const handleSheetChange = (index) => {
    if (workbook) {
      loadSheet(workbook, index);
    }
  };

  if (loading) {
    return (
      <div className="excel-viewer loading">
        <div className="spinner"></div>
        <p>Loading Excel preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="excel-viewer error">
        <p>❌ {error}</p>
      </div>
    );
  }

  if (!workbook || sheetNames.length === 0) {
    return (
      <div className="excel-viewer error">
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div className="excel-viewer">
      <div className="excel-header">
        <h3>📊 Excel Preview</h3>
        <p className="sheet-count">{sheetNames.length} sheet{sheetNames.length > 1 ? 's' : ''}</p>
      </div>

      {/* Sheet Tabs */}
      <div className="sheet-tabs">
        {sheetNames.map((name, index) => (
          <button
            key={index}
            className={`sheet-tab ${activeSheet === index ? 'active' : ''}`}
            onClick={() => handleSheetChange(index)}
          >
            {name}
          </button>
        ))}
      </div>

      {/* Sheet Content */}
      <div className="sheet-content">
        <div className="table-wrapper">
          <table className="excel-table">
            <tbody>
              {sheetData.map((row, rowIndex) => (
                <tr key={rowIndex} className={rowIndex === 0 ? 'header-row' : ''}>
                  {row.map((cell, cellIndex) => {
                    const CellTag = rowIndex === 0 ? 'th' : 'td';
                    return (
                      <CellTag key={cellIndex}>
                        {cell !== null && cell !== undefined ? String(cell) : ''}
                      </CellTag>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="excel-footer">
        <p className="info-text">
          Showing sheet: <strong>{sheetNames[activeSheet]}</strong>
          {' '}({sheetData.length} rows)
        </p>
      </div>
    </div>
  );
};

export default ExcelViewer;
