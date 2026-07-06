"""
Test that xbrl_writer generates valid, well-formed XML for all 8 files
using the EVX seed data as input.
"""
import json
import tempfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def seed_facts() -> list[dict]:
    data = json.loads((FIXTURES / "fact_map_seed.json").read_text(encoding="utf-8"))
    return data["facts"]


@pytest.fixture(scope="module")
def seed_contexts() -> dict:
    return json.loads((FIXTURES / "contexts.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def xbrl_package(seed_facts, seed_contexts) -> Path:
    from acra_helper.generate.xbrl_writer import write_xbrl_package

    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = write_xbrl_package(
            facts=seed_facts,
            contexts=seed_contexts,
            output_dir=Path(tmp),
            uen="201631437H",
            name="EVX VENTURES PTE. LTD.",
            fye=date(2025, 12, 31),
            currency="SGD",
        )
        # read files before tempdir is cleaned up
        return {f.name: f.read_text(encoding="utf-8") for f in pkg_dir.iterdir()}


class TestPackageStructure:
    def test_all_8_files_present(self, xbrl_package):
        names = set(xbrl_package.keys())
        assert "201631437H_2025.xbrl" in names
        assert "201631437H_2025.xsd" in names
        assert "201631437H_2025_pre.xml" in names
        assert "201631437H_2025_cal.xml" in names
        assert "201631437H_2025_def.xml" in names
        assert "201631437H_2025_lab.xml" in names
        assert "201631437H_2025_serialnotes.xml" in names
        assert "LayoutProperty.xml" in names


class TestInstanceDocument:
    def test_well_formed_xml(self, xbrl_package):
        ET.fromstring(xbrl_package["201631437H_2025.xbrl"])  # raises if malformed

    def test_contains_uen(self, xbrl_package):
        assert "201631437H" in xbrl_package["201631437H_2025.xbrl"]

    def test_contains_numeric_fact(self, xbrl_package):
        assert "6554" in xbrl_package["201631437H_2025.xbrl"]   # CashAndBankBalances 2025
        assert "37708" in xbrl_package["201631437H_2025.xbrl"]  # CashAndBankBalances 2024

    def test_contains_context_refs(self, xbrl_package):
        xml = xbrl_package["201631437H_2025.xbrl"]
        assert "asof_20251231" in xml
        assert "fromto_20250101_20251231" in xml

    def test_negative_value_preserved(self, xbrl_package):
        # TradeAndOtherPayablesCurrent = -22491
        assert "-22491" in xbrl_package["201631437H_2025.xbrl"]

    def test_ppe_dimension_context(self, xbrl_package):
        assert "ComputerOfficeEquipmentAndFurnitureFixturesAndFittingsMember" in \
               xbrl_package["201631437H_2025.xbrl"]


class TestSchema:
    def test_well_formed_xml(self, xbrl_package):
        ET.fromstring(xbrl_package["201631437H_2025.xsd"])

    def test_references_acra_taxonomy(self, xbrl_package):
        assert "acra.gov.sg" in xbrl_package["201631437H_2025.xsd"]

    def test_references_all_linkbases(self, xbrl_package):
        xsd = xbrl_package["201631437H_2025.xsd"]
        for suffix in ("_pre", "_cal", "_def", "_lab"):
            assert f"201631437H_2025{suffix}.xml" in xsd


class TestLinkbases:
    @pytest.mark.parametrize("fname", [
        "201631437H_2025_pre.xml",
        "201631437H_2025_cal.xml",
        "201631437H_2025_def.xml",
        "201631437H_2025_lab.xml",
    ])
    def test_well_formed(self, xbrl_package, fname):
        ET.fromstring(xbrl_package[fname])


class TestLayoutProperty:
    def test_well_formed_xml(self, xbrl_package):
        ET.fromstring(xbrl_package["LayoutProperty.xml"])

    def test_contains_uen_and_name(self, xbrl_package):
        lp = xbrl_package["LayoutProperty.xml"]
        assert "201631437H" in lp
        assert "EVX VENTURES" in lp
