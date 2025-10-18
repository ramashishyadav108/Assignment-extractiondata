import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.services.pdf_parser import PDFParser
from app.services.llm_extractor import LLMExtractor
from app.services.excel_generator import ExcelGenerator
from app.services.validator import DataValidator
from app.services.template_manager import TemplateManager
from app.config.settings import settings


@pytest.fixture
def pdf_parser():
    return PDFParser()


@pytest.fixture
def llm_extractor():
    return LLMExtractor()


@pytest.fixture
def excel_generator():
    return ExcelGenerator()


@pytest.fixture
def data_validator():
    return DataValidator()


@pytest.fixture
def template_manager():
    return TemplateManager(settings.TEMPLATE_DIR)


@pytest.fixture
def sample_pdf_path():
    """Path to sample PDF for testing."""
    return Path(__file__).parent.parent / 'examples' / 'sample_pdfs' / 'test.pdf'


@pytest.fixture
def template_1():
    """Template 1 configuration."""
    manager = TemplateManager(settings.TEMPLATE_DIR)
    return manager.get_template('template_1')


@pytest.fixture
def template_2():
    """Template 2 configuration."""
    manager = TemplateManager(settings.TEMPLATE_DIR)
    return manager.get_template('template_2')


def test_pdf_parser(pdf_parser, sample_pdf_path):
    """Test PDF text extraction."""
    if not sample_pdf_path.exists():
        pytest.skip("Sample PDF not found")
    
    result = pdf_parser.extract_text_from_pdf(sample_pdf_path)
    
    assert result is not None
    assert 'full_text' in result
    assert 'pages' in result
    assert 'num_pages' in result
    assert len(result['full_text']) > 0
    assert result['num_pages'] > 0


def test_template_loading(template_manager):
    """Test template configuration loading."""
    templates = template_manager.list_templates()
    
    assert 'template_1' in templates
    assert 'template_2' in templates


def test_template_1_structure(template_1):
    """Test Template 1 has required structure."""
    assert 'template_id' in template_1
    assert 'columns' in template_1
    assert 'required_fields' in template_1
    assert len(template_1['columns']) > 0
    assert 'fund_name' in template_1['required_fields']


def test_template_2_structure(template_2):
    """Test Template 2 has required structure."""
    assert 'template_id' in template_2
    assert 'columns' in template_2
    assert 'required_fields' in template_2
    assert len(template_2['columns']) > 0


def test_data_validator_type_validation(data_validator):
    """Test data type validation."""
    # Test currency validation
    is_valid, error = data_validator._validate_type(1000.50, 'currency', 'test_field')
    assert is_valid
    
    # Test date validation
    is_valid, error = data_validator._validate_type('2024-01-01', 'date', 'test_date')
    assert is_valid
    
    # Test percentage validation
    is_valid, error = data_validator._validate_type(0.15, 'percentage', 'test_pct')
    assert is_valid
    
    # Test string validation
    is_valid, error = data_validator._validate_type('Test Fund', 'string', 'test_str')
    assert is_valid


def test_excel_generator_value_formatting(excel_generator):
    """Test value formatting for Excel."""
    # Test currency formatting
    formatted = excel_generator._format_value('$1,000,000.50', 'currency')
    assert formatted == 1000000.50
    
    # Test percentage formatting
    formatted = excel_generator._format_value('15%', 'percentage')
    assert formatted == 0.15
    
    # Test number formatting
    formatted = excel_generator._format_value('1,234.56', 'number')
    assert formatted == 1234.56


@pytest.mark.skipif(
    not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY,
    reason="LLM API key not configured"
)
def test_llm_extraction_with_sample_text(llm_extractor, template_1):
    """Test LLM extraction with sample text."""
    sample_text = """
    Best Practices Fund II
    Fund Manager: Best Practices Capital
    Vintage Year: 2020
    Fund Size: $500,000,000
    Net IRR: 15.5%
    TVPI: 1.45x
    """
    
    result = llm_extractor.extract_with_llm(sample_text, template_1)
    
    assert result is not None
    assert 'data' in result
    assert isinstance(result['data'], dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
