import inspect
import sys
from typing import Optional, Mapping, Collection, Union, Any, TypeVar


def isinstance_safe(o, t):
    try:
        result = isinstance(o, t)
    except Exception:
        return False
    else:
        return result


def issubclass_safe(cls, classinfo):
    try:
        return issubclass(cls, classinfo)
    except Exception:
        return (is_new_type_subclass_safe(cls, classinfo)
                if is_new_type(cls)
                else False)


def is_new_type_subclass_safe(cls, classinfo):
    super_type = getattr(cls, "__supertype__", None)

    if super_type:
        return is_new_type_subclass_safe(super_type, classinfo)

    try:
        return issubclass(cls, classinfo)
    except Exception:
        return False


def is_new_type(type_):
    return inspect.isfunction(type_) and hasattr(type_, "__supertype__")


def _hasargs(type_, *args):
    try:
        res = all(arg in type_.__args__ for arg in args)
    except AttributeError:
        return False
    else:
        return res

T = TypeVar('T')

def is_optional(type_):
    return issubclass_safe(type_, Optional[T]) or _hasargs(type_, type(None))


def is_mapping(type_):
    return issubclass_safe(get_type_origin(type_), Mapping)


def is_collection(type_):
    return issubclass_safe(get_type_origin(type_), Collection)


def is_nonstr_collection(type_):
    return (issubclass_safe(get_type_origin(type_), Collection)
            and not issubclass_safe(type_, str))


def is_union(type_):
    return get_type_origin(type_) == Union


def is_instanceof_generic(obj, type_):
    try:
        for t in type_.__args__:
            if isinstance_safe(obj, t):
                return True
        return False
    except Exception:
        return False


def get_type_origin(type_):
    """Some spaghetti logic to accommodate differences between 3.6 and 3.7 in
    the typing api"""
    try:
        origin = type_.__origin__
    except AttributeError:
        if sys.version_info.minor == 6:
            try:
                origin = type_.__extra__
            except AttributeError:
                origin = type_
            else:
                origin = type_ if origin is None else origin
        else:
            origin = type_
    return origin


typing: Any = sys.modules.get('typing')


def is_forwardref(obj):
    return isinstance_safe(obj, typing.ForwardRef)


def resolve_forwardref(cls, ref):
    for base in cls.__mro__:
        base_globals = sys.modules[base.__module__].__dict__
        try:
            type_ = typing._eval_type(ref, base_globals, None)
            if type_:
                return type_
        except:
            pass
    return None
