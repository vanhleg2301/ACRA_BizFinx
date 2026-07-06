"""
Generate a complete ACRA BizFinx-compatible XBRL submission package (8 files).

Files produced:
  <stem>.xbrl              ← instance document (facts + contexts + units)
  <stem>.xsd               ← company extension schema
  <stem>_pre.xml           ← presentation linkbase (empty — refs ACRA taxonomy)
  <stem>_cal.xml           ← calculation linkbase  (empty — refs ACRA taxonomy)
  <stem>_def.xml           ← definition linkbase   (empty — refs ACRA taxonomy)
  <stem>_lab.xml           ← label linkbase         (empty — refs ACRA taxonomy)
  <stem>_serialnotes.xml   ← serialised FS notes (RTF text block)
  LayoutProperty.xml       ← BizFinx filing metadata
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from acra_helper.taxonomy.namespaces import (
    NS, TAXONOMY_BASE, ACRA_ENTITY_SCHEME, LB_ROLES, TEXT_ELEMENTS,
)

# Register all prefixes so ET uses them instead of ns0/ns1/...
# xbrli must stay as an explicit prefix (not default) so xbrli:pure in measure
# content is valid — an undeclared prefix in QName text causes XBRL parse failures.
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)
ET.register_namespace("xbrldi", "http://xbrl.org/2006/xbrldi")


# ── helpers ───────────────────────────────────────────────────────────────────

def _split(element_name: str) -> tuple[str, str]:
    """'sg-as:CashAndBankBalances' → ('sg-as', 'CashAndBankBalances')"""
    if ":" in element_name:
        p, local = element_name.split(":", 1)
        return p, local
    return "sg-as", element_name


def _indent(elem: ET.Element, level: int = 0) -> None:
    """In-place pretty-print an ElementTree via whitespace text nodes."""
    pad = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
        for child in elem:
            _indent(child, level + 1)
        # last child tail
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = pad


def _serialize(root: ET.Element) -> str:
    _indent(root)
    return ET.tostring(root, encoding="unicode", xml_declaration=False)


def _write(path: Path, content: str) -> None:
    path.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + content, encoding="utf-8")


def _esc(text: str) -> str:
    """Escape XML special chars in text content."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ── context XML builder ───────────────────────────────────────────────────────

def _build_context_elem(ctx_id: str, ctx_def: dict, uen: str) -> ET.Element:
    xbrli = NS["xbrli"]
    ctx = ET.Element(f"{{{xbrli}}}context", id=ctx_id)

    entity = ET.SubElement(ctx, f"{{{xbrli}}}entity")
    ident = ET.SubElement(entity, f"{{{xbrli}}}identifier",
                          scheme=ACRA_ENTITY_SCHEME)
    ident.text = uen

    dim = ctx_def.get("dimension")
    if dim:
        seg = ET.SubElement(entity, f"{{{xbrli}}}segment")
        xd = ET.SubElement(
            seg,
            "{http://xbrl.org/2006/xbrldi}explicitMember",
            dimension=dim["axis"],
        )
        xd.text = dim["member"]

    period_def = ctx_def["period"]
    period = ET.SubElement(ctx, f"{{{xbrli}}}period")
    if period_def["type"] == "instant":
        inst = ET.SubElement(period, f"{{{xbrli}}}instant")
        inst.text = period_def["date"]
    else:
        sd = ET.SubElement(period, f"{{{xbrli}}}startDate")
        sd.text = period_def["start"]
        ed = ET.SubElement(period, f"{{{xbrli}}}endDate")
        ed.text = period_def["end"]

    return ctx


# ── instance document ─────────────────────────────────────────────────────────

def _build_instance(
    facts: list[dict],
    contexts: dict[str, dict],
    uen: str,
    currency: str,
    stem: str,
) -> str:
    xbrli = NS["xbrli"]

    root = ET.Element(f"{{{xbrli}}}xbrl")

    # schemaRef
    ET.SubElement(
        root,
        f"{{{NS['link']}}}schemaRef",
        {f"{{{NS['xlink']}}}type": "simple",
         f"{{{NS['xlink']}}}href": f"{stem}.xsd"},
    )

    # contexts — only those referenced by at least one fact
    used_ctx = {f["context"] for f in facts}
    for ctx_id, ctx_def in contexts.items():
        if ctx_id in used_ctx:
            root.append(_build_context_elem(ctx_id, ctx_def, uen))

    # units
    unit_sgd = ET.SubElement(root, f"{{{xbrli}}}unit", id=currency)
    measure = ET.SubElement(unit_sgd, f"{{{xbrli}}}measure")
    measure.text = f"iso4217:{currency}"

    unit_pure = ET.SubElement(root, f"{{{xbrli}}}unit", id="PURE")
    pm = ET.SubElement(unit_pure, f"{{{xbrli}}}measure")
    pm.text = "xbrli:pure"

    # facts
    for fact in facts:
        prefix, local = _split(fact["element"])
        ns_uri = NS.get(prefix, NS["sg-as"])
        tag = f"{{{ns_uri}}}{local}"

        is_text = local in TEXT_ELEMENTS
        value = fact.get("value", "")

        attrs: dict[str, str] = {"contextRef": fact["context"]}

        if not is_text:
            try:
                num = float(str(value))
                attrs["unitRef"] = currency
                attrs["decimals"] = "0"
                value = str(int(num)) if num == int(num) else str(num)
            except (TypeError, ValueError):
                pass

        elem = ET.SubElement(root, tag, attrs)
        elem.text = str(value)

    return _serialize(root)


