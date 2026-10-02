
EasyCLI
====

A pedagogical example: `SimpleConfig` contains nested schemas, a type union, an apparent assignment ambiguity, and an unresolvable assignment ambiguity.

![SimpleConfig schema](dev/schema.png)

Runtime Configuration
----

Specifying runtime configuration typically involves one or more static config files, a collection of environment variables, and command line arguments.  Priority is, generally, in the same order: environment variables override static config files, and command line arguments override environment variables.  For `SimpleConfig`, this might look like:

### config.yaml

```config.yaml
# config.yaml
a3_c1: 1
a1: 2
a2:
  b1: 3
  b2: 4
a3:
  c1: 5
  u0: 6
a2_b1: 7
```

### environment variables

```
CUSTOM_PREFIX_A2_B2=40
```

### cli args

In python, this is most easily handled by the `argparse` library.

```bash
app --a2-b2 400
```

Using Pydantic
----

The `SimpleConfig` data structure is easily specified using the pydantic package.  

```python
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
```

