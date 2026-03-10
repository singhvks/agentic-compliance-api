import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger("compliance_api")

class DocumentParser:
    """Parses various document formats into raw text with page metadata."""
    
    @staticmethod
    def parse(file_path: str) -> Dict[int, str]:
        """
        Parses a document and returns a dictionary mapping page_number to text.
        Returns: {1: "page 1 text...", 2: "page 2 text..."}
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        logger.info(f"Parsing document {path.name} with extension {ext}")
        
        if ext == '.pdf':
            return DocumentParser._parse_pdf(path)
        elif ext == '.docx':
            return DocumentParser._parse_docx(path)
        elif ext == '.json':
            return DocumentParser._parse_json(path)
        elif ext == '.txt':
            return DocumentParser._parse_text(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
    @staticmethod
    def _parse_pdf(path: Path) -> Dict[int, str]:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF (fitz) is required for PDF parsing.")
            
        doc = fitz.open(str(path))
        pages = {}
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages[page_num + 1] = text
        return pages
        
    @staticmethod
    def _parse_docx(path: Path) -> Dict[int, str]:
        try:
            import docx
        except ImportError:
            raise ImportError("python-docx is required for DOCX parsing.")
            
        doc = docx.Document(str(path))
        # DOCX doesn't have a strict concept of pages like PDF. 
        # We'll treat the whole document as page 1.
        text = "\n".join([para.text for para in doc.paragraphs])
        return {1: text}
        
    @staticmethod
    def _parse_json(path: Path) -> Dict[int, str]:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Convert JSON structure to a string representation
        return {1: json.dumps(data, indent=2)}

    @staticmethod
    def _parse_text(path: Path) -> Dict[int, str]:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        return {1: text}
