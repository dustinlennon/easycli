import functools
import json
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typing import (
  Any,
  Dict,
  get_args, 
  overload,
  List,
  Tuple,
  Type,
  Union
)

from .exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)
from .utils.recursive_update import recursive_update
from .utils.json_encoder import TypenameJSONEncoder

#
# > AmbiguityTree
#
class AmbiguityTree(object):
  _INIT_TOKEN = object()

  def __init__(
      self,
      ModelType: Type[BaseModel],
      attr_path: str,
      token: object
    ):
    if token is not self.__class__._INIT_TOKEN:
      raise RuntimeError("'AmbiguityTree.__init__' is not intended to be called by client code")

    node = dict()
    assignable = self._build_recurse(node, ModelType, attr_path)

    if assignable == False:
      raise UnassignableError(
        ":{0} {1}".format(
          ModelType.__name__,
          attr_path
        )
      )
    
    self.root       = node
    self.model_type = ModelType
    self.attr_path  = attr_path


  def __repr__(self):
    return "{json}".format(
      json = json.dumps(self.root, cls = TypenameJSONEncoder)
    )

  def __str__(self):
    return "\n{json}".format(
      json = json.dumps(self.root, cls = TypenameJSONEncoder, indent = 2)
    )

  def __getitem__(self, key):
    return self.root[key]

  @overload
  @classmethod
  def assign[B:BaseModel](cls, model_or_type: B, attr_paths: Dict[str,Any]) -> B: ...

  @overload
  @classmethod
  def assign[B:BaseModel](cls, model_or_type: type[B], attr_paths: Dict[str,Any]) -> Dict: ...

  @classmethod
  def assign[B: BaseModel](
    cls,
    model_or_type: Union[B, Type[B]],
    attr_paths: Dict[str, Any]
  ) -> Union[B, Dict]:    
    if isinstance(model_or_type, BaseModel):
      model = model_or_type.model_dump()
      ModelType = type(model_or_type)
      cast_to_base_model = True

    elif issubclass(model_or_type, BaseModel):
      model = dict()
      ModelType = model_or_type
      cast_to_base_model = False

    else:
      raise TypeError(
        f"AmbiguityTree.assign: 'model_or_type' must be an instance of subclass of BaseModel: {type(T)}"
      )

    partial_config = dict()
    for attr_path, value in attr_paths.items():
      # instance = cls(ModelType, attr_path, token = cls._INIT_TOKEN)
      instance = cls._build(ModelType, attr_path)
      partial_config[attr_path] = instance._resolve(value)

    merged_config = functools.reduce(
      functools.partial(recursive_update, discard = True),
      partial_config.values(),
      model,
    )

    if cast_to_base_model == True:
      result = ModelType(**model)
    else:
      result = merged_config

    return result
  
  @classmethod
  def _build(
    cls,
    ModelType: Type[BaseModel],
    attr_path: str
  ):
    return cls(ModelType, attr_path, token = cls._INIT_TOKEN)

  def _build_recurse(
    self,
    node: dict,
    ModelType: Type[BaseModel],
    attr_path: str
  ):
    """
    Trace the attr_path to be assigned and construct the corresponding tree.  Due to 
    the parsing specification, i.e. FIELD_SUBFIELD_SUBSUBFIELD_..., ambiguities may 
    arise when prefixes are shared.  For example, when setting STEM_ONE, that can mean 
    either `stem_one` or `stem.one`.  When both are available in the data structure, 
    we will want to raise an exception.

    {
      "tests.test_ill_defined.Mix": {
        "stem": {
          "tests.test_ill_defined.Stem": {
            "one": null
          }
        },
        "stem_one": null
      }
    }

    However, there's another consideration, specifically, support for type unions. For
    example, abridged from the test code:

    > class SslConfig(BaseModel):
    >   connection          : Literal['ssl']
    >   private_key         : str
    >   cert_key            : str
    >   extra_cert_chain    : str
    >   port                : int = 443
    > 
    > class HttpConfig(BaseModel):
    >   connection          : Literal['http']
    >   port                : int = 80
    > 
    > class SiteConfig(BaseModel):
    >   server              : Union[HttpConfig, SslConfig] = Field(discriminator='connection')
    >

    The utility is that one may set SERVER_CONNECTION and obtain different behavior.  This
    generates a tree similar to the above, but, in this case, the result is resolvable:

    {
      "tests.config_models.SiteConfig": {
        "server": {
          "tests.config_models.HttpConfig": {
            "connection": null
          },
          "tests.config_models.SslConfig": {
            "connection": null
          }
        }
      }
    }

    """
    made_assignment = False

    if ModelType in node:
      raise AssertionError("AmbiguityTree._build_recurse: unexpected condition")
    node[ModelType] = dict()

    for field_name, field_info in ModelType.model_fields.items():
      fnup = field_name.upper()
      
      # assign
      if attr_path == fnup:
        node[ModelType][field_name] = None
        made_assignment = True

      # recurse
      elif attr_path.startswith(fnup):
        subpath = attr_path.removeprefix( f"{fnup}_" )

        for mm in self._model_metadata(field_info):
          subnode = dict()
          SubModelType = mm['model']
          if self._build_recurse(subnode, SubModelType, subpath):
            # Create `node[ModelType][field_name]` only if it makes an assignment;
            # moreover, and in general as with a type Union, there are multiple 
            # recursive calls required to update the dictionary at
            # `node[ModelType][field_name]`
            node[ModelType].setdefault(field_name, dict())
            recursive_update(node[ModelType][field_name], subnode, discard = False)
            made_assignment = True

    return made_assignment

  def _model_metadata(self, field_info: FieldInfo) -> List[Dict[str, Any]]:
    annotation = field_info.annotation

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
      members = [ annotation ]
    else:
      members = get_args(annotation)

    model_metadata = [
      {
        "model": member,
        "fields": list(member.model_fields.keys())
      }
      for member in members
      if isinstance(member, type) and issubclass(member, BaseModel)
    ]

    if len(model_metadata) == 0:
      raise AssertionError(f"unexpected annotation structure: {annotation}")
    
    return model_metadata

  def _resolve(
    self,
    value = None
  ):
    node  = dict()
    key = self.model_type.__name__

    self._resolve_recurse(node, key, self.root, value)

    fac = self._assigned_field_count(node)

    import pdb; pdb.set_trace()

    if fac == 0:
      raise UnassignableError(
        ":{0} {1}".format(
          self.model_type.__name__,
          self.attr_path
        )
      )
    elif fac >= 2:
      raise AmbiguousAssignmentError(
        ":{0} {1}".format(
          self.model_type.__name__,
          self.attr_path
        )
      )

    return node[key]

  def _resolve_recurse(
      self,
      node: dict,
      key,
      root,
      value
    ):
    """
    Resolve ambiguity trees where possible.  For example,

    {
      "tests.config_models.SiteConfig": {
        "server": {
          "tests.config_models.HttpConfig": {
            "connection": null
          },
          "tests.config_models.SslConfig": {
            "connection": null
          }
        }
      }
    }

    collapses to

    {
      "server": {
        "connection": "http"
      }
    }

    """
    if not isinstance(root, dict):
      try:
        node[key] = json.loads(value)
      except json.JSONDecodeError:
        node[key] = value

    else:
      node[key] = dict()

      for akey, subdata in root.items():
        if isinstance(akey, type) and issubclass(akey, BaseModel):
          obj = dict()
          self._resolve_recurse(obj, key, subdata, value)
          node[key].update( obj[key] )

        else:
          obj = dict()
          self._resolve_recurse(obj, akey, subdata, value)
          node[key][akey] = obj[akey]
           
  def _assigned_field_count(self, root):
    count = 0

    if not isinstance(root, dict):
      count = 1
    
    else:
      for key, subnode in root.items():
        count = count + self._assigned_field_count(subnode)

    return count

