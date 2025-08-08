from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import math
import fitz  # PyMuPDF


def _ensure_pdf_suffix(name: str) -> str:
    return name if name.lower().endswith(".pdf") else f"{name}.pdf"


def split_pdf(
    input_pdf: str | Path,
    max_pages: int = 10,
    output_dir: str | Path | None = None,
    output_pattern: str | None = None,
    password: str | None = None,
    keep_metadata: bool = True,
    overwrite: bool = False,
) -> List[Path]:
    """Split a single PDF into multiple parts of at most ``max_pages`` each.

    Parameters
    ----------
    input_pdf : str | Path
        Source PDF path.
    max_pages : int
        Maximum number of pages per chunk (default 10).
    output_dir : str | Path | None
        Destination directory (default: same as input).
    output_pattern : str | None
        Filename pattern. Supports placeholders: ``{stem}`` (input name without suffix),
        ``{i}`` (1-based index), ``{i0}`` (0-based index), ``{start}``, ``{end}`` (1-based page numbers).
        Default: ``"{stem}_part_{i:02d}.pdf"``.
    password : str | None
        Password if the PDF is encrypted.
    keep_metadata : bool
        If True, copy basic metadata to parts (default True).
    overwrite : bool
        If True, overwrite existing output files.

    Returns
    -------
    list[Path]
        Generated chunk paths.
    """
    input_pdf = Path(input_pdf)
    if output_dir is None:
        output_dir = input_pdf.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    pattern = output_pattern or "{stem}_part_{i:02d}.pdf"
    outputs: List[Path] = []

    with fitz.open(input_pdf) as src:
        if src.is_encrypted:
            if not password:
                raise ValueError("PDF is encrypted: please provide a password.")
            if not src.authenticate(password):
                raise ValueError("Wrong password for encrypted PDF.")

        total = src.page_count
        parts = math.ceil(total / max_pages)
        stem = input_pdf.stem

        for idx in range(parts):
            start0 = idx * max_pages  # 0-based inclusive
            end0 = min(start0 + max_pages, total) - 1  # 0-based inclusive
            start1 = start0 + 1  # 1-based inclusive
            end1 = end0 + 1

            out_name = pattern.format(
                stem=stem, i=idx + 1, i0=idx, start=start1, end=end1
            )
            out_path = output_dir / _ensure_pdf_suffix(out_name)

            if out_path.exists() and not overwrite:
                raise FileExistsError(
                    f"Output exists: {out_path}. Use overwrite=True to replace."
                )

            part_doc = fitz.open()
            part_doc.insert_pdf(src, from_page=start0, to_page=end0)
            if keep_metadata:
                try:
                    part_doc.set_metadata(src.metadata)
                except Exception:
                    pass
            part_doc.save(out_path, garbage=4, deflate=True)
            part_doc.close()
            outputs.append(out_path)

    return outputs


def find_pdfs(
    paths: Iterable[str | Path], recursive: bool = True, pattern: str = "*.pdf"
) -> List[Path]:
    """Collect PDFs from a list of files/directories.

    Parameters
    ----------
    paths : iterable of str | Path
        Input files or directories.
    recursive : bool
        Recurse into subdirectories.
    pattern : str
        Glob pattern (default: "*.pdf").
    """
    found: List[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix.lower() == ".pdf":
            found.append(p)
        elif p.is_dir():
            globber = p.rglob if recursive else p.glob
            found.extend([x for x in globber(pattern) if x.is_file()])
    # unique + stable order
    seen = set()
    unique: List[Path] = []
    for f in found:
        if f.resolve() not in seen:
            seen.add(f.resolve())
            unique.append(f)
    return unique


def split_many(
    inputs: Iterable[str | Path],
    *,
    max_pages: int = 10,
    output_dir: str | Path | None = None,
    output_pattern: str | None = None,
    recursive: bool = True,
    password: str | None = None,
    keep_metadata: bool = True,
    overwrite: bool = False,
) -> List[Path]:
    """Batch split multiple PDFs. Returns list of all produced files."""
    pdfs = find_pdfs(inputs, recursive=recursive)
    outputs: List[Path] = []
    for pdf in pdfs:
        out_dir = Path(output_dir) if output_dir else pdf.parent
        outputs.extend(
            split_pdf(
                pdf,
                max_pages=max_pages,
                output_dir=out_dir,
                output_pattern=output_pattern,
                password=password,
                keep_metadata=keep_metadata,
                overwrite=overwrite,
            )
        )
    return outputs
