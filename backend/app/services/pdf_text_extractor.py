from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


class PdfTextExtractor:
    def extract(self, pdf_bytes: bytes) -> list[ExtractedPage]:
        reader = PdfReader(BytesIO(pdf_bytes))
        extracted_pages: list[ExtractedPage] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if not text.strip():
                continue

            extracted_pages.append(
                ExtractedPage(
                    page_number=page_number,
                    text=text.strip(),
                )
            )

        return extracted_pages