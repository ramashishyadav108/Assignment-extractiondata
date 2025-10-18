import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JobManager:
    """Manage extraction jobs."""
    
    def __init__(self, jobs_dir: Path):
        self.jobs_dir = jobs_dir
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_job(
        self,
        files_count: int,
        template_id: str,
        file_names: list
    ) -> str:
        """Create a new extraction job."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            'job_id': job_id,
            'status': 'pending',
            'progress': 0.0,
            'files_count': files_count,
            'files_processed': 0,
            'template_id': template_id,
            'file_names': file_names,
            'errors': [],
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        self._save_job(job_id, job_data)
        logger.info(f"Created job: {job_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None
        
        with open(job_file, 'r') as f:
            return json.load(f)
    
    def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Update job status."""
        job_data = self.get_job(job_id)
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        job_data.update(updates)
        self._save_job(job_id, job_data)
    
    def mark_completed(self, job_id: str, output_file: str, extracted_data: list = None):
        """Mark job as completed."""
        updates = {
            'status': 'completed',
            'progress': 100.0,
            'completed_at': datetime.now().isoformat(),
            'output_file': output_file
        }
        if extracted_data:
            updates['extracted_data'] = extracted_data
        self.update_job(job_id, updates)
    
    def mark_failed(self, job_id: str, error: str):
        """Mark job as failed."""
        job_data = self.get_job(job_id)
        if job_data:
            errors = job_data.get('errors', [])
            errors.append(error)
            
            self.update_job(job_id, {
                'status': 'failed',
                'errors': errors,
                'completed_at': datetime.now().isoformat()
            })
    
    def _save_job(self, job_id: str, job_data: Dict[str, Any]):
        """Save job data to file."""
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
