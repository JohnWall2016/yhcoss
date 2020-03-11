from ..excel.xls import Workbook

workbook = Workbook('./data/test.xls')
sheet = workbook.get_sheet(0)
sheet.update(1, 4, '刘德华')
row = sheet.copy_row_to(1, 2)
row.update(4, '马德华')
workbook.save('./data/test2.xls')
