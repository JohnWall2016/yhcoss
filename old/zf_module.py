"""
支付模块
"""

from session import Session, DefaultSession

from excel.xlrd import open_workbook
from excel.xlutils.copy import copy

from datetime import date as Date

import re

from utils import NumUtils


class ZfModSession(Session):
    """
    代发模块操作会话
    """

    def get_bank_name_cn(self, bank):
        """
        获得银行代码中文名
        """
        return {"LY": "中国农业银行", "ZG": "中国银行", "JS": "中国建设银行",
                "NH": "农村信用合作社", "YZ": "邮政", "JT": "交通银行"}[bank]

    def cwzfgl_query(self, ffny, ywzt="0", pageno=1, pagesize=100):
        """
        财务支付单查询
        """
        params = '"aaa121":"","aaz031":"","aae002":"{ffny}","aae089":"{ywzt}",' \
                 '"bie013":"","page":{pageno},"pagesize":{pagesize},"filtering":[],' \
                 '"sorting":[],"totals":[{{"dataKey":"aae169","aggregate":"sum"}}]'
        self.post_service_content("cwzfglQuery", params.format(**locals()))
        return self.parse(self.read_body())

    def cwzfgl_zfdry_query(self, js, pageno=1, pagesize=15):
        """
        支付单人员查询
        """
        params = '"aaf015":"","aac002":"","aac003":"","aaz031":"{js[aaz031]}",' \
                 '"aae088":"{js[aae088]}","aaa121":"{js[aaa121]}",' \
                 '"aae002":"{js[aae002]}","page":{pageno},"pagesize":{pagesize},' \
                 '"filtering":[],"sorting":[],"totals":[{{"dataKey":"aae019","aggregate":"sum"}}]'
        self.post_service_content(
            "cwzfgl_zfdryQuery", params.format(**locals()))
        return self.parse(self.read_body())


def export_cwzfd(filename, ffny):
    """
    导出财务支付单

    filename:
      模板文件名
    ffny:
      发放年月
    """
    with DefaultSession(ZfModSession) as session:
        xlsbook = open_workbook(filename, formatting_info=1)
        book = copy(xlsbook)
        sheet = book.get_sheet(0)

        begindex = rowindex = 4
        total = 0

        m = re.match(r'(\d\d\d\d)(\d\d)', ffny)
        if m:
            ffn = m.group(1)
            ffy = int(m.group(2))
        else:
            raise Exception('发放年月格式有误（yyyynn）！')

        date = Date.today().strftime('%Y%m%d')
        title = '%s年%d月个人账户返还表' % (ffn, ffy)
        sheet.update(0, 0, title)

        # datecn = Date.today().strftime('%Y年%#m月')
        datecn = Date.today().strftime('%Y{0}%#m{1}%#d{2}').format(*'年月日')
        zbdate = "制表时间：" + datecn
        sheet.update(1, 7, zbdate)

        jo = session.cwzfgl_query(ffny)
        if jo and jo.get('datas'):
            for item in jo['datas']:
                if item.get('aaa079') == '3':
                    jo_item = session.cwzfgl_zfdry_query(item)['datas'][0]
                    tbr_name = jo_item['aac003']
                    tbr_idcard = jo_item['aac002']
                    zfdh = jo_item['aaz031']
                    fhje = jo_item['aae019']
                    bank_name = item['aae009']
                    bank_idcard = item['bie013']
                    bank_number = item['aae010']
                    jo_zz = session.cbzzfh_perinfo_list(tbr_idcard)
                    if jo_zz and jo_zz['rowcount'] > 0:
                        jo_zz_info = session.cbzzfh_perinfo(
                            jo_zz['datas'][0])['datas'][0]
                        fhyy = session.get_zzyy_cn(jo_zz_info['aae160'])
                        bank_type = session.get_bank_name_cn(
                            jo_zz_info['aaz065'])
                    else:
                        jo_zz = session.dyzzfh_perinfo_list(tbr_idcard)
                        if jo_zz and jo_zz['rowcount'] > 0:
                            jo_zz_info = session.dyzzfh_perinfo(
                                jo_zz['datas'][0])['datas'][0]
                            fhyy = session.get_zzyy_cn(jo_zz_info['aae160'])
                            bank_type = session.get_bank_name_cn(
                                jo_zz_info['aaz065'])
                        else:
                            fhyy = ''
                            bank_type = ''

                    row = sheet.get_or_create_row_from(rowindex, begindex)
                    row.update(0, rowindex - begindex + 1)
                    row.update(1, tbr_name)
                    row.update(2, tbr_idcard)
                    row.update(3, fhyy)
                    row.update(4, zfdh)
                    row.update(5, fhje)
                    row.update(6, NumUtils.to_chinese_number(fhje))
                    row.update(7, bank_name)
                    row.update(8, bank_number)
                    row.update(9, bank_type)

                    total += fhje
                    rowindex += 1

        row = sheet.get_or_create_row_from(rowindex, begindex)
        row.update(0, '合计')
        row.update(4, '')
        row.update(5, total)

        ext = filename.rfind('.')
        if ext > -1:
            tofilename = filename[0:ext] + date + filename[ext:]
        else:
            tofilename = filename + date

        book.save(tofilename)


if __name__ == '__main__':
    export_cwzfd('D:\\支付管理\\雨湖区居保个人账户返还表.xls', '201610')
