import json
from typing import Any

class TypenameJSONEncoder(json.JSONEncoder):
  def encode(self, o: Any) -> Any:
    if isinstance(o, dict):
      converted_obj = self._stringify_keys(o)
    return super().encode(converted_obj)

  def _stringify_keys(self, obj: Any) -> Any:
    if isinstance(obj, dict):
      return {self._convert_key(k): self._stringify_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
      return [self._stringify_keys(i) for i in obj]
    elif isinstance(obj, tuple):
      return tuple(self._stringify_keys(i) for i in obj)
    return obj

  def _convert_key(self, key: Any) -> Any:
    if isinstance(key, type):
      return f"{key.__module__}.{key.__name__}"
    return str(key)
