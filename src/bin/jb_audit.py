import click
from ..base.utils import to_dashdate
from ..jb.session import Cbsh, CbshQuery, Session
from ..jb import database as db


@click.command()
@click.argument('start_date', required=True, metavar='起始审核时间')
@click.argument('end_date', required=False, metavar='结束审核时间')
def audit(start_date, end_date):
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

    result = None

    with Session.use() as session:
        session.request_service(CbshQuery.new(start_date, end_date or ''))
        result = session.get_result(Cbsh)

    if result:
        with db.Session() as session:
            index = 1
            for cbsh in result.datas:
                r = session.query(db.FPHistoryData).filter_by(
                    idcard=cbsh.idcard).first()
                if r:
                    print(f'{index:3}. {cbsh.idcard} {cbsh.name} {cbsh.birthday} ' + 
                          f'{r.jbrdsf} {r.name if r.name != cbsh.name else ""}')
                else:
                    print(f'{index:3}. {cbsh.idcard} {cbsh.name} {cbsh.birthday}')
                index += 1


if __name__ == '__main__':
    audit()
