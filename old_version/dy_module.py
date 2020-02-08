"""
待遇模块
"""

from session import Session, DefaultSession

from excel.xlrd import open_workbook
from excel.xlutils.copy import copy

from datetime import date as Date


class DyModSession(Session):
    """
    待遇模块操作会话
    """
    def dyfh_query(self, shzt='0', pageno=1, pagesize=500):
        """
        到龄待遇审核查询
        """
        params = '"aaf013":"","aaf030":"","aae016":"{shzt}","aae011":"","aae036":"",' \
                 '"aae036s":"","aae014":"","aae015":"","aae015s":"","aac009":"",' \
                 '"aac002":"","aac003":"","page":{pageno},"pagesize":{pagesize},' \
                 '"filtering":[],"sorting":[{{"dataKey":"aaa027","sortDirection":"ascending"}}],' \
                 '"totals":[]'
        self.post_service_content('dyfhQuery', params.format(**locals()))
        return self.parse(self.read_body())


def export_dldysh(filename):
    """
    导出到龄待遇审核人员名单
    """
    with DefaultSession(DyModSession) as session:
        xlsbook = open_workbook(filename, formatting_info=1)
        book = copy(xlsbook)
        sheet = book.get_sheet(0)

        begindex = rowindex = 2

        date = Date.today().strftime('%Y%m%d')
        #datecn = Date.today().strftime('%Y年%#m月')
        datecn = Date.today().strftime('%Y{0}%#m{1}').format(*'年月')
        
        title = "雨湖区居保%s新增待遇领取人员审核名单" % datecn
        sheet.update(0, 0, title)

        js = session.dyfh_query()
        for data in js['datas']:
            if data.get('aac002'):
                xzqh = data['aaa027']     #行政区划
                name = data['aac003']
                idcard = data['aac002']
                csrq = data['aac006']
                ksxsny = data['aic160']   #开始享受月份
                yljdy = data['aic166']    #养老金待遇
                
                dlrq = data['aic162']     #到龄日期
                dysjksyf = data['aic160'] #待遇时间开始月份
                dyyf = data['aae211']     #财务月份

                memo = ''
                if idcard[6:12] < '195107':
                    memo = '补报补建'
                else:
                    dln = dlrq // 100
                    dly = dlrq % 100
                    if dly == 12:
                        dln += 1
                        dly = 1
                    else:
                        dly += 1
                    if dln * 100 + dly < dysjksyf:
                        memo = '补缴补建'
                memo2 = '待遇补发' if dysjksyf < dyyf else ''
                if not memo:
                    memo = memo2
                elif memo2:
                    memo += ',' + memo2

                if rowindex > begindex:
                    sheet.insert_row(rowindex)
                    #sheet.copy_row(rowindex - 1, rowindex)
                    sheet.copy_row_style(begindex, rowindex)

                print("%4d: %5s %20s" % (rowindex-begindex+1, name, idcard))

                sheet.update(rowindex, 0, rowindex-begindex+1)
                sheet.update(rowindex, 1, xzqh)
                sheet.update(rowindex, 2, name)
                sheet.update(rowindex, 3, idcard)
                sheet.update(rowindex, 4, csrq)
                sheet.update(rowindex, 5, ksxsny)
                sheet.update(rowindex, 6, yljdy)
                sheet.update(rowindex, 7, memo)

                rowindex += 1

        dir = filename.rfind('\\')
        if dir > -1:
            tofilename = filename[0:dir+1] + title + date + '.xls'
        else:
            tofilename = title + date + '.xls'

        book.save(tofilename)


from collections import OrderedDict

def split_to_sheets(filename):
    """
    将导出名单进行分表
    """
    xzqh_map = OrderedDict([
        ("长城乡", "长城"),
        ("昭潭街道", "昭潭"),
        ("先锋街道", "先锋"),
        ("万楼街道", "万楼"),
        ("鹤岭镇", "鹤岭"),
        ("楠竹山镇", "楠竹山"),
        ("姜畲镇", "姜畲"),
        ("响塘镇", "响塘"),
        ("城正街街道", "城正街"),
        ("雨湖路街道", "雨湖路"),
        ("平政路街道", "平政路"),
        ("云塘街道", "云塘"),
        ("中山路街道", "中山路"),
        ("窑湾街道", "窑湾"),
        ("广场街道", "广场"),
        ("羊牯塘街道", "羊牯塘")
        ])
    xlsbook = open_workbook(filename, formatting_info=1)
    sheet = xlsbook.sheet_by_index(0)
    book = copy(xlsbook)
    
    begindex = 2
    endindex = sheet.nrows

    print('%d -> %d' % (begindex, endindex))
    datas_map = OrderedDict()

    for i in range(begindex, endindex):
        xzqh = sheet.row_values(i)[1]
        for key in xzqh_map.keys():
            if xzqh.find(key) >= 0:
                if datas_map.get(key):
                    datas_map[key].append(i)
                else:
                    datas_map[key] = [i]
                break

    copy_sheet_index = 1
    date = Date.today().strftime('%Y%m%d')
    #datecn = Date.today().strftime('%Y年%#m月')
    datecn = Date.today().strftime('%Y{0}%#m{1}').format(*'年月')

    for key in datas_map.keys():
        print('%s -> %s' % (key, datas_map[key]))
        
        newsheet = book.copy_sheet(copy_sheet_index, xzqh_map[key])
        title = '雨湖区居保%s新增待遇领取人员审核名单' % datecn
        newsheet.update(0, 0, title)
        dwname = '       单位名称：%s' % key
        newsheet.update(1, 0, dwname)
        zbdate = '制表时间：%s' % date
        newsheet.update(1, 7, zbdate)

        rowindex = 3
        begindex = 18
        for i in datas_map[key]:
            if rowindex > 18:
                newsheet.insert_row(rowindex)
                newsheet.copy_row_style(begindex, rowindex)
            newsheet.update(rowindex, 0, rowindex - 2)
            values = sheet.row_values(i)
            newsheet.update(rowindex, 1, values[1])
            newsheet.update(rowindex, 2, values[2])
            newsheet.update(rowindex, 3, values[3])
            newsheet.update(rowindex, 4, values[4])
            newsheet.update(rowindex, 5, values[5])
            newsheet.update(rowindex, 6, values[6])
            newsheet.update(rowindex, 9, values[7])
            rowindex += 1

    book.del_sheet(copy_sheet_index)
    book.save(filename)
        

if __name__ == '__main__':
    #export_dldysh('D:\\银行数据\\社保卡开卡\\雨湖区居保新增待遇领取人员审核名单.xls')
    split_to_sheets('D:\\银行数据\\社保卡开卡\\雨湖区居保2016年10月新增待遇领取人员审核名单20161011.xls')
