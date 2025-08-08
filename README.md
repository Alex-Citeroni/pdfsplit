# pdfsplit

Split PDF files into fixed-size page chunks via CLI or Python API.

## Install (dev)
```bash
# in repository root
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## Usage

### CLI
```bash
pdfsplit split input.pdf --max-pages 10 --out outdir
# batch mode on a folder
pdfsplit batch ./docs --glob "**/*.pdf" --max-pages 8 --out ./out
# custom naming
pdfsplit split input.pdf --pattern "{stem}_p{start:03d}-to-{end:03d}.pdf"
```

### Python API
```bash
from pdfsplit import split_pdf

paths = split_pdf("input.pdf", max_pages=10, output_dir="out")
print(paths)
```

## Filename placeholders

- `{stem}`: input filename without extension

- `{i}` / `{i0}`: chunk index (1-based / 0-based)

- `{start}` / `{end}`: 1-based page numbers included in the chunk

## Notes

- Encrypted PDFs are supported via `--password`.

- Outputs are compressed and cleaned (`garbage=4, deflate=True`).

## Development
```bash
ruff check .
pytest
```