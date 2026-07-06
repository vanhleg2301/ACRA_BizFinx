"""
Build the RTF for DisclosureOfCompleteSetOfFinancialStatementsTextBlock.

BizFinx renders this text block verbatim, so it must preserve the layout of the
signed financial statements (tables, headings, indentation). The preferred path
converts the source .docx to RTF with LibreOffice (full fidelity); when
LibreOffice is unavailable we fall back to a minimal plain-text RTF.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _find_soffice() -> str | None:
    """Locate the LibreOffice binary via env override, PATH, or default install dirs."""
    env = os.environ.get("SOFFICE_PATH")
    if env and Path(env).exists():
        return env
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "LibreOffice" / "program" / "soffice.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "LibreOffice" / "program" / "soffice.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "LibreOffice" / "program" / "soffice.exe",
    ]
    for c in candidates:
        if str(c) and c.exists():
            return str(c)
    return None


def convert_docx_to_rtf(docx_path: Path) -> str | None:
    """Convert a .docx to RTF via LibreOffice, preserving tables and formatting.

    Returns the RTF string, or None if LibreOffice is unavailable or the
    conversion fails (caller should fall back to build_rtf).
    """
    soffice = _find_soffice()
    if not soffice:
        return None

    with tempfile.TemporaryDirectory() as tmp:
        # Isolated user profile avoids clashing with a running LibreOffice instance.
        profile = Path(tmp) / "profile"
        try:
            subprocess.run(
                [
                    soffice,
                    f"-env:UserInstallation=file:///{profile.as_posix()}",
                    "--headless",
                    "--convert-to",
                    "rtf",
                    "--outdir",
                    tmp,
                    str(docx_path),
                ],
                capture_output=True,
                timeout=120,
                check=True,
            )
        except (subprocess.SubprocessError, OSError):
            return None

        out = Path(tmp) / (docx_path.stem + ".rtf")
        if not out.exists():
            return None
        return out.read_text(encoding="utf-8", errors="replace")


def _escape_rtf(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    # Non-ASCII → Unicode escape
    out = []
    for ch in text:
        if ord(ch) > 127:
            out.append(f"\\u{ord(ch)}?")
        else:
            out.append(ch)
    return "".join(out)


def build_rtf(full_text: str) -> str:
    """Convert plain text to a minimal RTF document string."""
    lines = full_text.split("\n")
    rtf_body_parts = []
    for line in lines:
        escaped = _escape_rtf(line)
        rtf_body_parts.append(escaped + "\\par")

    body = "\n".join(rtf_body_parts)
    return (
        r"{\rtf1\ansi\deff0"
        r"{\fonttbl{\f0\froman\fcharset0 Times New Roman;}}"
        r"{\colortbl ;}"
        r"\f0\fs24 "
        + body
        + r"}"
    )
