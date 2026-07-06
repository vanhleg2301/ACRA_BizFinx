"""
Build a minimal RTF string from plain text (for DisclosureOfCompleteSetOfFinancialStatementsTextBlock).

RTF is required by BizFinx for the full FS text block.
We produce clean, BizFinx-compatible RTF: no images, no complex formatting.
"""


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
