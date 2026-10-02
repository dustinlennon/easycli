from pydantic import BaseModel
from typing import Union

class Uc(BaseModel):
  c1: int
  u0: int

class Ts(BaseModel):
  s1: int
  s2: int

class Uk(BaseModel):
  k1: Ts
  u0: int

class Tb(BaseModel):
  b1: int
  b2: int

class SimpleConfig(BaseModel):
  a1: int
  a2: Tb
  a3: Union[Uc, Uk]
  a2_b1: int
  a3_c1: int
