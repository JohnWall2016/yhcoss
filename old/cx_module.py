"""
查询模块
"""

from session import DefaultSession

from excel.xlrd import open_workbook
from excel.xlutils.copy import copy


def search_phone_to_xls(xls_name, xls_name_save, col_id, col_save):
    """
    查询电话
    """
    xls_book = open_workbook(xls_name, formatting_info=1)
    sheet_read = xls_book.sheet_by_index(1)
    book_write = copy(xls_book)
    sheet_write = book_write.get_sheet(1)

    nrows = sheet_read.nrows
    with DefaultSession() as session:
        for i in range(0, nrows):
            idcard = sheet_read.row_values(i)[col_id]
            datas = session.zhcxgrinfo_query(idcard)['datas']
            phone = ''
            if len(datas) and datas[0]['aae005']:
                phone = datas[0]['aae005']
            print(idcard, phone)
            sheet_write.write(i, col_save, phone)

    book_write.save(xls_name_save)


def search_ryzt_to_xls(xls_name, xls_name_save, col_id, col_save, row_beg=None, row_end=None):
    """
    查询人员状态
    """
    xls_book = open_workbook(xls_name, formatting_info=1)
    sheet_read = xls_book.sheet_by_index(0)
    book_write = copy(xls_book)
    sheet_write = book_write.get_sheet(0)

    if not row_beg:
        row_beg = 0
    if not row_end:
        row_end = sheet_read.nrows

    with DefaultSession() as session:
        for i in range(row_beg, row_end):
            idcard = sheet_read.row_values(i)[col_id]
            msg = ''
            js = session.zhcxgrinfo_query(idcard)
            if not js['rowcount']:
                msg = '未查到此人信息'
            else:
                cbzt = js['datas'][0]['aac008']
                jfzt = js['datas'][0]['aac031']
                if jfzt == '3':        #终止缴费人员
                    if cbzt == '1':    #正常待遇人员
                        msg = '正常待遇人员'
                    elif cbzt == '2':  #暂停待遇人员
                        msg = '暂停待遇人员'
                    elif cbzt == '4':  #终止参保人员（含缴费和待遇人员）
                        msg = '终止参保人员'
                    else:              #其他终止缴费人员
                        msg = '其他终止缴费人员'
                elif jfzt == '1':      #参保缴费人员
                    if cbzt == '1':    #正常缴费人员
                        msg = '正常缴费人员'
                    else:              #其他参保缴费人员
                        msg = '其他参保缴费人员'
                elif jfzt == '2':      #暂停缴费人员
                    if cbzt == '2':    #暂停缴费人员
                        msg = '暂停缴费人员'
                    else:              #其他暂停缴费人员
                        msg = '其他暂停缴费人员'
                else:
                    msg = '其他未知类型人员'
            print(idcard, msg)
            sheet_write.write(i, col_save, msg)

    book_write.save(xls_name_save)


def search_jfxx_to_xls(xls_name, xls_name_save, col_id, col_save,
                       row_beg=None, row_end=None, qsjfsj='20160101', jzjfsj='20161231'):
    """
    查询缴费信息
    """
    xls_book = open_workbook(xls_name, formatting_info=1)
    sheet_read = xls_book.sheet_by_index(0)
    book_write = copy(xls_book)
    sheet_write = book_write.get_sheet(0)

    if not row_beg:
        row_beg = 0
    if not row_end:
        row_end = sheet_read.nrows

    with DefaultSession() as session:
        for i in range(row_beg, row_end):
            idcard = sheet_read.row_values(i)[col_id]
            msg = ''
            js = session.jfxxcx_queryjfxx(idcard, qsjfsj, jzjfsj)
            if not js['rowcount']:
                msg = '无缴费信息'
            else:
                msg = '有缴费信息'
            print(idcard, msg)
            sheet_write.write(i, col_save, msg)

    book_write.save(xls_name_save)


import collections
    
XZQH_MAP = collections.OrderedDict([
    ('长城乡',       '43030201'),
    ('昭潭街道',     '43030202'),
    ('先锋街道',     '43030203'),
    ('万楼街道',     '43030204'),
    ('楠竹山镇',     '43030206'),
    ('姜畲镇',       '43030207'),
    ('鹤岭镇',       ['43030205','43030208']),
    ('城正街街道',   '43030209'),
    ('雨湖路街道',   '43030210'),
    ('平政路街道',   '43030211'),
    ('云塘街道',     '43030212'),
    ('中山路街道',   '43030213'),
    ('窑湾街道',     '43030214'),
    ('广场街道',     '43030215'),
    ('（其中：江麓）',['4303021506','4303021507','4303021508']),
    ('羊牯塘街道',   '43030216')
])


def count_jfqk_to_xls(qsjfsj, jzjfsj, jfnd = ''):
    """
    统计缴费情况
    """
    with DefaultSession() as session:
        for name, xzqh in XZQH_MAP.items():
            jj = 0.0; rs = 0
            if isinstance(xzqh, str):
                xzqh = [xzqh]
            for xzbm in xzqh:
                xz = xzbm if len(xzbm) <= 8 else xzbm[0:8]
                cun = '' if len(xzbm) <= 8 else xzbm
                # 先统计基金数，基金不分年度
                js = session.jfxxcx_queryjfxx('', qsjfsj, jzjfsj, '', xz, cun)
                ln = len(js['datas'])
                if ln > 0:
                    last = js['datas'][ln - 1]
                    jj += float(last['aae019'])
                # 再统计缴费人数，缴费人数只计当年度
                js = session.jfxxcx_queryjfxx('', qsjfsj, jzjfsj, jfnd, xz, cun)
                ln = len(js['datas'])
                if ln > 0:
                    last = js['datas'][ln - 1]
                    srs = last['aac002']
                    import re
                    m = re.search('人数：(\d+)', srs)
                    if m:
                        rs += int(m.group(1))
            print(u'{:\u3000<7s} {:>10.3f} {:>10d}'.format(name, jj/10000, rs))


if __name__ == '__main__':
    #search_phone_to_xls('人社局已核已享受2016特困一级补贴人员（包括未婚）.xls',
    #                      '人社局已核已享受2016特困一级补贴人员（包括未婚）2.xls',
    #                      2, 20)
    #search_ryzt_to_xls('雨湖区到龄欠费人员参保缴费明细台账（一、二季度）.xls',
    #                     '雨湖区到龄欠费人员参保缴费明细台账（一、二季度）3.xls',
    #                     3, 9, 1, 115)
    #search_jfxx_to_xls('雨湖区只需缴纳40元未参保缴费人员明细台账（一、二季度）.xls',
    #                     '雨湖区只需缴纳40元未参保缴费人员明细台账（一、二季度）3.xls',
    #                     2, 9, 1, 1330)
    #search_ryzt_to_xls('雨湖区只需缴纳40元未参保缴费人员明细台账（一、二季度）3.xls',
    #                     '雨湖区只需缴纳40元未参保缴费人员明细台账（一、二季度）4.xls',
    #                     2, 10, 1, 1330)
    count_jfqk_to_xls('20160101', '20161231', '2016')
    #search_ryzt_to_xls('2016年11月死亡申报名单2.xls', '2016年11月死亡申报名单3.xls',
    #                    3, 7, 2, 94)
                        
