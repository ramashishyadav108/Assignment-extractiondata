from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, List

from app.services.template_manager import TemplateManager
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize template manager
try:
    template_manager = TemplateManager(settings.TEMPLATE_DIR)
    logger.info(f"Template manager initialized with {len(template_manager.templates)} templates")
except Exception as e:
    logger.error(f"Failed to initialize template manager: {str(e)}")
    template_manager = None


@router.get("/templates")
async def list_templates():
    """
    List all available extraction templates.

    Returns:
        Dictionary of template IDs and their names
    """
    try:
        if template_manager is None:
            raise HTTPException(
                status_code=500,
                detail="Template manager not initialized"
            )

        templates = template_manager.list_templates()

        if not templates:
            logger.warning(f"No templates found in {settings.TEMPLATE_DIR}")
            raise HTTPException(
                status_code=404,
                detail=f"No templates found. Please check template directory: {settings.TEMPLATE_DIR}"
            )

        return {
            "templates": templates,
            "template_dir": str(settings.TEMPLATE_DIR),
            "count": len(templates)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get a specific template configuration.

    Args:
        template_id: ID of the template to retrieve

    Returns:
        Template configuration
    """
    try:
        if template_manager is None:
            raise HTTPException(
                status_code=500,
                detail="Template manager not initialized"
            )

        template = template_manager.get_template(template_id)
        return {
            "template_id": template_id,
            "config": template
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
