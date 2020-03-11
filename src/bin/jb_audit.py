import click
from ..base.utils import to_dashdate
from ..jb.session import Cbsh, CbshQuery, Session
from ..jb import database as db
from ..excel.xls import Workbook


@click.command()
@click.argument('start_date', required=True, metavar='起始审核时间')
@click.argument('end_date', required=False, metavar='结束审核时间')
def audit(start_date:str='', end_date:str=''):
    '''
    特殊参保人员身份信息变更导出程序

    \b
    起始审核时间, 例如: 20190429
    截止审核时间, 例如: 20190505
    '''
    start_date = to_dashdate(start_date)
    if end_date:
        end_date = to_dashdate(end_date)

    print(f'{start_date=}, {end_date=}')

    time_span = ''
    if start_date:
        time_span += start_date
    if end_date:
        time_span += '_' + end_date

    result = None

    with Session.use() as session:
        session.request_service(CbshQuery.new(start_date, end_date or ''))
        result = session.get_result(Cbsh)

    if result is not None:
        with db.Session() as session:
            if len(result.datas):
                print(f'共计 {len(result.datas)} 条')
                index = 1
                findex = 2
                sindex = 2
                export = False
                dir = r'D:\精准扶贫'
                workbook = Workbook(f'{dir}\\批量信息变更模板.xls')
                sheet = workbook.get_sheet(0)
                for cbsh in result.datas:
                    r = session.query(db.FPHistoryData).filter_by(idcard=cbsh.idcard).first()
                    if r:
                        print(f'{index:3}. {cbsh.idcard} {cbsh.name} {cbsh.birthday} ' + 
                              f'{r.jbrdsf} {r.name if r.name != cbsh.name else ""}')
                        row = sheet.copy_row(findex, sindex)
                        row.update('B', cbsh.idcard)
                        row.update('E', cbsh.name)
                        row.update('J', jb_class[r.jbrdsf])
                        sindex += 1
                        export = True
                    else:
                        print(f'{index:3}. {cbsh.idcard} {cbsh.name} {cbsh.birthday}')
                    index += 1
                if export:
                    workbook.save(f'{dir}\\批量信息变更{time_span}.xls')


jb_class = {
    '贫困人口一级': '051',
    '特困一级': '031',
    '低保对象一级': '061',
    '低保对象二级': '062',
    '残一级': '021',
    '残二级': '022'
}


if __name__ == '__main__':
    audit()
