import React, { useState } from 'react';
import '../styles/ExcelSheetViewer.css';

const ExcelSheetViewer = ({ data }) => {
  const [activeSheet, setActiveSheet] = useState(0);

  if (!data) {
    return <div className="excel-viewer-empty">No data to display</div>;
  }

  // Build sheets from the extracted data
  const sheets = buildSheets(data);

  if (sheets.length === 0) {
    return <div className="excel-viewer-empty">No sheets available</div>;
  }

  const currentSheet = sheets[activeSheet];

  return (
    <div className="excel-viewer">
      {/* Sheet Tabs */}
      <div className="excel-tabs">
        {sheets.map((sheet, index) => (
          <button
            key={index}
            className={`excel-tab ${activeSheet === index ? 'active' : ''}`}
            onClick={() => setActiveSheet(index)}
          >
            {sheet.name}
          </button>
        ))}
      </div>

      {/* Sheet Content */}
      <div className="excel-sheet">
        <div className="excel-sheet-name">{currentSheet.name}</div>
        <div className="excel-grid-container">
          <table className="excel-grid">
            <thead>
              <tr>
                {currentSheet.headers.map((header, idx) => (
                  <th key={idx}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentSheet.rows.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx}>{formatCellValue(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Build sheets from extracted data - ALWAYS show all sheets
function buildSheets(data) {
  const sheets = [];

  // Sheet 1: Doc Summary
  const docSummary = {
    'File Name': data.file_name || '—',
    'Upload Date': data.upload_date || '—',
    'Status': data.status || 'Completed',
    'Template': data.template_id || 'Accurate Extraction',
    'Total Pages': data.total_pages || '—',
    'Processing Time': data.processing_time || '—'
  };
  sheets.push({
    name: 'Doc Summary',
    headers: ['Field', 'Value'],
    rows: Object.entries(docSummary).map(([key, value]) => [key, value])
  });

  // Sheet 2: Portfolio Summary (Fund Summary)
  const fundSummary = data.preview_data?.fund_summary || data.extracted_data?.fund_summary || {};
  if (Object.keys(fundSummary).length > 0) {
    sheets.push({
      name: 'Portfolio Summary',
      headers: ['Field', 'Value'],
      rows: Object.entries(fundSummary).map(([key, value]) => [
        formatFieldName(key),
        value
      ])
    });
  } else {
    sheets.push({
      name: 'Portfolio Summary',
      headers: ['Field', 'Value'],
      rows: [['No data extracted', '—']]
    });
  }

  // Sheet 3: Schedule of Investments (Portfolio Companies)
  const companies = data.preview_data?.portfolio_companies_sample || 
                    data.extracted_data?.portfolio_companies || 
                    data.extracted_data?.schedule_of_investments || [];
  
  if (companies.length > 0) {
    const allKeys = new Set();
    companies.forEach(company => {
      Object.keys(company).forEach(key => allKeys.add(key));
    });
    
    const headers = Array.from(allKeys);
    const rows = companies.map(company => 
      headers.map(header => company[header] ?? '—')
    );

    sheets.push({
      name: 'Schedule of Investments',
      headers: headers,
      rows: rows
    });
  } else {
    sheets.push({
      name: 'Schedule of Investments',
      headers: ['Company', 'Investment Type', 'Fair Value'],
      rows: [['No companies extracted', '—', '—']]
    });
  }

  // Sheet 4: Statement of Operations
  const operations = data.extracted_data?.statement_of_operations || [];
  if (operations.length > 0) {
    const allKeys = new Set();
    operations.forEach(period => {
      Object.keys(period).forEach(key => allKeys.add(key));
    });
    
    const headers = Array.from(allKeys);
    const rows = operations.map(period => 
      headers.map(header => period[header] ?? '—')
    );

    sheets.push({
      name: 'Statement of Operations',
      headers: headers,
      rows: rows
    });
  } else {
    sheets.push({
      name: 'Statement of Operations',
      headers: ['Period', 'Total Income', 'Total Expenses', 'Net Income'],
      rows: [['No data extracted', '—', '—', '—']]
    });
  }

  // Sheet 5: Statement of Cash Flows
  const cashflows = data.extracted_data?.statement_of_cashflows || [];
  if (cashflows.length > 0) {
    const allKeys = new Set();
    cashflows.forEach(period => {
      Object.keys(period).forEach(key => allKeys.add(key));
    });
    
    const headers = Array.from(allKeys);
    const rows = cashflows.map(period => 
      headers.map(header => period[header] ?? '—')
    );

    sheets.push({
      name: 'Statement of Cashflows',
      headers: headers,
      rows: rows
    });
  } else {
    sheets.push({
      name: 'Statement of Cashflows',
      headers: ['Period', 'Operating Activities', 'Investing Activities', 'Financing Activities'],
      rows: [['No data extracted', '—', '—', '—']]
    });
  }

  // Sheet 6: PCAP Statement
  const pcap = data.extracted_data?.pcap_statement || [];
  if (pcap.length > 0) {
    const allKeys = new Set();
    pcap.forEach(period => {
      Object.keys(period).forEach(key => allKeys.add(key));
    });
    
    const headers = Array.from(allKeys);
    const rows = pcap.map(period => 
      headers.map(header => period[header] ?? '—')
    );

    sheets.push({
      name: 'PCAP Statement',
      headers: headers,
      rows: rows
    });
  } else {
    sheets.push({
      name: 'PCAP Statement',
      headers: ['Partner', 'Beginning Balance', 'Contributions', 'Distributions', 'Ending Balance'],
      rows: [['No data extracted', '—', '—', '—', '—']]
    });
  }

  // Sheet 7: Portfolio Company Profile
  sheets.push({
    name: 'Portfolio Company profile',
    headers: ['Company', 'Description', 'Website', 'Founded', 'Employees'],
    rows: [['Data not yet available', '—', '—', '—', '—']]
  });

  // Sheet 8: Portfolio Company Financials
  sheets.push({
    name: 'Portfolio Company Financials',
    headers: ['Company', 'Revenue', 'EBITDA', 'Net Income', 'Year'],
    rows: [['Data not yet available', '—', '—', '—', '—']]
  });

  // Sheet 9: Footnotes
  const footnotes = data.extracted_data?.footnotes || [];
  if (footnotes.length > 0) {
    sheets.push({
      name: 'Footnotes',
      headers: ['Number', 'Text'],
      rows: footnotes.map(fn => [fn.number || '—', fn.text || '—'])
    });
  } else {
    sheets.push({
      name: 'Footnotes',
      headers: ['Number', 'Text'],
      rows: [['No footnotes extracted', '—']]
    });
  }

  // Sheet 10: Reference Values
  sheets.push({
    name: 'Reference Values',
    headers: ['Metric', 'Definition', 'Formula'],
    rows: [
      ['DPI', 'Distributions to Paid-In Capital', 'Total Distributions / Total Paid-In Capital'],
      ['RVPI', 'Residual Value to Paid-In Capital', 'NAV / Total Paid-In Capital'],
      ['TVPI', 'Total Value to Paid-In Capital', '(Distributions + NAV) / Total Paid-In Capital'],
      ['IRR', 'Internal Rate of Return', 'Annualized effective compound return rate'],
      ['MOIC', 'Multiple on Invested Capital', 'Total Value / Invested Capital']
    ]
  });

  return sheets;
}

// Format field name to be more readable
function formatFieldName(fieldName) {
  return fieldName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Format cell value
function formatCellValue(value) {
  if (value === null || value === undefined) {
    return '—';
  }
  
  if (typeof value === 'number') {
    // Format large numbers with commas
    if (Math.abs(value) >= 1000) {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
    return value;
  }
  
  return value;
}

export default ExcelSheetViewer;
