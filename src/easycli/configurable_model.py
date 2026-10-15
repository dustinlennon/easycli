from pydantic import BaseModel
from .configurable_mixin import ConfigurableMixin

#
# > ConfigurableModel
#
from pydantic._internal._model_construction import ModelMetaclass

class _ConfigurableModelMeta(ModelMetaclass, type):
  pass

class ConfigurableModel(ConfigurableMixin, BaseModel, metaclass = _ConfigurableModelMeta):
  pass
