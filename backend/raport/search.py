# search.py
# Utility module
from pathlib import Path
from typing import Union
import PyPDF2
import re
from loguru import logger


def search_text_in_pdfs(
    directory_pdfs: Path, text: str
) -> Union[tuple[Path, int], tuple[None, int]]:
    """
    We search in all the files from the directory_pdfs the text and return the path of the file
    that we found the text and the number of page
    """
    for file in directory_pdfs.glob("*.pdf"):
        logger.debug(f"File {file}")
        reader = PyPDF2.PdfReader(file)
        for page_number, page in enumerate(reader.pages, start=1):
            whole_text_page = page.extract_text() or ""
            if re.search(text, whole_text_page, flags=re.IGNORECASE):
                return file, page_number
    return None, -1
