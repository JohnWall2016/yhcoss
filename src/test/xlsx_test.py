from ..excel.xls import Workbook

workbook = Workbook('./data/test.xls')
sheet = workbook.get_sheet(0)
print(sheet.row(1).value(2))
print(sheet.row(1).value('E'))
sheet.update(2, 5, '刘德华')
sheet.update(2, 'B', 123456)
row = sheet.copy_row(2, 3)
row.update(5, '马德华')
row.update('B', 244567)
workbook.save('./data/test2.xls')
