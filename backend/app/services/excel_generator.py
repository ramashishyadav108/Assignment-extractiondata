from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExcelGenerator:
    """Generate Excel files from extracted data."""
    
    def __init__(self):
        self.logger = logger
    
    def generate_excel(
        self,
        extracted_data: Dict[str, Any],
        template_config: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Generate Excel file matching template structure.
        
        Args:
            extracted_data: Data extracted from PDF
            template_config: Template configuration
            output_path: Path to save Excel file
            
        Returns:
            Path to generated Excel file
        """
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Extracted Data"
            
            # Get columns from template
            columns = template_config.get('columns', [])
            
            # Write headers
            self._write_headers(ws, columns)
            
            # Write data rows
            self._write_data_row(ws, extracted_data, columns, row=2)
            
            # Format worksheet
            self._format_worksheet(ws, columns)
            
            # Save workbook
            wb.save(output_path)
            self.logger.info(f"Excel file generated: {output_path}")
            
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error generating Excel: {str(e)}")
            raise
    
    def _write_headers(self, ws, columns: List[Dict[str, Any]]):
        """Write header row with formatting."""
        for col_idx, column in enumerate(columns, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = column['name']
            
            # Header formatting
            cell.font = Font(bold=True, color="FFFFFF", size=11)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            # Add border
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            cell.border = thin_border
    
    def _write_data_row(
        self,
        ws,
        data: Dict[str, Any],
        columns: List[Dict[str, Any]],
        row: int
    ):
        """Write a single data row."""
        for col_idx, column in enumerate(columns, start=1):
            field_name = column['field']
            field_type = column['type']
            
            # Get value from extracted data
            value = data.get(field_name, '')
            
            # Format value based on type
            formatted_value = self._format_value(value, field_type)
            
            cell = ws.cell(row=row, column=col_idx)
            cell.value = formatted_value
            
            # Apply cell formatting
            self._apply_cell_formatting(cell, field_type)
    
    def _format_value(self, value: Any, field_type: str) -> Any:
        """Format value based on field type."""
        if value is None or value == '':
            return ''
        
        try:
            if field_type == 'currency':
                # Ensure it's a number
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '').strip()
                return float(value)
            
            elif field_type == 'date':
                # Parse date if it's a string
                if isinstance(value, str):
                    try:
                        return datetime.strptime(value, '%Y-%m-%d')
                    except:
                        return value
                return value
            
            elif field_type == 'percentage':
                # Convert to decimal
                if isinstance(value, str):
                    value = value.replace('%', '').strip()
                    return float(value) / 100 if float(value) > 1 else float(value)
                return float(value) if float(value) <= 1 else float(value) / 100
            
            elif field_type == 'number':
                if isinstance(value, str):
                    value = value.replace(',', '').strip()
                return float(value)
            
            else:  # string
                return str(value)
        
        except Exception as e:
            logger.warning(f"Error formatting value {value} as {field_type}: {str(e)}")
            return value
    
    def _apply_cell_formatting(self, cell, field_type: str):
        """Apply formatting to cell based on data type."""
        # Alignment
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        
        # Number format
        if field_type == 'currency':
            cell.number_format = '$#,##0.00'
            cell.alignment = Alignment(horizontal="right", vertical="center")
        
        elif field_type == 'date':
            cell.number_format = 'yyyy-mm-dd'
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        elif field_type == 'percentage':
            cell.number_format = '0.00%'
            cell.alignment = Alignment(horizontal="right", vertical="center")
        
        elif field_type == 'number':
            cell.number_format = '#,##0.00'
            cell.alignment = Alignment(horizontal="right", vertical="center")
        
        # Border
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        cell.border = thin_border
    
    def _format_worksheet(self, ws, columns: List[Dict[str, Any]]):
        """Apply final formatting to worksheet."""
        # Auto-adjust column widths
        for col_idx, column in enumerate(columns, start=1):
            col_letter = get_column_letter(col_idx)
            
            # Calculate optimal width based on header
            max_length = len(column['name']) + 2
            
            # Check if there's data and adjust
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_idx, max_col=col_idx):
                for cell in row:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
            
            # Set width (with limits)
            ws.column_dimensions[col_letter].width = min(max(max_length, 15), 50)
        
        # Freeze header row
        ws.freeze_panes = 'A2'
