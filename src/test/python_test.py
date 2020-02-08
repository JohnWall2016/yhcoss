import dataclasses
from dataclasses import dataclass, field, MISSING, fields
from dataclasses_json import dataclass_json, config, DataClassJsonMixin
from typing import Type, TypeVar, List, Literal, Generic, Dict, List, Union, Callable


def json(name: str = None, default=MISSING):
    return field(metadata=config(field_name=name), default=default)


class Jsonable(DataClassJsonMixin):
    def to_json(self):
        return super().to_json(separators=(',', ':'))


A = TypeVar('A', bound=Jsonable)


@dataclass
class Request(Jsonable, Generic[A]):
    serviceid: str
    target: str = ''
    sessionid: Union[str, None] = None
    loginname: str = ''
    password: str = ''
    params: Union[A, None] = None
    datas: Union[List[A], None] = None

    def __init__(self, serviceid: str, params: A):
        self.serviceid = serviceid
        self.params = params
        self.datas = [params]


def page(cls):
    @dataclass
    class DataPage(cls):
        page: Union[int, None] = None
        pagesize: Union[int, None] = None
    return DataPage


@page
@dataclass
class Person(Jsonable):
    name: str = json(name='abc1', default='')
    age: Union[int, None] = None
    friends: Union[List['Person'], None] = None


@page
@dataclass
class SomeQuery(Jsonable):
    aac22: str = ''

p = Person(name='John', age=20, friends=[], page=1, pagesize=500) # type: ignore
req = Request[Person]('query', p)
print(req.to_json())
print(type(p))

p1 = SomeQuery()
req2 = Request[SomeQuery]('query', p1)
print(req2.to_json())
print(type(p1))

print(type(p1) == type(p))
print(type(p1).__hash__)
print(type(p).__hash__)

p = Person(name='John', age=20, friends=[], page=1, pagesize=500) # type: ignore
req = Request[Person]('query', p)
print(req.to_json())
print(type(p))
