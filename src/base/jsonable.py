from dataclasses import fields, field, is_dataclass
from typing import *
from .types import *
import json
import copy


def jfield(name: str = '', ignore=False, **kws):
    return field(metadata={'name': name, 'ignore': ignore}, **kws)


A = TypeVar('A')


class Jsonable:
    def to_json(self) -> str:
        return json.dumps(_to_dict(self), separators=(',', ':'))

    @classmethod
    def from_json(cls: Type[A], s: str) -> Optional[A]:
        # print(f'cls0: {cls}')
        return _from_dict(cls, json.loads(s), cls)


def _to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        result = []
        for field in fields(type(obj)):
            # print(f'{field=}')
            name = field.name
            meta = field.metadata
            if meta:
                if meta.get('ignore', False):
                    continue
                jfname = meta.get('name', '')
                if jfname:
                    name = jfname
            result.append((name,  _to_dict(getattr(obj, field.name, None))))
        return dict(result)
    elif isinstance(obj, Mapping):
        return dict((_to_dict(k), _to_dict(v)) for k, v in obj.items())
    elif isinstance(obj, Collection) and not isinstance(obj, str) and not isinstance(obj, bytes):
        return list(_to_dict(v) for v in obj)
    else:
        return copy.deepcopy(obj)


def _from_dict(cls, dict: Any, rootcls):
    # print(f'{cls=}')
    if isinstance_safe(dict, cls):
        return dict
    elif is_dataclass(cls) and isinstance_safe(dict, Mapping):
        args = {}
        field_name = 'Unknown'
        try:
            for field in fields(cls):
                field_name = name = field.name
                meta = field.metadata
                if meta:
                    if meta.get('ignore', False):
                        continue
                    jfname = meta.get('name', '')
                    if jfname:
                        name = jfname
                args[field.name] = _from_dict(
                    field.type, dict.get(name, None), rootcls)
        except Exception as ex:
            raise Exception(f'decoding field "{field_name}" error: {ex}')
        return cls(**args)
    elif is_mapping(cls) and isinstance_safe(dict, Mapping):
        k_type, v_type = cls.__args__
        return dict((_from_dict(k_type, k, rootcls),
                     _from_dict(v_type, v, rootcls))
                    for k, v in dict)
    elif is_nonstr_collection(cls) and isinstance_safe(dict, Collection):
        type_ = cls.__args__[0]
        return list(_from_dict(type_, e, rootcls) for e in dict)
    elif is_union(cls) and is_instanceof_generic(dict, cls):
        return dict
    elif is_forwardref(cls):
        type_ = resolve_forwardref(rootcls, cls)
        if type_ is not None:
            return _from_dict(type_, dict, rootcls)
        return dict
    else:
        raise Exception(f'except type: {cls}, get: {type(dict)}, {dict}')
