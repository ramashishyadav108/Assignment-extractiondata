import logging
from pathlib import Path
from typing import List
import json

from app.services.pdf_parser import PDFParser
from app.services.enhanced_llm_extractor import EnhancedLLMExtractor
from app.services.enhanced_excel_generator import EnhancedExcelGenerator
from app.services.job_manager import JobManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize services
pdf_parser = PDFParser()
enhanced_llm_extractor = EnhancedLLMExtractor()
enhanced_excel_generator = EnhancedExcelGenerator()
job_manager = JobManager(settings.PROJECT_ROOT / "jobs")

# Define portfolio summary fields matching expected output
PORTFOLIO_SUMMARY_FIELDS = [
    {"field": "General Partner", "description": "Name of the General Partner managing the fund"},
    {"field": "ILPA GP", "description": "ILPA format General Partner name"},
    {"field": "Assets Under Management", "description": "Total assets under management (numeric value)"},
    {"field": "Active Funds", "description": "Number of active funds"},
    {"field": "Active Portfolio Companies", "description": "Number of active portfolio companies"},
    {"field": "Fund Name", "description": "Official name of the fund"},
    {"field": "Fund Currency", "description": "Currency used for fund reporting (e.g., USD, EUR)"},
    {"field": "Total Commitments", "description": "Total committed capital"},
    {"field": "Total Drawdowns", "description": "Total capital drawn/paid-in"},
    {"field": "Remaining Commitments", "description": "Uncalled capital remaining"},
    {"field": "Total Number of Investments", "description": "Total number of portfolio investments"},
    {"field": "Total Distributions", "description": "Total distributions to investors"},
    {"field": "- as % of Drawdowns", "description": "Distributions as percentage of drawdowns"},
    {"field": "- as % of Commitments", "description": "Distributions as percentage of commitments"},
    {"field": "DPI", "description": "Distributions to Paid-In Capital multiple"},
    {"field": "RVPI", "description": "Residual Value to Paid-In Capital multiple"},
    {"field": "TVPI", "description": "Total Value to Paid-In Capital multiple"},
]


async def process_enhanced_extraction_job(
    job_id: str,
    file_names: List[str],
    template_id: str = "portfolio_summary"
):
    """
    Process extraction job using enhanced extractor for accurate Field|Value format.

    Args:
        job_id: Job identifier
        file_names: List of file names to process
        template_id: Template to use (default: portfolio_summary)
    """
    try:
        logger.info(f"Starting enhanced extraction job {job_id}")

        # Update job status
        job_manager.update_job(job_id, {
            'status': 'processing',
            'progress': 0.0
        })

        # Store all extracted data for preview
        all_extracted_data = []

        # Process each file
        for idx, file_name in enumerate(file_names):
            try:
                logger.info(f"Processing file {idx + 1}/{len(file_names)}: {file_name}")

                # Extract text from PDF with page information
                pdf_path = settings.UPLOAD_DIR / file_name
                pdf_content = pdf_parser.extract_text_from_pdf(pdf_path)

                logger.info(f"Extracted {pdf_content['num_pages']} pages from {file_name}")

                # Extract data using enhanced LLM extractor
                extracted_data = enhanced_llm_extractor.extract_portfolio_summary(
                    pdf_content['full_text'],
                    pdf_content['pages'],
                    PORTFOLIO_SUMMARY_FIELDS
                )

                logger.info(f"Extracted {len(extracted_data)} fields from {file_name}")

                # Add source file info and store for preview
                extracted_data_with_source = extracted_data.copy()
                extracted_data_with_source['_source_file'] = file_name
                all_extracted_data.append(extracted_data_with_source)

                # Generate Excel file with Field | Value format
                # Use sanitized filename
                safe_filename = file_name.replace('.pdf', '').replace(' ', '_')
                output_filename = f"{safe_filename}_Extracted_Fund_Data.xlsx"
                output_path = settings.OUTPUT_DIR / output_filename

                enhanced_excel_generator.generate_portfolio_summary_excel(
                    extracted_data,
                    output_path,
                    fund_name=file_name
                )

                logger.info(f"Generated Excel file: {output_path}")

                # Update progress
                progress = ((idx + 1) / len(file_names)) * 100
                job_manager.update_job(job_id, {
                    'files_processed': idx + 1,
                    'progress': progress,
                    'output_file': str(output_path)
                })

            except Exception as e:
                logger.error(f"Error processing {file_name}: {str(e)}", exc_info=True)
                job_manager.mark_failed(job_id, f"Error processing {file_name}: {str(e)}")
                return

        # Mark job as completed with extracted data
        job_manager.mark_completed(job_id, str(output_path), all_extracted_data)

        logger.info(f"Enhanced extraction job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Enhanced extraction job {job_id} failed: {str(e)}", exc_info=True)
        job_manager.mark_failed(job_id, str(e))
