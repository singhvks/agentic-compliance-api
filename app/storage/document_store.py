import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.logging import logger

class DocumentStore:
    """Manages local file storage and job metadata persistence."""
    
    def __init__(self):
        self.base_dir = Path(settings.DOCUMENT_STORE_PATH)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_job_file(self, job_id: str) -> Path:
        return self.base_dir / f"{job_id}_status.json"
        
    def _get_report_file(self, job_id: str) -> Path:
        return self.base_dir / f"{job_id}_report.json"
        
    def _get_doc_dir(self, job_id: str) -> Path:
        doc_dir = self.base_dir / job_id
        doc_dir.mkdir(exist_ok=True)
        return doc_dir

    def create_job(self, job_id: str) -> None:
        """Initialize a new job with processing status."""
        status_data = {"job_id": job_id, "status": "processing"}
        logger.info("Created job in DocumentStore", job_id=job_id)
        self._write_json(self._get_job_file(job_id), status_data)
        
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the current job status."""
        file_path = self._get_job_file(job_id)
        if not file_path.exists():
            return None
        return self._read_json(file_path)
        
    def update_job_status(self, job_id: str, new_status: str) -> None:
        """Update job status to completed or failed."""
        status_data = self.get_job_status(job_id)
        if status_data:
            status_data["status"] = new_status
            self._write_json(self._get_job_file(job_id), status_data)
            logger.info("Updated job status", job_id=job_id, status=new_status)
            
    def save_report(self, job_id: str, report_data: Dict[str, Any]) -> None:
        """Save final JSON report."""
        self._write_json(self._get_report_file(job_id), report_data)
        self.update_job_status(job_id, "completed")
        logger.info("Saved report to DocumentStore", job_id=job_id)
        
    def save_failed(self, job_id: str, error: str) -> None:
        """Save failure context."""
        status_data = self.get_job_status(job_id) or {"job_id": job_id}
        status_data["status"] = "failed"
        status_data["error"] = error
        self._write_json(self._get_job_file(job_id), status_data)
        logger.error("Job failed", job_id=job_id, error=error)
        
    def get_report(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve completed report."""
        file_path = self._get_report_file(job_id)
        if not file_path.exists():
            return None
        return self._read_json(file_path)

    def save_document(self, job_id: str, file_name: str, content_bytes: bytes) -> str:
        """Save uploaded document bytes to a job specific folder."""
        doc_path = self._get_doc_dir(job_id) / file_name
        with open(doc_path, "wb") as f:
            f.write(content_bytes)
        logger.info("Saved document to disk", job_id=job_id, filename=file_name)
        return str(doc_path)
        
    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def _read_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

document_store = DocumentStore()
