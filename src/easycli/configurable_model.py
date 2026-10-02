from collections import defaultdict
import itertools
import json
import os
from pydantic import (
  BaseModel,
  ConfigDict,
  ValidationError
)
from types import SimpleNamespace
from typing import (
  get_args,
  Iterator,
  Protocol,
  Tuple,
  TYPE_CHECKING
)
import warnings
import yaml

from .ambiguity_tree import AmbiguityTree
from .exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)

#
# yaml setup
#
try:
  from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
  from yaml import Loader, Dumper

#
# linter setup
#
if TYPE_CHECKING: 
  class ConfigurableInstance("ConfigurableModel", BaseModel, Protocol):
    pass

#
# warnings setup
#
def custom_formatwarning(msg, category, filename, lineno, line=None):
    return f"{filename}:{lineno}: {category.__name__}: {msg}\n"
warnings.formatwarning = custom_formatwarning

#
# > ConfigurableModel
#
class ConfigurableModel(object):
  model_config = ConfigDict(validate_assignment=True)

  @classmethod
  def from_yamlfile[T](cls: type[T], yamlfile) -> T:
    with open(yamlfile) as fp:
      data = yaml.load(fp, Loader = Loader)
    return cls(**data)

  @classmethod
  def from_buffer[T](cls: type[T], buffer) -> T:
    data = yaml.safe_load(buffer)
    return cls(**data)

  @classmethod
  def fields[T:BaseModel](cls: type[T]) -> Iterator[str]:
    return cls.model_fields.keys()

  # @classmethod
  # def env_field_pairs(cls, env):
  #   tkap_env = { k:v for k,v in env.items() if k.startswith("TKAP") }

  #   def test_func(env_kvp: Tuple[str,str], field_name: str):
  #     return env_kvp[0].removeprefix(cls.env_prefix).startswith(field_name.upper())
    
  #   env_kvpairs = [ (k,v) for k,v in tkap_env.items() ]

  #   return filter(
  #     lambda p: test_func(*p),
  #     itertools.product(env_kvpairs, cls.model_fields.keys())
  #   )

  def update_from_env[T:ConfigurableInstance](self: T, env = None) -> T:
    raise NotImplementedError("update_from_env: awaiting AmbiguityTree refactor")
    cls = type(self)
    env = os.environ if env is None else env
   
    # efp = list(cls.env_field_pairs(env))


  def update_from_args[T:ConfigurableInstance](self: T, args: SimpleNamespace) -> T:
    raise NotImplementedError("update_from_args: awaiting AmbiguityTree refactor")

