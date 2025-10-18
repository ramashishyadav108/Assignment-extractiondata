import pdfplumber
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract text and tables from PDF files with layout preservation."""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text with layout preservation from PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            text_content = []
            all_text = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text with layout preservation
                    page_text = page.extract_text(layout=True)
                    
                    # Extract tables separately for better structure
                    tables = page.extract_tables()
                    
                    # Process tables into structured format
                    structured_tables = []
                    if tables:
                        for table in tables:
                            structured_tables.append(self._process_table(table))
                    
                    page_content = {
                        'page': page_num + 1,
                        'text': page_text or '',
                        'tables': structured_tables,
                        'width': page.width,
                        'height': page.height
                    }
                    
                    text_content.append(page_content)
                    all_text += (page_text or '') + "\n\n"
                
                return {
                    'pages': text_content,
                    'full_text': all_text.strip(),
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata or {}
                }
        
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def _process_table(self, table: List[List[str]]) -> Dict[str, Any]:
        """
        Process raw table data into structured format.
        
        Args:
            table: Raw table data from pdfplumber
            
        Returns:
            Structured table dictionary
        """
        if not table or len(table) == 0:
            return {'headers': [], 'rows': []}
        
        # First row is typically headers
        headers = [str(cell).strip() if cell else '' for cell in table[0]]
        
        # Rest are data rows
        rows = []
        for row in table[1:]:
            row_data = [str(cell).strip() if cell else '' for cell in row]
            rows.append(row_data)
        
        return {
            'headers': headers,
            'rows': rows
        }
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata or {},
                    'file_size': pdf_path.stat().st_size
                }
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return {}
