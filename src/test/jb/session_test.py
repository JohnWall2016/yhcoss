from dataclasses import dataclass
from ...jb.session import Service, Parameters, params

print(Service(Parameters('loadCurrentUser'), 'wj', 'abc').to_json())

@params(id='syslogin', page=True)
class Syslogin(Parameters):
    username: str
    passwd: str

print(Syslogin("abc", "123").to_json()) # type: ignore

print(Service(Syslogin("abc", "123"), 'wj', 'abc').to_json()) # type: ignore