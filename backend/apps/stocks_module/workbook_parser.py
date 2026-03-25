from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET


MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


@dataclass(frozen=True)
class WorkbookStockRow:
    market_code: str
    source_sector: str
    company_name: str
    symbol: str


def parse_stock_workbook(path: str | Path) -> list[WorkbookStockRow]:
    workbook_path = Path(path)
    rows: list[WorkbookStockRow] = []

    with zipfile.ZipFile(workbook_path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}

        for sheet in workbook.find(f"{MAIN_NS}sheets"):
            sheet_name = sheet.attrib.get("name", "")
            if sheet_name.startswith("IND "):
                market_code = "IN"
            elif sheet_name.startswith("USA "):
                market_code = "US"
            else:
                continue

            relationship_id = sheet.attrib.get(f"{REL_NS}id")
            target = relationship_map[relationship_id].lstrip("/")
            if not target.startswith("xl/"):
                target = f"xl/{target}"

            worksheet = ET.fromstring(archive.read(target))
            sheet_rows = worksheet.find(f"{MAIN_NS}sheetData")
            if sheet_rows is None:
                continue

            source_sector = _source_sector_name(sheet_name)
            for row in list(sheet_rows.findall(f"{MAIN_NS}row"))[2:]:
                cells = row.findall(f"{MAIN_NS}c")
                if len(cells) < 2:
                    continue

                company_name = _cell_text(cells[0])
                symbol = _cell_text(cells[1])
                if not company_name or not symbol:
                    continue

                rows.append(
                    WorkbookStockRow(
                        market_code=market_code,
                        source_sector=source_sector,
                        company_name=company_name.strip(),
                        symbol=symbol.strip(),
                    )
                )

    return rows


def _source_sector_name(sheet_name: str) -> str:
    if "—" in sheet_name:
        return sheet_name.split("—", 1)[1].strip()
    if "-" in sheet_name:
        return sheet_name.split("-", 1)[1].strip()
    return sheet_name.strip()


def _cell_text(cell) -> str | None:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find(f"{MAIN_NS}is")
        if inline is None:
            return None
        return "".join(node.text or "" for node in inline.iter(f"{MAIN_NS}t"))

    value = cell.find(f"{MAIN_NS}v")
    if value is None:
        return None
    return value.text
