from pydantic import (
  BaseModel,
  BeforeValidator,
  Field,
  ValidationError
)
import tempfile
from typing import (
  Annotated,
  Literal,
  Union
)

#
# tempdir_factory
#
def tempdir_factory(prefix):
  dirname = tempfile._get_default_tempdir()
  basename = next(tempfile._get_candidate_names())
  return f"{dirname}/{prefix}{basename}"

#
# ensure_logpath
#
def ensure_logpath(value):
  if isinstance(value, dict):
    return value
  elif isinstance(value, str):
    return PermanentLogfile(path = value)
  elif value is None:
    return TemporaryLogfile()
  else:
    raise ValueError(f"unsupported logfile type: '{type(value).__name__}'")

#
# SslConfig
#
class SslConfig(BaseModel):
  connection          : Literal['ssl']
  private_key         : str
  cert_key            : str
  extra_cert_chain    : str
  port                : int = 443

#
# HttpConfig
#
class HttpConfig(BaseModel):
  connection          : Literal['http']
  port                : int = 80

#
# PermanentLogfile
#
class PermanentLogfile(BaseModel):
  permanent   : Literal[True] = True
  path        : str

#
# TemporaryLogfile
#
class TemporaryLogfile(BaseModel):
  permanent   : Literal[False] = False
  prefix      : str = "EasyCliExample."
  path        : str = Field(default_factory = lambda data: tempdir_factory(data['prefix']))

#
# SiteConfig
#
class SiteConfig(BaseModel):
  pidfile             : str = "./test.pid"  
  server              : Union[HttpConfig, SslConfig] \
                          = Field(discriminator='connection')

  logfile             : Annotated[
                          Union[PermanentLogfile, TemporaryLogfile],
                          BeforeValidator(ensure_logpath)
                        ] \
                          = Field(default_factory = TemporaryLogfile, discriminator='permanent')
