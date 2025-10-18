import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate extracted data against source and schema."""
    
    def __init__(self):
        self.logger = logger
    
    def validate_extraction(
        self,
        extracted_data: Dict[str, Any],
        pdf_text: str,
        template_schema: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate extracted data.
        
        Args:
            extracted_data: Data extracted by LLM
            pdf_text: Original PDF text
            template_schema: Template configuration
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # 1. Check for missing required fields
        required_fields = template_schema.get('required_fields', [])
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # 2. Validate data types
        for column in template_schema.get('columns', []):
            field_name = column['field']
            field_type = column['type']
            
            if field_name in extracted_data:
                value = extracted_data[field_name]
                
                if value is not None and value != '':
                    type_valid, type_error = self._validate_type(value, field_type, field_name)
                    if not type_valid:
                        errors.append(type_error)
        
        # 3. Cross-check critical values against PDF text
        critical_fields = self._get_critical_fields(template_schema)
        for field in critical_fields:
            if field in extracted_data:
                value = extracted_data[field]
                if value and str(value).strip():
                    # Check if value appears in source (with some flexibility)
                    if not self._value_in_text(str(value), pdf_text):
                        warnings.append(
                            f"Value '{value}' for field '{field}' not clearly found in source"
                        )
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def _validate_type(
        self,
        value: Any,
        expected_type: str,
        field_name: str
    ) -> Tuple[bool, str]:
        """Validate value against expected type."""
        try:
            if expected_type == 'string':
                if not isinstance(value, str):
                    return False, f"Field '{field_name}' should be string, got {type(value).__name__}"
            
            elif expected_type == 'currency':
                if not isinstance(value, (int, float)):
                    # Try to parse if it's a string
                    if isinstance(value, str):
                        value = value.replace('$', '').replace(',', '').strip()
                        float(value)
                    else:
                        return False, f"Field '{field_name}' should be numeric for currency"
            
            elif expected_type == 'date':
                if isinstance(value, str):
                    # Try to parse date
                    datetime.strptime(value, '%Y-%m-%d')
                else:
                    return False, f"Field '{field_name}' should be date string in YYYY-MM-DD format"
            
            elif expected_type == 'percentage':
                if not isinstance(value, (int, float)):
                    if isinstance(value, str):
                        value = value.replace('%', '').strip()
                        float(value)
                    else:
                        return False, f"Field '{field_name}' should be numeric for percentage"
            
            elif expected_type == 'number':
                if not isinstance(value, (int, float)):
                    if isinstance(value, str):
                        float(value)
                    else:
                        return False, f"Field '{field_name}' should be numeric"
            
            return True, ""
        
        except Exception as e:
            return False, f"Type validation failed for '{field_name}': {str(e)}"
    
    def _get_critical_fields(self, template_schema: Dict[str, Any]) -> List[str]:
        """Identify critical fields that should be cross-checked."""
        critical_types = ['currency', 'date', 'number']
        critical_fields = []
        
        for column in template_schema.get('columns', []):
            if column['type'] in critical_types or column.get('required', False):
                critical_fields.append(column['field'])
        
        return critical_fields
    
    def _value_in_text(self, value: str, text: str) -> bool:
        """
        Check if value appears in text with some flexibility.
        Handles variations in formatting, spacing, etc.
        """
        # Clean value and text
        clean_value = re.sub(r'[^\w\s]', '', value.lower())
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Check for exact match
        if clean_value in clean_text:
            return True
        
        # Check for partial matches (for multi-word values)
        words = clean_value.split()
        if len(words) > 1:
            # Check if most words appear
            matches = sum(1 for word in words if len(word) > 2 and word in clean_text)
            return matches >= len(words) * 0.7
        
        return False
