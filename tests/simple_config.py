from pydantic import (
  BaseModel,
  Field
)

from typing import (
  Literal,
  Optional,
  Union
)

class Span(BaseModel):
  length    : int
  width     : int

class Imperial(BaseModel):
  system    : Literal['FPS']
  time      : float
  span      : Optional[Span] = None

class Metric(BaseModel):
  system    : Literal['MKS']
  time      : float
  span      : Span

class Tb(BaseModel):
  b1        : int
  b2        : int

class SimpleConfig(BaseModel):
  a1        : int
  a2        : Tb
  a3        : Union[Metric, Imperial] = \
                Field(discriminator='system')
  a2_b1     : int
