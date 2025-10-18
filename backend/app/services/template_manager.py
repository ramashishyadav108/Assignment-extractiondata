import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manage extraction templates."""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.templates = {}
        logger.info(f"Template directory: {self.template_dir}")
        logger.info(f"Template directory (absolute): {self.template_dir.resolve()}")
        logger.info(f"Template directory exists: {self.template_dir.exists()}")
        self._load_templates()
    
    def _load_templates(self):
        """Load all template configurations."""
        try:
            template_files = list(self.template_dir.glob('*.json'))
            logger.info(f"Found {len(template_files)} template files")
            
            for template_file in template_files:
                template_id = template_file.stem
                with open(template_file, 'r') as f:
                    self.templates[template_id] = json.load(f)
                logger.info(f"Loaded template: {template_id}")
            
            logger.info(f"Total templates loaded: {len(self.templates)}")
            logger.info(f"Available templates: {list(self.templates.keys())}")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}", exc_info=True)
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template configuration by ID."""
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found")
        return self.templates[template_id]
    
    def list_templates(self) -> Dict[str, str]:
        """List available templates."""
        return {
            tid: config.get('name', tid)
            for tid, config in self.templates.items()
        }