# ── extension schema (.xsd) — written as string to avoid ET namespace issues ──

def _build_xsd(stem: str) -> str:
    imports = "\n".join(
        f'  <xs:import namespace="{NS[p]}"\n'
        f'             schemaLocation="{TAXONOMY_BASE}/{p}.xsd"/>'
        for p in ("sg-as", "sg-dei", "sg-ca", "sg-ssa")
    )
    linkbases = "\n".join(
        f'      <link:linkbaseRef\n'
        f'        xlink:type="simple"\n'
        f'        xlink:href="{stem}_{kind[:3]}.xml"\n'
        f'        xlink:role="{role}"\n'
        f'        xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>'
        for kind, role in [
            ("pre", LB_ROLES["presentation"]),
            ("cal", LB_ROLES["calculation"]),
            ("def", LB_ROLES["definition"]),
            ("lab", LB_ROLES["label"]),
        ]
    )
    return (
        f'<xs:schema\n'
        f'  xmlns:xs="{NS["xs"]}"\n'
        f'  xmlns:link="{NS["link"]}"\n'
        f'  xmlns:xlink="{NS["xlink"]}"\n'
        f'  elementFormDefault="qualified">\n'
        f'{imports}\n'
        f'  <xs:annotation>\n'
        f'    <xs:appinfo>\n'
        f'{linkbases}\n'
        f'    </xs:appinfo>\n'
        f'  </xs:annotation>\n'
        f'</xs:schema>'
    )


# ── empty linkbase template — written as string ───────────────────────────────

_LB_TAG = {
    "pre": "presentationLink",
    "cal": "calculationLink",
    "def": "definitionLink",
    "lab": "labelLink",
}


def _empty_linkbase(suffix: str) -> str:
    tag = _LB_TAG[suffix]
    return (
        f'<link:linkbase\n'
        f'  xmlns:link="{NS["link"]}"\n'
        f'  xmlns:xlink="{NS["xlink"]}"\n'
        f'  xmlns:xsi="{NS["xsi"]}"\n'
        f'  xsi:schemaLocation="{NS["link"]} '
        f'http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">\n'
        f'  <link:{tag}\n'
        f'    xlink:type="extended"\n'
        f'    xlink:role="http://www.xbrl.org/2003/role/link"/>\n'
        f'</link:linkbase>'
    )


# ── serialnotes.xml ───────────────────────────────────────────────────────────

def _build_serialnotes(facts: list[dict], fye_str: str) -> str:
    rtf_value = ""
    for f in facts:
        if "DisclosureOfCompleteSetOfFinancialStatementsTextBlock" in f["element"]:
            rtf_value = _esc(str(f.get("value", "")))
            break
    return (
        f'<SerialNotes>\n'
        f'  <Note period="{fye_str}">{rtf_value or "(No financial statements text provided)"}</Note>\n'
        f'</SerialNotes>'
    )


# ── LayoutProperty.xml ────────────────────────────────────────────────────────

def _build_layout(uen: str, name: str, fye_str: str, currency: str, address: str = "") -> str:
    addr_line = f'  <PrincipalPlaceOfBusiness>{_esc(address)}</PrincipalPlaceOfBusiness>\n' if address else ""
    return (
        f'<LayoutProperty>\n'
        f'  <UEN>{_esc(uen)}</UEN>\n'
        f'  <CompanyName>{_esc(name)}</CompanyName>\n'
        f'  <FiscalYearEnd>{fye_str}</FiscalYearEnd>\n'
        f'  <Currency>{currency}</Currency>\n'
        f'  <TaxonomyVersion>Full_XBRL_2026_v1.0</TaxonomyVersion>\n'
        f'  <FilingType>Full XBRL</FilingType>\n'
        f'  <GeneratedBy>ACRA XBRL Pre-Filler</GeneratedBy>\n'
        f'{addr_line}'
        f'</LayoutProperty>'
    )


# ── public entry point ────────────────────────────────────────────────────────

def write_xbrl_package(
    facts: list[dict],
    contexts: dict[str, dict],
    output_dir: Path,
    uen: str,
    name: str,
    fye: date,
    currency: str = "SGD",
    address: str = "",
) -> Path:
    """
    Generate all 8 XBRL files into output_dir/<uen>_<year>/.
    Returns the package directory.
    """
    year = fye.year
    fye_str = fye.isoformat()
    stem = f"{uen}_{year}"

    pkg_dir = output_dir / stem
    pkg_dir.mkdir(parents=True, exist_ok=True)

    _write(pkg_dir / f"{stem}.xbrl",
           _build_instance(facts, contexts, uen, currency, stem))
    _write(pkg_dir / f"{stem}.xsd",
           _build_xsd(stem))
    for suffix in ("pre", "cal", "def", "lab"):
        _write(pkg_dir / f"{stem}_{suffix}.xml", _empty_linkbase(suffix))
    _write(pkg_dir / f"{stem}_serialnotes.xml",
           _build_serialnotes(facts, fye_str))
    _write(pkg_dir / "LayoutProperty.xml",
           _build_layout(uen, name, fye_str, currency, address))

    return pkg_dir
