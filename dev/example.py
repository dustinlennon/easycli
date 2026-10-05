import argparse

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
#
# build_parser
#
def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--config",
    default = "dev/config.yaml"
  )

  parser.add_argument(
    "--connection",
    dest = 'EXAMPLE_SERVER_CONNECTION'
  )

  return parser

#
# cli
#
def cli():
  """
  invoke:
    $ poetry run python3 dev/example.py --config ./dev/config.yaml
  """
  parser = build_parser()
  args = parser.parse_args()

  site_config = (
    SiteConfig
      .from_yaml_source(args.config)
      .update_from_env()
      .update_from_args(args)
  )
      
  print(repr(site_config))


#
# __main__
#
if __name__ == '__main__':
  cli()
