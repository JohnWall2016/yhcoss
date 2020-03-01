from ..excel import openpyxl as xlsx

wb = xlsx.open('')
sheet = wb.worksheets[0]
wb.save()