import argparse
import io
import os
from pydantic import (
  BaseModel,
  ConfigDict
)
from typing import (
  Protocol,
  TYPE_CHECKING,
  Union
)
import warnings
import yaml

from easycli.configuration_builder import ConfigurationBuilder

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
  prefix: str
  model_config = ConfigDict(validate_assignment=True)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    ModelType = type(self)
    self._builder = ConfigurationBuilder.build(ModelType)

  @classmethod
  def from_yaml[T:ConfigurableInstance](
      cls: type[T],
      yaml: str
    ) -> T:
    instance = cls.from_yaml_source(
      io.StringIO(yaml)
    )
    return instance

  @classmethod
  def from_yaml_source[T:ConfigurableInstance](
      cls: type[T],
      yaml_source: Union[str, io.TextIOBase]
    ) -> T:
    if isinstance(yaml_source, io.TextIOBase):
      obj = yaml.safe_load(yaml_source)
    else:
      with open(yaml_source) as fp:
        obj = yaml.safe_load(fp)       
    return cls(**obj)

  def update_from_dict[T:ConfigurableInstance](
      self: T,
      args: dict[str, str],
      *,
      fallback: bool,
      discard: bool
    ) -> T:
    assignment_set = { 
      k.removeprefix(self.prefix):v
      for k,v in args.items()
      if k.startswith(self.prefix)
    }
    return self._builder.apply_assignments(self, assignment_set, fallback = fallback, discard = discard)

  def update_from_env[T:ConfigurableInstance](
      self: T,
      env = None
    ) -> T:
    env = os.environ.copy() if env is None else env
    return self.update_from_dict(env, fallback = False, discard = False)

  def update_from_args[T:ConfigurableInstance](
      self: T,
      args: argparse.Namespace,
      fallback: bool = True,
      discard: bool = False
    ) -> T:
      return self.update_from_dict(vars(args), fallback = True, discard = False)

