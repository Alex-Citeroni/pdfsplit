from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import typer
from tqdm import tqdm

from .core import split_pdf, split_many, find_pdfs

app = typer.Typer(add_completion=False, help="Split PDF files into chunks of N pages.")


@app.command()
def split(
    input_pdf: Path = typer.Argument(
        ..., exists=True, readable=True, help="PDF sorgente"
    ),
    max_pages: int = typer.Option(10, min=1, help="Pagine massime per file"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Cartella di output"),
    pattern: Optional[str] = typer.Option(
        None, help="Pattern nome file (usa {stem},{i},{start},{end})"
    ),
    password: Optional[str] = typer.Option(None, help="Password se il PDF è cifrato"),
    overwrite: bool = typer.Option(False, help="Sovrascrivi se esiste"),
    no_metadata: bool = typer.Option(False, help="Non copiare i metadati"),
):
    """Taglia un singolo PDF in più parti."""
    outputs = split_pdf(
        input_pdf,
        max_pages=max_pages,
        output_dir=out,
        output_pattern=pattern,
        password=password,
        keep_metadata=not no_metadata,
        overwrite=overwrite,
    )
    for p in outputs:
        typer.echo(p)


@app.command()
def batch(
    paths: List[Path] = typer.Argument(..., help="File o cartelle"),
    recursive: bool = typer.Option(True, help="Cerca ricorsivamente nelle cartelle"),
    glob: str = typer.Option("*.pdf", help="Glob pattern per i PDF"),
    max_pages: int = typer.Option(10, min=1, help="Pagine massime per file"),
    out: Optional[Path] = typer.Option(
        None, "--out", "-o", help="Cartella di output comune"
    ),
    pattern: Optional[str] = typer.Option(None, help="Pattern nome file"),
    overwrite: bool = typer.Option(False, help="Sovrascrivi se esiste"),
    password: Optional[str] = typer.Option(None, help="Password per PDF cifrati"),
    no_metadata: bool = typer.Option(False, help="Non copiare i metadati"),
):
    """Processa più PDF (file e/o cartelle)."""
    pdfs = find_pdfs(paths, recursive=recursive, pattern=glob)
    if not pdfs:
        raise typer.Exit(code=0)

    produced = []
    for pdf in tqdm(pdfs, desc="Splitting", unit="file"):
        produced.extend(
            split_pdf(
                pdf,
                max_pages=max_pages,
                output_dir=out or pdf.parent,
                output_pattern=pattern,
                password=password,
                keep_metadata=not no_metadata,
                overwrite=overwrite,
            )
        )
    for p in produced:
        typer.echo(p)


def main():
    app()
