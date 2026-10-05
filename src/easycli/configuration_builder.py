import functools
import json
from pydantic import (
  BaseModel
)
from typing import (
  Any,
  Dict,
  overload,
  Type,
  Union
)
import warnings

from easycli.trie import Trie, TrieNodeEncoder
from easycli.utils.lookahead import lookahead
from easycli.utils.model_metadata import model_metadata
from easycli.utils.recursive_update import recursive_update

from easycli.exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)


class ConfigurationBuilder[B:BaseModel]:
  def __init__(
      self,
      trie: Trie
    ):
    warnings.warn("ConfigurationBuilder.__init__ is not intended to be called directly in client code")
    self.trie = trie

  def __str__(self):
    return json.dumps(self.trie.root, cls = TrieNodeEncoder, indent = 2)

  def __repr__(self):
    return json.dumps(self.trie.root, cls = TrieNodeEncoder)

  @classmethod
  def build[M:BaseModel](
      cls,
      ModelType: Type[M]
    ) -> "ConfigurationBuilder[M]":
    trie = Trie()

    for pk in cls._path_search(ModelType):
      trie.insert(pk)

    with warnings.catch_warnings():
      warnings.simplefilter('ignore')
      instance = cls(trie)

    return instance

  @classmethod
  def _path_search(
      cls,
      ModelType: Union[dict, Type[BaseModel]],
      *,
      pathkey = tuple()
    ):

    for field_name, field_info in ModelType.model_fields.items():
      pk = pathkey + (field_name, )
      yield pk

      sub = set()
      for mm in model_metadata(field_info):
        for s in cls._path_search(mm['model'], pathkey = tuple()):
          sub.add(s)

      for s in sub:
        yield pk + s

  def generate_assignment(self, prefix, value) -> dict:
    node = self.trie.search(prefix)

    if node is None:
      raise UnassignableError(f"'{prefix}' not found")
    elif len(node.source) > 1:
      raise AmbiguousAssignmentError(f"'{prefix}' is not uniquely determined")

    item = next(iter(node.source))

    t = r = dict()
    for k, is_terminating in lookahead(item.split('.')):
      if is_terminating:
        r[k] = value
      else:
        r = r.setdefault(k, dict())

    return t

  def compile_assignments(self, assignment_set) -> dict:
    prefixes = sorted(assignment_set.keys())
    for a,b in zip(prefixes, prefixes[1:]):
      if b.startswith(a):
        raise ValueError(f"Incompatible assignment prefixes: {a} {b}")
    
    partial_configs = list()
    for prefix, value in assignment_set.items():
      try:
        value = json.loads(value)
      except (json.JSONDecodeError, TypeError):
        pass
      
      pc = self.generate_assignment(prefix, value)
      partial_configs.append(pc)

    compiled_config = functools.reduce(
      functools.partial(recursive_update, discard = False, fallback = False), 
      partial_configs,
      dict()
    )

    return compiled_config
  
  def apply_assignments(
      self,
      model_instance: B,
      assignment_set,
      *,
      discard,
      fallback,
    ) -> B:
    ModelType = type(model_instance)
    incremental_config  = self.compile_assignments(assignment_set)
    updated_config      = recursive_update(
      model_instance.model_dump(),
      incremental_config, 
      discard = discard,
      fallback = fallback
    )
    return ModelType.model_validate(updated_config)

  @overload
  @classmethod
  def assign[M:BaseModel](
    cls,
    instance_or_type: M,
    assignment_set: Dict[str,Any]
  ) -> M: ...

  @overload
  @classmethod
  def assign[M:BaseModel](
    cls,
    instance_or_type: type[M],
    assignment_set: Dict[str,Any]
  ) -> Dict: ...

  @classmethod
  def assign[M:BaseModel](
    cls,
    instance_or_type: Union[M, Type[M]],
    assignment_set: Dict[str, Any]
  ) -> Union[B, Dict]:
    if isinstance(instance_or_type, BaseModel):
      model_dict = instance_or_type.model_dump()
      ModelType = type(instance_or_type)
      cast_to_base_model = True

    elif issubclass(instance_or_type, BaseModel):
      model_dict = dict()
      ModelType = instance_or_type
      cast_to_base_model = False

    else:
      raise TypeError(
        f"'instance_or_type' must be an instance or subclass of BaseModel: {type(T)}"
      )

    instance = cls.build(ModelType)

    incremental_config  = instance.compile_assignments(assignment_set)
    updated_config      = recursive_update(model_dict, incremental_config, discard = False, fallback = False)

    if cast_to_base_model == True:
      result = ModelType(**updated_config)
    else:
      result = updated_config

    return result

