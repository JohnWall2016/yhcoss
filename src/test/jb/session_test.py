from ...jb.session import *
from dataclasses import dataclass as _dataclass
from typing import get_type_hints
import typing_inspect

#print(Service(Parameters('loadCurrentUser'), 'wj', 'abc').to_json())
#
#
# @params(id='syslogin')
# class Syslogin(Parameters):
#    username: str
#    passwd: Optional[str] = None
#
#
# print(Syslogin("abc", "123").to_json())  # type: ignore
#
#s = Syslogin.from_json('{"username":"abc1","passwd":"1232","other":"goog"}')
# print(s)
#s = Syslogin.from_json('{"username":"abc1","other":"goog"}')
# print(s)
#
# print(Service(Syslogin("abc", "123"), 'wj', 'abc').to_json())  # type: ignore
#
#
# @params(id='syslogin', page=Page(2, 500, sorting=[{'aac12': 'asc'}]))
# class SysloginP(Parameters):
#    username: str
#    passwd: str
#
#
# print(SysloginP("abc", "123").to_json())  # type: ignore
#
# print(Service(SysloginP("abc", "123"), 'wj', 'abc').to_json())  # type: ignore

with Session.use('002') as session:
    session.request_service(CbxxQuery(idcard='430321196408086422'))
    result = session.get_result(CbxxResult)
    if len(result) > 0:
        print(result[0].name, result[0].cbstate_ch,
              result[0].jfstate_ch, result[0].jbstate_cn)
        print(result[0].birthday, type(result[0].birthday))
    print(result)

    session.request_service(CbshQuery(start_date='2020-02-14'))
    result = session.get_result(CbshResult)
    idx = 0
    for cbsh in result.datas:
        idx += 1
        print(f'{idx} {cbsh.name} {cbsh.idcard} {cbsh.birthday}')
