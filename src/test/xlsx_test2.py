from ..xlsx.workbook import *
from ..xlsx.xmlutils import *
from typing import *

def test():
    wb = Workbook.from_file('./data/test.xlsx')
    print(f'{wb=}')
    sheets = wb.find('sheets')
    print(f'{sheets=}')

    for c in wb:
        print(f'{type(c.tag)=} {c.tag=}')

    print(f'{wb.nsmap=}')
    sheets = wb.find('sheets', wb.nsmap)
    print(XmlName(sheets._element))
    print(f'{sheets=}')
    print(f'{sheets.tostring(encoding="unicode")=}')

    print(sheets.tag)
    print(type(sheets.tag))
    print(sheets.tag.localname)
    print(sheets.tag.namespace)

    print(sheets.nsmap)
    print(sheets.attrib)
    print(type(sheets.attrib))

    for sheet in sheets:
        print(sheet.attrib)
        name = sheet.get_attrib_value('name')
        sheet_id = sheet.get_attrib_value('sheetId')
        rid = sheet.get_attrib_value(XmlName(sheets.nsmap['r'], 'id'))
        print(f'{name=} {sheet_id=} {rid=}')


def test_xmlelement():
    elem = XmlElement.new('sheets',
                          nsmap={None: 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
    subelem = XmlElement.new('sheet', {'name': "Sheet1"})
    elem.append(subelem)
    subelem.attrib['sheetId'] = '1'
    subelem.attrib[XmlName(elem.nsmap['r'], 'id')] = 'rId1'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    subelem.attrib[XmlName(xml_ns, 'space')] = 'preserve'

    for k, v in subelem.attrib.items():
        print(f'{XmlName(k).localname=}, {v=}')

    print(elem)
    print(subelem.get_attrib_value(XmlName(elem.nsmap['r'], 'id')))
    print(elem.nsmap)
    print(subelem.nsmap)
    print(XmlName(None, 'id'))
    print(XmlName('abc', 'id'))
    
    subelem.text = 'abcedfg'
    print(subelem)
    subelem.remove_attrib('sheetId')
    subelem.remove_attrib('id')
    print(subelem)
    subelem.remove_attrib(XmlName(subelem.nsmap['r'], 'id'))
    print(subelem)

def test_workbook():
    wb = Workbook.from_file('./data/test.xlsx')
    print(wb.shared_strings._strlist)
    print(wb.shared_strings._idxdict)
    print(len(wb))

    sheet = wb[0]
    print(sheet.last_row_index)
    print(sheet.name)
    print(sheet[3].cell('C').value())
    print(sheet.cell('A1').value())

    sheet = wb.sheet('Sheet1')
    print(sheet.cell_at(3, 4).value())

def test_remove():
    elem = XmlElement.new('abc')
    elem.append(XmlElement.new('efg'))
    print(elem)
    subelem = elem.find_by_localname('efg')
    print(subelem)
    if subelem._element is None:
        print('subelem is True')
    else:
        print('subelem is False')
    elem.remove('efg')
    print(elem)
    print(subelem)

def test_xmlname():
    nsmap: Dict[Optional[str], str]={'ab': 'abcdefg'}
    e = XmlElement.new('abc', nsmap=nsmap)
    f = XmlElement.new('{abcdefg}efg')
    e.append(f)
    f.addprevious(XmlElement.new('hij'))
    print(e)

    print(e.find('hij'))
    print(e.find('hij', nsmap))
    print(e.find_by_localname('hij'))
    
    print(e.find('{abcdefg}efg'))
    print(e.find('ab:efg', nsmap))
    print(e.find_by_localname('efg'))

    xmlns = XmlNamespace({
                None: 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
                'x14ac': 'http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac'
            })
    print(xmlns.tag('mc', 'Ignorable'))
    e = XmlElement.new(
                'worksheet',
                attrib={xmlns.tag('mc', 'Ignorable'): 'x14ac'},
                nsmap=xmlns.nsmap)
    print(e)


def test_save():
    wb = Workbook.from_file('./data/test.xlsx')
    wb[0].cell('B4').value = '刘德华'
    wb.save_file('./data/test2.xlsx')

#test()
#test_xmlelement()
#test_workbook()
#test_remove()
#test_xmlname()
test_save()