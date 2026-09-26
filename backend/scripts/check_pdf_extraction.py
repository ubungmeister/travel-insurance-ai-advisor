r"""Smoke-test text extraction against a real PDF file.

Run from the backend directory:

    python -m scripts.check_pdf_extraction "path/to/document.pdf"
"""

import argparse
from pathlib import Path

from app.services.pdf_text_extractor import PdfTextExtractor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract PDF text and print a short page preview."
    )
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--preview-pages", type=int, default=3)
    parser.add_argument("--preview-characters", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pdf_path: Path = args.pdf_path

    if not pdf_path.is_file():
        raise SystemExit(f"PDF file not found: {pdf_path}")

    pdf_bytes = pdf_path.read_bytes()
    pages = PdfTextExtractor().extract(pdf_bytes)

    if not pages:
        raise SystemExit("No extractable text was found in the PDF.")

    if args.expected_pages is not None and len(pages) != args.expected_pages:
        raise SystemExit(
            f"Expected {args.expected_pages} extracted pages, got {len(pages)}."
        )

    print(f"File: {pdf_path.name}")
    print(f"PDF size: {len(pdf_bytes):,} bytes")
    print(f"Extracted pages: {len(pages)}")

    for page in pages[: args.preview_pages]:
        preview = " ".join(page.text.split())[: args.preview_characters]
        print()
        print(f"Page {page.page_number}:")
        print(preview)

    print()
    print("PDF extraction completed successfully.")


if __name__ == "__main__":
    main()
