from typing import *
from dataclasses import dataclass
from ..base.jsonable import *

def test1():
    @dataclass
    class Person:
        name: str = jfield('abc001', '')
        age: Optional[int] = None


    @dataclass
    class Worker(Jsonable, Person):
        coworkers: List['Worker'] = jfield(default_factory=list)


    w = Worker(name='Peter', age=32)
    w.coworkers.append(Worker(name='Jack', age=33))
    w.coworkers.append(Worker(name='Ben'))
    j = w.to_json()
    print(j)

    w2 = Worker.from_json(j)
    print(w2)

def test2():
    T = TypeVar('T')

    class Result(Protocol, Generic[T]):
        message: str
        datas: List[T]

        def __init__(self, message: str, datas: List[T]) -> None:
            ...
        def __len__(self) -> int:
            ...
        def __getitem__(self, key: int) -> T:
            ...
        def to_json(self) -> str:
            ...
        @classmethod
        def from_json(cls: Type[A], s: str) -> Optional[A]:
            ...

    def result_class(cls: Type[T]) -> Type[Result[T]]:
        @dataclass
        class _Result(Jsonable):
            message: str
            datas: List[cls]

            def __len__(self) -> int:
                return len(self.datas or [])

            def __getitem__(self, key: int) -> T:
                return self.datas[key]
        return _Result

    @dataclass
    class Item:
        desc: str = ''

    ItemResult = result_class(Item)

    r = ItemResult[Item]('abc', [Item('item1'), Item('item2')])
    j = r.to_json()
    print(j)
    r2 = ItemResult[Item].from_json(j)
    print(r2)
    

test2()



    
    
