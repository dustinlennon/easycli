from pydantic import BaseModel, Field
from typing import ClassVar, Literal, Union

from easycli.configurable_model import ConfigurableModel

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
# SiteConfig
#
class SiteConfig(ConfigurableModel, BaseModel):
  prefix              : ClassVar[str] = "EXAMPLE_"

  logfile             : str = "/tmp/example.log"
  server              : Union[HttpConfig, SslConfig] \
                          = Field(discriminator='connection')
