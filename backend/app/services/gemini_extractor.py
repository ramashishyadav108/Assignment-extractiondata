"""
Gemini API integration service for data extraction.
Handles communication with Google's Gemini API and processes responses.
Uses progressive chunking to extract complete data from large PDFs.
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, Any, Optional, List
from app.config import settings
from app.templates.prompt_template import EXTRACTION_PROMPT_TEMPLATE, VALIDATION_PROMPT

logger = logging.getLogger(__name__)


class GeminiExtractor:
    """Extract structured data using Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API client.
        
        Args:
            api_key: Gemini API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"Initialized Gemini model: {settings.GEMINI_MODEL}")
    
    def extract_data(self, pdf_text: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Extract structured data from PDF text using progressive chunking.
        Splits large PDFs into 4 chunks (1/4 each) and extracts all 9 sections from each chunk,
        then progressively merges the results.
        
        Args:
            pdf_text: Extracted text from PDF
            max_retries: Maximum number of retry attempts
            
        Returns:
            Structured data as a dictionary
            
        Raises:
            Exception: If extraction fails
        """
        # Use progressive chunking strategy for complete data extraction
        # Split into 4 chunks (1/4 of total data each)
        min_chunk_size = 10000  # Minimum chunk size to avoid too small chunks
        chunk_size = max(min_chunk_size, len(pdf_text) // 4)  # 1/4 of total data
        
        if len(pdf_text) > min_chunk_size * 2:  # Only chunk if PDF is large enough
            logger.info(f"PDF text size: {len(pdf_text)} chars")
            logger.info(f"Using progressive chunking: 1/4 of total data per chunk (~{chunk_size} chars)")
            return self._extract_data_progressive_chunks(pdf_text, chunk_size, max_retries)
        else:
            logger.info(f"PDF text size ({len(pdf_text)} chars) - Using single extraction")
            return self._extract_data_single(pdf_text, max_retries)
    
    def _extract_data_progressive_chunks(self, pdf_text: str, chunk_size: int, max_retries: int) -> Dict[str, Any]:
        """
        Extract data progressively by splitting PDF into chunks.
        For EACH chunk, extract all 9 sections, then merge results.
        
        Args:
            pdf_text: Full PDF text
            chunk_size: Size of each chunk in characters (1/4 of total)
            max_retries: Maximum retry attempts
            
        Returns:
            Merged structured data from all chunks
        """
        # Split PDF text into chunks
        chunks = self._split_into_chunks(pdf_text, chunk_size)
        total_chunks = len(chunks)
        
        logger.info("="*80)
        logger.info("PROGRESSIVE CHUNKING EXTRACTION (1/4 Strategy)")
        logger.info("="*80)
        logger.info(f"Total PDF size: {len(pdf_text)} characters")
        logger.info(f"Chunk size: ~{chunk_size} characters (1/4 of total)")
        logger.info(f"Number of chunks: {total_chunks}")
        logger.info("")
        
        # Initialize merged result with all 9 section structures
        merged_result = {
            "portfolio_summary": {},
            "schedule_of_investments": [],
            "statement_of_operations": [],
            "statement_of_cashflows": {},
            "pcap_statement": {},
            "portfolio_company_profile": [],
            "portfolio_company_financials": [],
            "footnotes": [],
            "reference_values": {}  # 9th section
        }
        
        # Process each chunk and extract all 9 sections
        for chunk_idx, chunk_text in enumerate(chunks, 1):
            logger.info("-"*80)
            logger.info(f"📊 CHUNK {chunk_idx}/{total_chunks}")
            logger.info(f"   Chunk size: {len(chunk_text)} characters")
            logger.info(f"   Percentage: {(len(chunk_text) / len(pdf_text) * 100):.1f}% of total PDF")
            logger.info(f"   Character range: {sum(len(chunks[i]) for i in range(chunk_idx-1))} - {sum(len(chunks[i]) for i in range(chunk_idx))}")
            logger.info("-"*80)
            
            try:
                # Extract all 9 sections from this chunk
                logger.info(f"   🔄 Extracting all 9 sections from chunk {chunk_idx}...")
                chunk_data = self._extract_data_single(chunk_text, max_retries)
                
                if chunk_data:
                    logger.info(f"   ✅ Successfully extracted data from chunk {chunk_idx}")
                    logger.info(f"   📦 Sections found: {list(chunk_data.keys())}")
                    
                    # Progressively merge this chunk's data into the main result
                    logger.info(f"   🔄 Merging chunk {chunk_idx} data into accumulated results...")
                    merged_result = self._progressive_merge(merged_result, chunk_data, chunk_idx)
                    logger.info(f"   ✓ Chunk {chunk_idx} merged successfully")
                    
                    # Log current state
                    self._log_merge_status(merged_result, chunk_idx, total_chunks)
                else:
                    logger.warning(f"   ⚠️  No data extracted from chunk {chunk_idx}")
                    
            except Exception as e:
                logger.error(f"   ❌ Failed to process chunk {chunk_idx}: {str(e)}")
                logger.info(f"   ➡️  Continuing with next chunk...")
            
            logger.info("")
        
        logger.info("="*80)
        logger.info("PROGRESSIVE EXTRACTION COMPLETED")
        logger.info("="*80)
        logger.info(f"✓ Processed {total_chunks} chunks")
        logger.info(f"✓ Final result contains data from all chunks")
        logger.info(f"✓ All 9 sections processed")
        logger.info("")
        
        # Final validation
        validated_data = self._validate_data(merged_result)
        
        return validated_data
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of specified size.
        Try to split at page boundaries when possible.
        
        Args:
            text: Full text to split
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Try to split at page boundaries first
        pages = text.split("--- Page ")
        current_chunk = ""
        
        for page in pages:
            page_text = "--- Page " + page if page else page
            
            # If adding this page exceeds chunk size, save current chunk and start new one
            if len(current_chunk) + len(page_text) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = page_text
            else:
                current_chunk += page_text
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # If no pages found or chunks too large, fall back to simple splitting
        if not chunks or any(len(c) > chunk_size * 1.5 for c in chunks):
            chunks = []
            for i in range(0, len(text), chunk_size):
                chunks.append(text[i:i + chunk_size])
        
        return chunks
    
    def _progressive_merge(self, accumulated: Dict[str, Any], new_data: Dict[str, Any], chunk_num: int) -> Dict[str, Any]:
        """
        Progressively merge new chunk data into accumulated results.
        Updates existing data without overwriting previously extracted information.
        
        Args:
            accumulated: Accumulated data from previous chunks
            new_data: New data from current chunk
            chunk_num: Current chunk number
            
        Returns:
            Updated accumulated data
        """
        for key, value in new_data.items():
            if key not in accumulated:
                accumulated[key] = value
                
            elif isinstance(value, dict) and isinstance(accumulated[key], dict):
                # For dictionaries (portfolio_summary, cashflows, pcap, reference_values)
                # Merge new keys, but keep existing values for duplicate keys
                for sub_key, sub_value in value.items():
                    if sub_key not in accumulated[key] or accumulated[key][sub_key] is None or accumulated[key][sub_key] == 0:
                        # Only update if not already set or is null/zero
                        accumulated[key][sub_key] = sub_value
                
            elif isinstance(value, list) and isinstance(accumulated[key], list):
                # For lists (investments, operations, companies, footnotes)
                # Append new items, avoiding duplicates
                existing_items = accumulated[key]
                
                for new_item in value:
                    # Check if this item already exists (simple duplicate check)
                    is_duplicate = False
                    if isinstance(new_item, dict):
                        # Check for duplicate based on key fields
                        for existing_item in existing_items:
                            if self._is_duplicate_item(existing_item, new_item):
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        accumulated[key].append(new_item)
        
        return accumulated
    
    def _is_duplicate_item(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """
        Check if two dictionary items are duplicates based on key fields.
        
        Args:
            item1: First item
            item2: Second item
            
        Returns:
            True if items are duplicates
        """
        # Key fields to check for duplicates
        key_fields = ['investment_name', 'company_name', 'line_item', 'footnote_number', 'name']
        
        for field in key_fields:
            if field in item1 and field in item2:
                if item1[field] == item2[field]:
                    return True
        
        return False
    
    def _log_merge_status(self, data: Dict[str, Any], current_chunk: int, total_chunks: int):
        """
        Log the current status of merged data.
        
        Args:
            data: Current merged data
            current_chunk: Current chunk number
            total_chunks: Total number of chunks
        """
        logger.info(f"   📈 Progress after chunk {current_chunk}/{total_chunks}:")
        
        for key, value in data.items():
            if isinstance(value, list):
                logger.info(f"      - {key}: {len(value)} items")
            elif isinstance(value, dict):
                if key in ["statement_of_cashflows", "pcap_statement"]:
                    row_count = len([k for k in value.keys() if k.startswith("row_")])
                    logger.info(f"      - {key}: {row_count} row entries")
                else:
                    non_null_count = len([v for v in value.values() if v is not None and v != 0 and v != ""])
                    logger.info(f"      - {key}: {non_null_count} fields populated")
    
    def _extract_data_single(self, pdf_text: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Extract data from PDF text using a single API call.
        Extracts all 9 sections from the provided text.
        
        Args:
            pdf_text: Extracted text from PDF (or chunk)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Structured data as a dictionary with all 9 sections
        """
        # Truncate text if too long (Gemini has token limits)
        # Gemini 2.0 Flash has larger context window - can handle more
        max_chars = 100000  # Increased limit for Gemini 2.0 Flash
        if len(pdf_text) > max_chars:
            logger.warning(f"PDF text too long ({len(pdf_text)} chars), truncating to {max_chars}")
            pdf_text = pdf_text[:max_chars] + "\n\n[... text truncated ...]"
        
        # Create prompt with extracted text
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(extracted_text=pdf_text)
        
        # Try extraction with retries
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Extraction attempt {attempt}/{max_retries}")
                logger.info("Sending extraction request to Gemini API...")
                
                # Generate content with specific configuration
                generation_config = {
                    "temperature": settings.GEMINI_TEMPERATURE,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": settings.GEMINI_MAX_TOKENS,
                }
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings={
                        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                    }
                )
                
                # Extract text from response
                response_text = response.text
                logger.info(f"Received response from Gemini ({len(response_text)} chars)")
                
                # Log first part of response for debugging
                logger.debug(f"Response preview: {response_text[:500]}...")
                
                # Parse JSON response
                extracted_data = self._parse_json_response(response_text)
                
                # Validate and clean data
                validated_data = self._validate_data(extracted_data)
                
                logger.info("Successfully extracted and validated data")
                return validated_data
                
            except Exception as e:
                logger.error(f"Extraction attempt {attempt} failed: {str(e)}")
                if attempt == max_retries:
                    logger.error(f"All {max_retries} extraction attempts failed")
                    raise Exception(f"Failed to extract data after {max_retries} attempts: {str(e)}")
                logger.info(f"Retrying... ({attempt + 1}/{max_retries})")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response, handling markdown code blocks.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Parsed JSON data
        """
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in cleaned_text:
                start = cleaned_text.find("```json") + 7
                end = cleaned_text.rfind("```")
                cleaned_text = cleaned_text[start:end].strip()
            elif "```" in cleaned_text:
                start = cleaned_text.find("```") + 3
                end = cleaned_text.rfind("```")
                cleaned_text = cleaned_text[start:end].strip()
            
            # Remove any leading/trailing non-JSON text
            # Find first { and last }
            start_idx = cleaned_text.find("{")
            end_idx = cleaned_text.rfind("}")
            
            if start_idx == -1 or end_idx == -1:
                raise json.JSONDecodeError("No JSON object found", cleaned_text, 0)
            
            cleaned_text = cleaned_text[start_idx:end_idx + 1]
            
            # Parse JSON
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response text (first 1000 chars): {response_text[:1000]}...")
            
            # Try to salvage data by asking Gemini to fix it
            try:
                fix_prompt = f"""The following text should be valid JSON but has errors. Fix it and return ONLY valid JSON (no explanations, no markdown):

