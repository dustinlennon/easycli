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
import yaml

from easycli.configuration_builder import ConfigurationBuilder

#
# > ConfigurableMixin
#
class ConfigurableMixin:
  prefix        : str
  model_config  : ConfigDict

  @classmethod
  def from_yaml[T:"ConfigurableModel"](
      cls: type[T],
      yaml: str
    ) -> T:
    instance = cls.from_yaml_source(
      io.StringIO(yaml)
    )
    return instance

  @classmethod
  def from_yaml_source[T:"ConfigurableModel"](
      cls: type[T],
      yaml_source: Union[str, io.TextIOBase]
    ) -> T:
    if issubclass(cls, BaseModel) == False:
      raise TypeError("ConfigurableMixin requires a pydantic.BaseModel")

    if isinstance(yaml_source, io.TextIOBase):
      obj = yaml.safe_load(yaml_source)
    else:
      with open(yaml_source) as fp:
        obj = yaml.safe_load(fp)

    instance = cls(**obj)
    instance._builder = ConfigurationBuilder.build(cls)

    return instance
    
  def update_from_dict[T:"ConfigurableModel"](
      self: T,
      args: dict[str, str],
      *,
      fallback: bool,
      discard: bool
    ) -> T:
    if isinstance(self, BaseModel) == False:
      raise TypeError("ConfigurableMixin requires a pydantic.BaseModel")

    assignment_set = { 
      k.removeprefix(self.prefix):v
      for k,v in args.items()
      if k.startswith(self.prefix)
    }
    return self._builder.apply_assignments(self, assignment_set, fallback = fallback, discard = discard)

  def update_from_env[T:"ConfigurableModel"](
      self: T,
      env = None
    ) -> T:
    env = os.environ.copy() if env is None else env
    return self.update_from_dict(env, fallback = False, discard = False)

  def update_from_args[T:"ConfigurableModel"](
      self: T,
      args: argparse.Namespace
    ) -> T:
      return self.update_from_dict(vars(args), fallback = True, discard = False)

#
# > ConfigurableModel (annotation)
#
from pydantic._internal._model_construction import ModelMetaclass

class _ConfigurableModelMeta(ModelMetaclass, type):
  pass

class ConfigurableModel(ConfigurableMixin, BaseModel, metaclass = _ConfigurableModelMeta):
  pass
