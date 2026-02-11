from typing import List, Dict
from pypdf import PdfReader
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/pdf_loader.log")

class PDFLoader:
    """
    Loads a PDF and extracts text page by page.
    """

    def load(self, file_path: str) -> List[Dict]:
        """
        Args:
            file_path: path to PDF file

        Returns:
            List of dicts:
            [
                {
                    "page": 1,
                    "text": "extracted text..."
                },
                ...
            ]
        """
        logger.info(f"Loading PDF: {file_path}")
        
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            logger.info(f"PDF opened successfully - total pages: {total_pages}")

            pages: List[Dict] = []

            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""

                pages.append({
                    "page": idx + 1,  
                    "text": text.strip()
                })
            
            logger.info(f"PDF processed - {total_pages} pages extracted")
            return pages
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}", exc_info=True)
            raise