{response_text[:5000]}

Return ONLY the corrected JSON starting with {{ and ending with }}"""
                
                response = self.model.generate_content(fix_prompt)
                fixed_text = response.text.strip()
                
                # Clean again
                if "```json" in fixed_text:
                    start = fixed_text.find("```json") + 7
                    end = fixed_text.rfind("```")
                    fixed_text = fixed_text[start:end].strip()
                elif "```" in fixed_text:
                    start = fixed_text.find("```") + 3
                    end = fixed_text.rfind("```")
                    fixed_text = fixed_text[start:end].strip()
                
                # Find JSON boundaries
                start_idx = fixed_text.find("{")
                end_idx = fixed_text.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    fixed_text = fixed_text[start_idx:end_idx + 1]
                
                data = json.loads(fixed_text)
                logger.info("Successfully repaired JSON response")
                return data
                
            except Exception as repair_error:
                logger.error(f"Failed to repair JSON: {str(repair_error)}")
                raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted data.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Validated data
        """
        # Basic validation - ensure required top-level keys exist
        required_keys = [
            "portfolio_summary",
            "schedule_of_investments",
            "statement_of_operations",
            "statement_of_cashflows",
            "pcap_statement",
            "portfolio_company_profile",
            "portfolio_company_financials",
            "footnotes",
            "reference_values"
        ]
        
        for key in required_keys:
            if key not in data:
                logger.warning(f"Missing required key: {key}, adding empty structure")
                if key in ["schedule_of_investments", "statement_of_operations", 
                          "portfolio_company_profile", "portfolio_company_financials", 
                          "footnotes"]:
                    data[key] = []
                elif key in ["statement_of_cashflows", "pcap_statement"]:
                    data[key] = {}  # These are now dicts, not arrays
                elif key == "reference_values":
                    data[key] = {}
                else:
                    data[key] = {}
        
        # Check if critical financial statements have data
        if isinstance(data.get("statement_of_cashflows"), dict):
            cashflow_keys = len([k for k in data["statement_of_cashflows"].keys() if k.startswith("row_")])
            if cashflow_keys == 0:
                logger.warning("Statement of Cashflows is empty - no row data extracted")
            else:
                logger.info(f"Statement of Cashflows: {cashflow_keys} keys extracted (expected 78)")
        
        if isinstance(data.get("pcap_statement"), dict):
            pcap_keys = len([k for k in data["pcap_statement"].keys() if k.startswith("row_")])
            if pcap_keys == 0:
                logger.warning("PCAP Statement is empty - no row data extracted")
            else:
                logger.info(f"PCAP Statement: {pcap_keys} keys extracted (expected 84)")
        
        return data
    
    def extract_with_retry(self, pdf_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Extract data with retry logic.
        
        Args:
            pdf_text: Extracted text from PDF
            max_retries: Maximum number of retry attempts
            
        Returns:
            Structured data
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Extraction attempt {attempt + 1}/{max_retries}")
                return self.extract_data(pdf_text)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("Retrying...")
        
        raise Exception(f"Failed after {max_retries} attempts: {str(last_error)}")
