from ..xlsx.workbook import *
from ..xlsx.xmlutils import *


def test():
    wb = Workbook.from_file('./data/test.xlsx')
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
    print(type(sheets.attrib))

    for sheet in sheets:
        print(sheet.attrib)
        name = sheet.get('name')
        sheet_id = sheet.get('sheetId')
        rid = sheet.get(XmlName(sheets.nsmap['r'], 'id'))
        print(f'{name=} {sheet_id=} {rid=}')


def test_xmlelement():
    elem = XmlElement.new('sheets',
                          nsmap={None: 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
    subelem = XmlElement.new('sheet', {'name': "Sheet1"})
    elem.append(subelem)
    subelem.attrib['sheetId'] = '1'
    subelem.attrib[XmlName(elem.nsmap['r'], 'id')] = 'rId1'

    print(elem)
    print(subelem.get(XmlName(elem.nsmap['r'], 'id')))
    print(elem.nsmap)
    print(subelem.nsmap)
    print(XmlName(None, 'id'))
    print(XmlName('abc', 'id'))
    
    print(subelem)
    subelem.remove_attrib('id')
    print(subelem)
    subelem.remove_attrib(XmlName(subelem.nsmap['r'], 'id'))
    print(subelem)


#test()
test_xmlelement()
