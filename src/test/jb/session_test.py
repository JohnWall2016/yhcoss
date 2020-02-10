from dataclasses import dataclass
from ...jb.session import Service, Parameters, params, Page, Session

print(Service(Parameters('loadCurrentUser'), 'wj', 'abc').to_json())


@params(id='syslogin')
class Syslogin(Parameters):
    username: str
    passwd: str


print(Syslogin("abc", "123").to_json())  # type: ignore

print(Service(Syslogin("abc", "123"), 'wj', 'abc').to_json())  # type: ignore


@params(id='syslogin', page=Page(2, 500, sorting=[{'aac12': 'asc'}]))
class SysloginP(Parameters):
    username: str
    passwd: str


print(SysloginP("abc", "123").to_json())  # type: ignore

print(Service(SysloginP("abc", "123"), 'wj', 'abc').to_json())  # type: ignore

with Session.use('002') as session:
    #session.request_service()
    pass