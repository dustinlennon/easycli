
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
a1: 2
a2:
  b1: 3
  b2: 4
a2_b1: 7
a3:
  system: FPS
  time: 60
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
```

