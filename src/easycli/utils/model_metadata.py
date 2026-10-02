from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typing import (
  Any,
  Dict,
  get_args,
  List,
)

def model_metadata(field_info: FieldInfo) -> List[Dict[str, Any]]:
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
 
  return model_metadata
