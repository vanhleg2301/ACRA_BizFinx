"""
Parse a Word (.docx) financial statements file.

Extracts:
- text_blocks: {heading -> [paragraph text, ...]}  (sections by Heading style)
- tables: list of 2-D arrays (list of rows, each row is list of cell strings)
- full_text: concatenated plain text (for RTF builder)
"""
from pathlib import Path

import docx


def parse_word(path: Path) -> dict:
    doc = docx.Document(str(path))

    text_blocks: dict[str, list[str]] = {}
    current_heading = "__preamble__"
    tables_by_heading: dict[str, list] = {}

    for block in doc.element.body:
        tag = block.tag.split("}")[-1] if "}" in block.tag else block.tag

        if tag == "p":
            para = docx.text.paragraph.Paragraph(block, doc)
            style = (para.style.name or "").lower()
            text = para.text.strip()

            if style.startswith("heading"):
                current_heading = text or current_heading
                text_blocks.setdefault(current_heading, [])
            elif text:
                text_blocks.setdefault(current_heading, []).append(text)

        elif tag == "tbl":
            table = docx.table.Table(block, doc)
            rows = [
                [cell.text.strip() for cell in row.cells]
                for row in table.rows
            ]
            tables_by_heading.setdefault(current_heading, []).append(rows)

    full_text = "\n".join(
        f"\n{heading}\n" + "\n".join(lines)
        for heading, lines in text_blocks.items()
        if lines
    )

    return {
        "text_blocks": text_blocks,
        "tables": tables_by_heading,
        "full_text": full_text,
    }
