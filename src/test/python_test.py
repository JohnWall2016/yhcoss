from typing import *

def test_str():
    abc = """'
        abcefg
        '"""
    print(abc)

    print("abcefg"
          "hijijlj"
          "ljlsjdfl")

T = TypeVar('T')
U = TypeVar('U')


def call_safe(func: Callable[[T], U], args: T, default: U = None):
    try:
        return func(*args)
    except:
        return default


print(call_safe(int, '23'))
print(call_safe(int, '23A'))
print(call_safe(int, '23A', 123))
