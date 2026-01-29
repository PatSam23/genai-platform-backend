from typing import List, Dict
from pypdf import PdfReader

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
        reader = PdfReader(file_path)

        pages: List[Dict] = []

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""

            pages.append({
                "page": idx + 1,   # human-friendly page number
                "text": text.strip()
            })

        return pages