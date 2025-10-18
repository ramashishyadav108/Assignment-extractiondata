import json
import logging
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EnhancedLLMExtractor:
    """Enhanced extractor with page reference support."""

    EXTRACTION_PROMPT = """You are a precise data extraction assistant for Private Equity fund documents. Extract information from the PDF content.

**PDF CONTENT:**
{pdf_text}

**FIELDS TO EXTRACT:**
{fields_list}

**CRITICAL INSTRUCTIONS:**
1. For EACH value, INCLUDE source page reference: "value|Page X, description"
2. If value is calculated/derived: "value|Derived from [explanation]"
3. If not found: "|Not found"
4. Currency values: numeric only, e.g., "750000000|Page 5, Total Commitments"
5. Percentages: numeric (140 means 140%, 1.40 means 1.40x multiple)
6. Look across ALL pages - data may be scattered throughout
7. Extract from: Summary pages, Financial Statements, Tables, Letters
8. Common locations:
   - Fund Name: Cover page, opening letter
   - Financial metrics: Summary page, Statement of Net Assets
   - Performance: TVPI, DPI, RVPI usually in Summary or Performance section
   - Commitments/Drawdowns: Capital account statements

**EXAMPLE OUTPUTS:**
- "Linolex Fund LP|Page 1, Cover"
- "750000000|Page 5, Summary (Total Commitments $750.0m)"
- "50000000|Derived from Total Commitments - Paid-in Capital"
- "1.40|Page 5, Summary (DPI 1.40x)"
- "|Not found"

**OUTPUT FORMAT:**
Return ONLY a valid JSON object with field names as keys:
{{
  "General Partner": "value|source",
  "Fund Name": "value|source",
  "Total Commitments": "value|source",
  ...
}}

Be extremely accurate. Double-check all numbers and calculations.
"""

    def __init__(self):
        self.logger = logger
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def extract_portfolio_summary(
        self,
        pdf_text: str,
        pdf_pages: List[Dict[str, Any]],
        fields: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Extract portfolio summary data with page references.

        Args:
            pdf_text: Full text from PDF
            pdf_pages: List of page dictionaries with page numbers
            fields: List of field definitions

        Returns:
            Dictionary mapping field names to "value|source" strings
        """
        # Add page markers to text
        enhanced_text = self._add_page_markers(pdf_text, pdf_pages)

        # Create fields list for prompt
        fields_list = "\n".join([
            f"- {f['field']}: {f.get('description', '')}"
            for f in fields
        ])

        # Format prompt
        prompt = self.EXTRACTION_PROMPT.format(
            pdf_text=enhanced_text[:100000],  # Use more context
            fields_list=fields_list
        )

        try:
            gemini_model = genai.GenerativeModel(settings.LLM_MODEL)
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for accuracy
                )
            )

            # Parse JSON from response
            content = response.text

            # Extract JSON from markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            self.logger.info(f"Successfully extracted {len(result)} fields")
            return result

        except Exception as e:
            self.logger.error(f"Enhanced extraction error: {str(e)}")
            raise

    def _add_page_markers(self, full_text: str, pages: List[Dict[str, Any]]) -> str:
        """Add page number markers to help LLM identify sources."""
        if not pages:
            return full_text

        enhanced = ""
        for page in pages:
            page_num = page.get('page', '?')
            page_text = page.get('text', '')
            enhanced += f"\n\n=== PAGE {page_num} ===\n{page_text}"

        return enhanced
