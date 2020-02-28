from ...jb.session import *


def test():
    with Session.use() as session:
        session.request_service(CbxxQuery.new(idcard='430321196408086422'))
        result = session.get_result(Cbxx)
        if result and len(result) > 0:
            print(result[0].name, result[0].cbstate_ch,
                  result[0].jfstate_ch, result[0].jbstate_cn)
            print(result[0].birthday, type(result[0].birthday))
        print(result)

        session.request_service(CbshQuery.new(start_date='2020-02-14'))
        result = session.get_result(Cbsh)
        if result:
            idx = 0
            for cbsh in result.datas:
                idx += 1
                print(f'{idx} {cbsh.name} {cbsh.idcard} {cbsh.birthday}')

test()