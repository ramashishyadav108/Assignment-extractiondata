"""
PDF text extraction service using pdfplumber.
Handles PDF parsing and text extraction with error handling.
"""

import pdfplumber
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text content from PDF files."""
    
    def __init__(self):
        self.extracted_text = ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
            
        Raises:
            Exception: If PDF extraction fails
        """
        try:
            extracted_text = []
            
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Processing PDF with {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    logger.debug(f"Extracting text from page {page_num}")
                    
                    # Extract text from the page
                    text = page.extract_text()
                    
                    if text:
                        extracted_text.append(f"\n--- Page {page_num} ---\n")
                        extracted_text.append(text)
                    
                    # Also extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, start=1):
                            extracted_text.append(f"\n[Table {table_num} on Page {page_num}]\n")
                            # Convert table to text representation
                            for row in table:
                                if row:
                                    row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                    extracted_text.append(row_text + "\n")
            
            self.extracted_text = "".join(extracted_text)
            
            if not self.extracted_text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            logger.info(f"Successfully extracted {len(self.extracted_text)} characters from PDF")
            return self.extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def get_text_preview(self, max_chars: int = 500) -> str:
        """Get a preview of the extracted text."""
        if not self.extracted_text:
            return ""
        return self.extracted_text[:max_chars] + ("..." if len(self.extracted_text) > max_chars else "")
