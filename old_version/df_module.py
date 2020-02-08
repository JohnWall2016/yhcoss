"""
代发模块
"""

from session import Session, DefaultSession

from excel.xlrd import open_workbook
from excel.xlutils.copy import copy

from datetime import date as Date

import re


class DfModSession(Session):
    """
    代发模块操作会话
    """
    def execute_dfrymd_query(self, dftype, idcard, dfcbstate, dfffstate,
                           pageno = 1, pagesize = 500):
        """
        代发人员名单查询
        """
        param = '"aaf013":"","aaf030":"","aae100":"{dfcbstate}","aac002":"{idcard}",' \
             '"aac003":"","aae116":"{dfffstate}","aac082":"","aac066":"{dftype}",' \
             '"page":{pageno},"pagesize":{pagesize},"filtering":[],'\
             '"sorting":[{{"dataKey":"aaf103","sortDirection":"ascending"}}],"totals":[]'
        self.post_service_content('executeDfrymdQuery', param.format(**locals()))
        return self.parse(self.read_body())

    def get_dflx_cn(self, type):
        """
        获得代发类型中文名
        """
        return {"801":"独生子女", "802":"乡村教师", "803":"乡村医生"}[type]

    def get_jbzt_cn(self, state):
        """
        获得居保状态中文名
        """
        return {"1":"正常参保", "2":"暂停参保", "3":"未参保", "4":"终止参保"}[state]


def export_dfrymd_normal(filename, dftype, bcny):
    """
    导出代发人员名单（正常）

    filename:
      导出文件模板
    dftype:
      代发类型
    bcny:
      本次年月
    """
    with DefaultSession(DfModSession) as session:
        xlsbook = open_workbook(filename, formatting_info=1)
        book = copy(xlsbook)
        sheet = book.get_sheet(0)

        begindex = rowindex = 3
        total = 0

        date = Date.today().strftime('%Y%m%d')
        #datecn = Date.today().strftime('%Y年%#m月')
        datecn = Date.today().strftime('%Y{0}%#m{1}%#d{2}').format(*'年月日')
        zbdate = "制表时间：" + datecn
        sheet.update(1, 6, zbdate)
        
        js = session.execute_dfrymd_query(dftype, "", "1", "1")
        for data in js['datas']:
            if data.get('aac001'):
                # id = data['aac001']
                address = data['aaf103']
                name = data['aac003']
                idcard = data['aac002']
                dfksny = data['aic160']
                dfbz = data['aae019']
                dfname = data['aac066s']
                #dfffstate = session.get_dfffzt_cn(data['aae116'])
                jbstate = session.get_jbzt_cn(data['aac008s'])
                dfjzny = data['aae002jz']
                dfjzje = data['aae019jz']
                memo = ''

                # 计算本次应发金额
                ksny = str(dfjzny) + "0" if dfjzny else str(dfksny) + "1"
                m = re.match(r'(\d\d\d\d)(\d\d)(\d)', ksny)
                if m:
                    ksn = int(m.group(1))
                    ksy = int(m.group(2)) - int(m.group(3))
                    if m.group(3) == '1':
                        memo = '新增'
                else:
                    ksn = 0
                    ksy = 0

                if dfbz:
                    ksbz = dfbz
                    if memo:
                        memo += '按月'
                else:
                    ksbz = 5000
                    if memo:
                        memo += '一次性'
                        
                if dfjzje:
                    yfje = dfjzje
                else:
                    yfje = 0
                    
                m = re.match(r'(\d\d\d\d)(\d\d)', bcny)
                if m:
                    jsn = int(m.group(1))
                    jsy = int(m.group(2))
                else:
                    jsn = ksn
                    jsy = ksy

                if ksbz == 5000:
                    bcje = ksbz - yfje
                else:
                    bcje = ksbz * ((jsn - ksn) * 12 + jsy - ksy)

                if bcje > 0:
                    print('%d, %s, %s' % (rowindex, name, idcard))

                    row = sheet.get_or_create_row_from(rowindex, begindex)                    
                    row.update(0, rowindex - begindex + 1)
                    row.update(1, address)
                    row.update(2, name)
                    row.update(3, idcard)
                    row.update(4, dfksny)
                    row.update(5, ksbz)
                    row.update(6, dfname)
                    row.update(7, jbstate)
                    row.update(8, dfjzny if dfjzny else '')
                    row.update(9, dfjzje if dfjzje else '')
                    row.update(10, bcje)
                    row.update(11, memo)

                    total += bcje
                    rowindex += 1

        #合计
        row = sheet.get_or_create_row_from(rowindex, begindex)
        row.update(0, '')
        row.update(2, '共计')
        row.update(3, rowindex - begindex)
        row.update(5, '')
        row.update(9, '合计')
        row.update(10, total)

        ext = filename.rfind('.')
        if ext > -1:
            tofilename = filename[0:ext] + '（' + session.get_dflx_cn(dftype) + '）' + \
                         date + filename[ext:]
        else:
            tofilename = filename + '（' + session.get_dflx_cn(dftype) + '）' + date

        book.save(tofilename)


if __name__ == '__main__':
    # "801":"独生子女", "802":"乡村教师", "803":"乡村医生"
    export_dfrymd_normal("D:\\代发管理\\雨湖区城乡居民基本养老保险代发人员名单.xls", "803", "201609")
