from typing import *
from dataclasses import dataclass
from ..jsonable import *

@dataclass
class Person:
    name: str = jfield('abc001', '')
    age: Optional[int] = None


@dataclass
class Worker(Jsonalbe, Person):
    coworkers: List['Worker'] = jfield(default_factory=list)


w = Worker(name='Peter', age=32)
w.coworkers.append(Worker(name='Jack', age=33))
w.coworkers.append(Worker(name='Ben'))
j = w.to_json()
print(j)

w2 = Worker.from_json(j)
print(w2)
    
    
