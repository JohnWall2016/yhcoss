from ..xlsx.workbook import *
from ..xlsx.xmlutils import *

wb = Workbook.from_file('/Users/wangjiong/Downloads/信息核对报告表模板.xlsx')
print(f'{wb=}')
sheets = wb.find('sheets')
print(f'{sheets=}')

for c in wb:
    print(f'{c.tag=}')

print(f'{wb.nsmap=}')
sheets = wb.find('sheets', wb.nsmap)
print(f'{sheets=}')
print(f'{sheets.tostring(encoding="unicode")=}')

print(sheets.nsmap)
print(sheets.attrib)

for sheet in sheets:
    print(sheet.attrib)
    name = sheet.get('name')
    sheet_id = sheet.get('sheetId')
    rid = sheet.get('id', sheets.nsmap)
    print(f'{name=} {sheet_id=} {rid=}')


