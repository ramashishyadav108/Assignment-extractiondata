import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract structured data from PDF text using LLM."""
    
    EXTRACTION_PROMPT = """You are a precise data extraction assistant. Extract information from the following PDF content according to the template schema.

**EXTRACTION TEMPLATE:**
{template_schema}

**PDF CONTENT:**
{pdf_text}

**INSTRUCTIONS:**
1. Extract ONLY the fields specified in the template
2. Maintain exact field names and data types
3. For missing data, use null or empty string
4. For dates, use format: YYYY-MM-DD
5. For currency, extract numeric value only (no currency symbols)
6. Preserve decimal precision
7. For percentages, use decimal format (e.g., 0.15 for 15%)
8. Extract data from tables if present
9. Look for data across all pages
10. If uncertain about a value, still provide best estimate

**OUTPUT FORMAT:**
Return a valid JSON object with the following structure:
{{
  "data": {example_output_structure},
  "confidence_score": 0.95,
  "notes": "Any relevant extraction notes"
}}

Be extremely accurate. Double-check numbers, dates, and spellings against the source text.
"""
    
    def __init__(self):
        self.logger = logger
        self.gemini_model = None
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(settings.LLM_MODEL)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def extract_with_llm(
        self,
        pdf_text: str,
        template_schema: Dict[str, Any],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data using LLM with retry logic.
        
        Args:
            pdf_text: Extracted text from PDF
            template_schema: Template configuration
            model: Override default model
            
        Returns:
            Extracted data dictionary
        """
        model_to_use = model or settings.LLM_MODEL
        
        try:
            return self._extract_with_gemini(pdf_text, template_schema, model_to_use)
        
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {str(e)}")
            raise
    
    def _extract_with_gemini(
        self,
        pdf_text: str,
        template_schema: Dict[str, Any],
        model: str
    ) -> Dict[str, Any]:
        """Extract using Google Gemini models."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        # Create model instance with the specified model name
        # This ensures we use the latest model configuration
        gemini_model = genai.GenerativeModel(model)
        
        # Create example output structure
        example_structure = self._create_example_structure(template_schema)
        
        # Format prompt
        prompt = self.EXTRACTION_PROMPT.format(
            template_schema=json.dumps(template_schema, indent=2),
            pdf_text=pdf_text[:30000],  # Gemini supports larger context
            example_output_structure=json.dumps(example_structure, indent=2)
        )
        
        try:
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.LLM_TEMPERATURE,
                )
            )
            
            # Parse JSON from response
            content = response.text
            
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Ensure proper structure
            if 'data' not in result:
                result = {'data': result, 'confidence_score': 0.8}
            
            return result
        
        except Exception as e:
            self.logger.error(f"Gemini extraction error: {str(e)}")
            raise
    
    def _create_example_structure(self, template_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create example output structure from template."""
        example = {}
        
        for column in template_schema.get('columns', []):
            field_name = column['field']
            field_type = column['type']
            
            # Provide example values based on type
            if field_type == 'string':
                example[field_name] = "Example text"
            elif field_type == 'currency':
                example[field_name] = 1000000.00
            elif field_type == 'date':
                example[field_name] = "2024-01-01"
            elif field_type == 'percentage':
                example[field_name] = 0.15
            elif field_type == 'number':
                example[field_name] = 100
            else:
                example[field_name] = None
        
        return example
