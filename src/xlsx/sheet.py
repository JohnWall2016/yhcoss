from typing import Optional, Dict, List, Final

from .address_converter import RangeRef, CellRef
from .relationships import Relationships
from .xmlutils import XmlElement, try_parse

from .row import *

import src.xlsx.workbook as wb


class Sheet(XmlElement):
    namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

    def __init__(self, workbook: 'wb.Workbook', id: XmlElement, element: Optional[XmlElement],
                 relationships: Optional[XmlElement]):
        if element is None:
            element = XmlElement.new(
                'worksheet',
                attrib={'mc:Ignorable': 'x14ac'},
                nsmap={
                    None: self.namespace,
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
                    'x14ac': 'http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac'
                })
            element.append(XmlElement.new('sheetData'))
        super().__init__(element)
        self._workbook = workbook
        self._id = id
        self._relationships = Relationships(relationships)
        self._max_shared_formula_id = -1
        self.remove('dimension')

        self._sheet_data_elem = self.find_by_localname('sheetData')
        if self._sheet_data_elem is not None:
            self.remove(self._sheet_data_elem)
        self._last_row_index = -1
        self._rows: Dict[int, Row] = {}
        for r in self._sheet_data_elem:
            row = Row(self, r)
            index = row.index
            if index > self._last_row_index:
                self._last_row_index = index
                self._rows[index] = row
        self._sheet_data_elem.clear()

        self._cols: Dict[int, XmlElement] = {}
        self._cols_elem = self.find_by_localname('cols')
        if self._cols_elem is not None:
            self.remove(self._cols_elem)
        else:
            self._cols_elem = XmlElement.new('cols')
        for col in self._cols_elem:
            min = col.get_attrib_value('min')
            max = col.get_attrib_value('max')
            min = int(min) if min else None
            max = int(max) if max else None
            if min is not None and max is not None:
                for i in range(min, max + 1):
                    self._cols[i] = col
        self._cols_elem.clear()

        self._sheet_pr_elem = self.find_by_localname('sheetPr')
        if self._sheet_pr_elem is None:
            self._sheet_pr_elem = XmlElement.new('sheetPr')
            self.insert_in_order(self._sheet_pr_elem, element_order)

        self._emerge_cells: Dict[RangeRef, XmlElement] = {}
        self._emerge_cells_elem = self.find_by_localname('mergeCells')
        if self._emerge_cells_elem is not None:
            self.remove(self._emerge_cells_elem)
        else:
            self._emerge_cells_elem = XmlElement.new('mergeCells')
        for merge_cell in self._emerge_cells_elem:
            ref = merge_cell.get_attrib_value('ref')
            if ref is not None:
                range_ref = RangeRef.from_address(ref)
                if range_ref is not None:
                    self._emerge_cells[range_ref] = merge_cell
        self._emerge_cells_elem.clear()

        self._data_validations: Dict[str, XmlElement] = {}
        self._data_validations_elem = self.find_by_localname('dataValidations')
        if self._data_validations_elem is not None:
            self.remove(self._data_validations_elem)
        else:
            self._data_validations_elem = XmlElement.new('dataValidations')
        for data_validation in self._data_validations_elem:
            self._data_validations['sqref'] = data_validation
        self._data_validations_elem.clear()

        self._hyper_links: Dict[str, XmlElement] = {}
        self._hyper_links_elem = self.find_by_localname('hyperlinks')
        if self._hyper_links_elem is not None:
            self.remove(self._hyper_links_elem)
        else:
            self._hyper_links_elem = XmlElement.new('hyperlinks')
        for hyper_link in self._hyper_links_elem:
            ref = self._hyper_links_elem.get_attrib_value('ref')
            if ref:
                self._hyper_links[ref] = hyper_link
        self._hyper_links_elem.clear()
            
    @property
    def workbook(self) -> 'wb.Workbook':
        return self._workbook

    @property
    def name(self):
        return self._id.get_attrib_value('name')

    @name.setter
    def name(self, value: str):
        self._id.attrib['name'] = value

    @property
    def last_row_index(self):
        return self._last_row_index

    def __getitem__(self, index: int) -> 'Row':
        if index in self._rows:
            return self._rows[index]
        row_elem = XmlElement.new('row', {'r':str(index)})
        row = Row(self, row_elem)
        self._rows[index] = row
        if index > self._last_row_index:
            self._last_row_index = index
        return row

    def cell_at(self, row: int, column: int) -> 'Cell':
        return self[row][column]

    def cell(self, name: str) -> Optional['Cell']:
        ref = CellRef.from_address(name)
        if ref is not None:
            return self.cell_at(ref.row, ref.column)
        return None

    def update_max_shared_formula_id(self, shared_formula_id: int):
        if shared_formula_id > self._max_shared_formula_id:
            self._max_shared_formula_id = shared_formula_id

    def existing_column_style_id(self, column: int) -> Optional[int]:
        col = self._cols.get(column)
        if col is not None:
            style = col.get_attrib_value('style')
            if style:
                return try_parse(int, style)
        return None

    def insert_row(self, index: int, row_elem: XmlElement = None, copy_index: int = None):
        if row_elem is None:
            row_elem = XmlElement.new('row', {'r':str(index)})
        row = Row(self, row_elem)
        if index <= self._last_row_index:
            for i in range(self._last_row_index, index - 1, -1):
                r = self._rows.get(i)
                if r is not None:
                    r.index = i + 1
                    self._rows[i + 1] = r
            self._last_row_index += 1
        self._rows[index] = row
        if index > self._last_row_index:
            self._last_row_index = index

        merge_cells: Dict[RangeRef, XmlElement] = {}
        for ref, elem in self._emerge_cells.items():
            if index <= ref.start.row:
                ref.start.row += 1
            if index <= ref.end.row:
                ref.end.row += 1
            elem.attrib['ref'] = ref.to_address()
            if copy_index is not None:
                if ref.start.row == copy_index and ref.end.row == copy_index:
                    range_ref = RangeRef(index, ref.start.column, index, ref.end.column)
                    merge_cells[range_ref] = XmlElement.new('mergeCell', {'ref': range_ref.to_address()})
        if merge_cells:
            self._emerge_cells.update(merge_cells)
        return row

    def insert_row_copy_from(self, index: int, copy_index: int, clear_value: bool = False) -> 'Row':
        copy_row = self._rows.get(copy_index)
        if copy_row is None:
            return self.insert_row(index)
        return self.insert_row(index, copy_row.to_xml(index, clear_value), copy_index)

    def copy_row_to(self, copy_index: int, to_index: int, clear_value: bool = False) -> 'Row':
        if copy_index == to_index:
            return self[copy_index]
        else:
            return self.insert_row_copy_from(to_index, copy_index, clear_value)
    
    def to_xmls(self) -> Dict[str, XmlElement]:
        elem = self.deepcopy()

        cols: List[XmlElement] = []
        for i in sorted(self._cols):
            col = self._cols[i]
            if i == col.get_attrib_value('min') and len(col.attrib) > 2:
                cols.append(col.deepcopy())
        self._cols_elem.clear()
        cols_elem = self._cols_elem.deepcopy()
        cols_elem.append_all(cols)
        if len(cols_elem) > 0:
            elem.insert_in_order(cols_elem, element_order)
        
        self._sheet_data_elem.clear()
        sheet_data_elem = self._sheet_data_elem.deepcopy()
        for i in sorted(self._rows):
            sheet_data_elem.append(self._rows[i].to_xml())
        if len(sheet_data_elem) > 0:
            elem.insert_in_order(sheet_data_elem, element_order)

        self._hyper_links_elem.clear()
        hyper_links_elem = self._hyper_links_elem.deepcopy()
        hyper_links_elem.append_all((v.deepcopy() for v in self._hyper_links.values()))
        if len(hyper_links_elem) > 0:
            elem.insert_in_order(hyper_links_elem, element_order)

        self._emerge_cells_elem.clear()
        emerge_cells_elem = self._emerge_cells_elem.deepcopy()
        emerge_cells_elem.append_all((v.deepcopy() for v in self._emerge_cells.values()))
        if len(emerge_cells_elem) > 0:
            elem.insert_in_order(emerge_cells_elem, element_order)

        self._data_validations_elem.clear()
        data_validations_elem = self._data_validations_elem.deepcopy()
        data_validations_elem.append_all((v.deepcopy() for v in self._data_validations.values()))
        if len(data_validations_elem) > 0:
            elem.insert_in_order(data_validations_elem, element_order)

        return {
            'id': self._id,
            'sheet': elem,
            'relationships': self._relationships
        }


element_order: Final = [
    "sheetPr",
    "dimension",
    "sheetViews",
    "sheetFormatPr",
    "cols",
    "sheetData",
    "sheetCalcPr",
    "sheetProtection",
    "autoFilter",
    "protectedRanges",
    "scenarios",
    "autoFilter",
    "sortState",
    "dataConsolidate",
    "customSheetViews",
    "mergeCells",
    "phoneticPr",
    "conditionalFormatting",
    "dataValidations",
    "hyperlinks",
    "printOptions",
    "pageMargins",
    "pageSetup",
    "headerFooter",
    "rowBreaks",
    "colBreaks",
    "customProperties",
    "cellWatches",
    "ignoredErrors",
    "smartTags",
    "drawing",
    "drawingHF",
    "picture",
    "oleObjects",
    "controls",
    "webPublishItems",
    "tableParts",
    "extLst"
]