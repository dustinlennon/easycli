import functools
from itertools import chain, combinations
import json
from pydantic import (
  BaseModel
)
import pytest
import textwrap
from typing import (
  Any,
  Dict,
  Iterator,
  Optional,
  overload,
  Type,
  Union
)

from yaml import safe_load

from easycli.utils.lookahead import lookahead
from easycli.utils.model_metadata import model_metadata
from easycli.utils.recursive_update import recursive_update

from easycli.exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)

from tests.simple_config import *

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# zz = Counter(['_'.join(pk).upper() for pk in pathkeys])
# psit = powerset(zz)

#
# > TrieNode
#
class TrieNode(object):
  def __init__(self, prefix):
    self.children: Dict[str, "TrieNode"]   = dict()
    self.prefix     = '_'.join(prefix)
    self.source     = set()

  def __repr__(self):
    source = "; ".join(self.source)
    result = f"{self.prefix}: {source}"
    return result
    
  def __getitem__(self, key):
    return self.children[key]

#
# > BaseModelTrie
#
class BaseModelTrie[B:BaseModel]:
  def __init__(self):
    self.root = TrieNode('')

  def insert(self, word):
    trie = self.root
   
    source   = '.'.join(word)
    word    = '_'.join(word).upper().split('_')

    for i in range(len(word)):
      letter    = word[i]
      prefix    = word[0:(i+1)]
      
      if letter not in trie.children:
        trie.children.setdefault(letter, TrieNode(prefix))
      trie = trie.children[letter]
    
    trie.source.add(source)

  def visit(self, root = None) -> Iterator[TrieNode]:
    if root is None:
      root = self.root
    else:
      yield root

    for node in root.children.values():
      for subnode in self.visit(node):
        yield subnode

  def search(self, prefix) -> Optional[TrieNode]:
    trie    = self.root
    word    = prefix.split('_')
    result  = None

    try:
      for letter in word:
        trie = trie.children[letter]
    except KeyError:
      result = None
    else:
      result = trie

    return result

  def __getitem__(self, key):
    return self.root[key]

  @classmethod
  def build[M:BaseModel](cls, ModelType: Type[M]) -> "BaseModelTrie[M]":
    trie = cls()

    for pk in cls._path_search(ModelType):
      trie.insert(pk)

    return trie

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

  def generate_assignment(self, prefix, value):
    node = self.search(prefix)

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

  def compile_assignments(self, assignment_set):
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
      recursive_update, 
      partial_configs,
      dict()
    )

    return compiled_config
  
  def apply_assignments(self, model_instance: B, assignment_set) -> B:
    ModelType = type(model_instance)
    incremental_config  = self.compile_assignments(assignment_set)
    updated_config      = recursive_update(model_instance.model_dump(), incremental_config)   
    return ModelType.model_validate(updated_config)

  @overload
  @classmethod
  def assign[B:BaseModel](cls, model_or_type: B, assignment_set: Dict[str,Any]) -> B: ...

  @overload
  @classmethod
  def assign[B:BaseModel](cls, model_or_type: type[B], assignment_set: Dict[str,Any]) -> Dict: ...

  @classmethod
  def assign[B: BaseModel](
    cls,
    model_or_type: Union[B, Type[B]],
    assignment_set: Dict[str, Any]
  ) -> Union[B, Dict]:
    if isinstance(model_or_type, BaseModel):
      model_dict = model_or_type.model_dump()
      ModelType = type(model_or_type)
      cast_to_base_model = True

    elif issubclass(model_or_type, BaseModel):
      model_dict = dict()
      ModelType = model_or_type
      cast_to_base_model = False

    else:
      raise TypeError(
        f"AmbiguityTree.assign: 'model_or_type' must be an instance of subclass of BaseModel: {type(T)}"
      )

    instance = cls.build(ModelType)
    incremental_config  = instance.compile_assignments(assignment_set)
    updated_config      = recursive_update(model_dict, incremental_config)   

    if cast_to_base_model == True:
      result = ModelType(**updated_config)
    else:
      result = updated_config

    return result



if __name__ == '__main__':

  prefix_tree = BaseModelTrie.build(SimpleConfig)

  for node in prefix_tree.visit():
    print(node)

  try:
    prefix_tree.generate_assignment('A2_B1', None)
  except (AmbiguousAssignmentError,) as e:
    print(f"{type(e).__name__}: {str(e)}")

  try:
    prefix_tree.generate_assignment('A2_B4', None)
  except (UnassignableError,) as e:
    print(f"{type(e).__name__}: {str(e)}")

  prefix_tree.generate_assignment('A2_B2', None)
  prefix_tree.generate_assignment('A3_U0', None)

  yamldata = textwrap.dedent(
    """
    a3_c1: 1
    a1: 2
    a2:
      b1: 3
      b2: 4
    a3:
      c1: 5
      u0: 6
    a2_b1: 7
    """
  ).strip()

  yamlobj = safe_load(yamldata)
  model_instance = SimpleConfig(**yamlobj)

  assignment_set = {
    'A2_B2': 0,
    'A3_K1_S1': 0,
    'A3_U0': 0
  }
  updated_model = prefix_tree.apply_assignments(model_instance, assignment_set)

  assignment_set = {
    'A3': {
      'k1': {
        's1': 0,
        's2': 0
      },
      'u0': 0,
    }
  }  
  updated_model = prefix_tree.apply_assignments(model_instance, assignment_set)

  assignment_set = {
    'A3': '{"k1":{"s1":0,"s2":0},"u0":0}'
  }
  updated_model = prefix_tree.apply_assignments(model_instance, assignment_set)

  incremental_config = BaseModelTrie.assign(SimpleConfig, assignment_set)
  updated_model      = BaseModelTrie.assign(model_instance, assignment_set)

