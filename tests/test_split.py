from __future__ import annotations

from pathlib import Path
import fitz
from src.pdfsplit.core import split_pdf


def _make_pdf(path: Path, pages: int) -> None:
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i+1}")
    doc.save(path)
    doc.close()


def test_split_basic(tmp_path: Path):
    src = tmp_path / "demo.pdf"
    _make_pdf(src, 23)
    outs = split_pdf(src, max_pages=10)
    assert len(outs) == 3

    # open each part and verify page counts
    counts = []
    for p in outs:
        with fitz.open(p) as d:
            counts.append(d.page_count)
    assert counts == [10, 10, 3]
