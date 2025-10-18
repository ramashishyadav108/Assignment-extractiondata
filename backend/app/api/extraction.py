import logging
from pathlib import Path
from typing import List

from app.services.pdf_parser import PDFParser
from app.services.llm_extractor import LLMExtractor
from app.services.excel_generator import ExcelGenerator
from app.services.validator import DataValidator
from app.services.template_manager import TemplateManager
from app.services.job_manager import JobManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize services
pdf_parser = PDFParser()
llm_extractor = LLMExtractor()
excel_generator = ExcelGenerator()
data_validator = DataValidator()
template_manager = TemplateManager(settings.TEMPLATE_DIR)
job_manager = JobManager(settings.PROJECT_ROOT / "jobs")


async def process_extraction_job(
    job_id: str,
    file_names: List[str],
    template_id: str
):
    """
    Process extraction job for multiple files.
    
    Args:
        job_id: Job identifier
        file_names: List of file names to process
        template_id: Template to use
    """
    try:
        logger.info(f"Starting extraction job {job_id}")
        
        # Update job status
        job_manager.update_job(job_id, {
            'status': 'processing',
            'progress': 0.0
        })
        
        # Get template configuration
        template_config = template_manager.get_template(template_id)
        
        # Process each file
        all_extracted_data = []
        
        for idx, file_name in enumerate(file_names):
            try:
                logger.info(f"Processing file {idx + 1}/{len(file_names)}: {file_name}")
                
                # Extract text from PDF
                pdf_path = settings.UPLOAD_DIR / file_name
                pdf_content = pdf_parser.extract_text_from_pdf(pdf_path)
                
                # Extract data using LLM
                result = llm_extractor.extract_with_llm(
                    pdf_content['full_text'],
                    template_config
                )
                
                extracted_data = result.get('data', {})
                
                # Validate extraction
                is_valid, errors, warnings = data_validator.validate_extraction(
                    extracted_data,
                    pdf_content['full_text'],
                    template_config
                )
                
                if warnings:
                    logger.warning(f"Validation warnings for {file_name}: {warnings}")
                
                if not is_valid:
                    logger.error(f"Validation failed for {file_name}: {errors}")
                    job_manager.update_job(job_id, {
                        'errors': errors
                    })
                
                # Add source file info
                extracted_data['_source_file'] = file_name
                all_extracted_data.append(extracted_data)
                
                # Update progress
                progress = ((idx + 1) / len(file_names)) * 100
                job_manager.update_job(job_id, {
                    'files_processed': idx + 1,
                    'progress': progress
                })
            
            except Exception as e:
                logger.error(f"Error processing {file_name}: {str(e)}")
                job_manager.mark_failed(job_id, f"Error processing {file_name}: {str(e)}")
                return
        
        # Generate Excel file
        output_filename = f"extracted_data_{job_id}.xlsx"
        output_path = settings.OUTPUT_DIR / output_filename
        
        # For single file, use the data directly
        # For multiple files, we'd need to handle multiple rows
        if len(all_extracted_data) == 1:
            excel_generator.generate_excel(
                all_extracted_data[0],
                template_config,
                output_path
            )
        else:
            # Generate multi-row Excel
            generate_multi_file_excel(
                all_extracted_data,
                template_config,
                output_path
            )
        
        # Mark job as completed
        job_manager.mark_completed(job_id, str(output_path), all_extracted_data)
        
        logger.info(f"Job {job_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job_manager.mark_failed(job_id, str(e))


def generate_multi_file_excel(
    data_list: List[dict],
    template_config: dict,
    output_path: Path
):
    """Generate Excel with multiple rows from multiple files."""
    from openpyxl import Workbook
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Extracted Data"
    
    # Write headers
    columns = template_config.get('columns', [])
    for col_idx, column in enumerate(columns, start=1):
        ws.cell(row=1, column=col_idx, value=column['name'])
    
    # Write data rows
    for row_idx, data in enumerate(data_list, start=2):
        excel_generator._write_data_row(ws, data, columns, row_idx)
    
    # Format worksheet
    excel_generator._format_worksheet(ws, columns)
    
    wb.save(output_path)
