import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.core.logging import logger
from app.core.exceptions import ValidationError, NotFoundError


class FileStorageService:
    """Service for file storage operations"""
    
    def __init__(self, base_path: str = "app/utils/assets"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Allowed file types and max sizes (in bytes)
        self.allowed_extensions = {
            "image": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
            "document": {".pdf", ".doc", ".docx", ".txt", ".md"},
            "spreadsheet": {".xls", ".xlsx", ".csv"}
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def _get_allowed_extensions(self) -> set:
        """Get all allowed file extensions"""
        all_extensions = set()
        for ext_set in self.allowed_extensions.values():
            all_extensions.update(ext_set)
        return all_extensions
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size"""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        allowed_extensions = self._get_allowed_extensions()
        
        if file_ext not in allowed_extensions:
            raise ValidationError(
                f"File type not allowed. Allowed types: {', '.join(sorted(allowed_extensions))}"
            )
        
        # Note: File size validation should be done when reading the file
        # FastAPI's UploadFile doesn't provide size before reading
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename"""
        file_ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"
    
    async def upload_file(self, file: UploadFile, task_id: str) -> dict:
        """Upload a file for a task"""
        logger.info(f"File upload attempt: {file.filename} for task: {task_id}")
        
        if not file.filename:
            raise ValidationError("Filename is required")
        
        # Validate file
        self._validate_file(file)
        
        # Create task directory
        task_dir = self.base_path / str(task_id)
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)
        file_path = task_dir / unique_filename
        
        # Read file content and check size
        content = await file.read()
        file_size = len(content)
        
        if file_size > self.max_file_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {self.max_file_size / (1024*1024)}MB")
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File uploaded successfully: {file_path} ({file_size} bytes)")
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": str(file_path.relative_to(self.base_path)),
            "file_size": file_size,
            "content_type": file.content_type
        }
    
    async def download_file(self, file_path: str) -> bytes:
        """Download a file by relative path"""
        full_path = self.base_path / file_path
        
        if not full_path.exists() or not full_path.is_file():
            raise NotFoundError("File not found")
        
        # Security check: ensure path is within base_path
        try:
            full_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise ValidationError("Invalid file path")
        
        logger.info(f"File download: {file_path}")
        
        with open(full_path, "rb") as f:
            return f.read()
    
    async def delete_file(self, file_path: str) -> None:
        """Delete a file by relative path"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise NotFoundError("File not found")
        
        # Security check: ensure path is within base_path
        try:
            full_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise ValidationError("Invalid file path")
        
        full_path.unlink()
        logger.info(f"File deleted: {file_path}")
    
    async def list_files(self, task_id: str) -> list[dict]:
        """List all files for a task"""
        task_dir = self.base_path / str(task_id)
        
        if not task_dir.exists():
            return []
        
        files = []
        for file_path in task_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path.relative_to(self.base_path)),
                    "file_size": stat.st_size,
                    "created_at": stat.st_ctime
                })
        
        return files
