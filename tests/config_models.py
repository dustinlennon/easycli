from pydantic import (
  BaseModel,
  BeforeValidator,
  Field
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
  if isinstance(value, str):
    return PermanentLogging(permanent = True, path = value)
  elif value is None:
    return TemporaryLogging()
  else:
    return value

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
# PermanentLogging
#
class PermanentLogging(BaseModel):
  permanent   : Literal[True]
  path        : str

#
# TemporaryLogging
#
class TemporaryLogging(BaseModel):
  permanent   : Literal[False] = False
  prefix      : str = "tkap."
  path        : str = Field(default_factory = lambda data: tempdir_factory(data['prefix']))

#
# SiteConfig
#
class SiteConfig(BaseModel):
  pidfile             : str = "./test.pid"  
  server              : Union[HttpConfig, SslConfig] \
                          = Field(discriminator='connection')

  logging             : Annotated[
                          Union[PermanentLogging, TemporaryLogging],
                          BeforeValidator(ensure_logpath)
                        ] \
                          = Field(default_factory = TemporaryLogging, discriminator='permanent')
