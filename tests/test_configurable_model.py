import pytest
import textwrap
from argparse import Namespace

from .site_config import *

#
# fixtures
#

@pytest.fixture
def site_config() -> SiteConfig:
  config = \
    textwrap.dedent(
      """
      logfile: /tmp/site.log
      server:
        connection: ssl
        private_key: ./certificates/ssl/key.pem
        cert_key: ./certificates/ssl/site.crt
        extra_cert_chain: ./pki/intermediate_ca.crt
        port: 4443
      """
    ).strip()
  
  return SiteConfig.from_yaml(config)

#
# > TestSiteConfig
#
class TestSiteConfig:
  def test_from_yaml(self, site_config: SiteConfig):
    assert isinstance(site_config, SiteConfig)
    assert isinstance(site_config, BaseModel)
    assert isinstance(site_config, ConfigurableMixin)

  def test_from_env(self, site_config: SiteConfig):
    env = {
      'EXAMPLE_SERVER_CONNECTION'  : 'http',
      'EXAMPLE_LOGFILE'            : '/tmp/site.log'
    }
    updated_config = site_config.update_from_env(env)
    assert isinstance(updated_config.server, HttpConfig)
    assert updated_config.logfile == '/tmp/site.log'

  def test_from_args(self, site_config: SiteConfig):
    args = Namespace(
      EXAMPLE_SERVER_CONNECTION = 'http',
      EXAMPLE_LOGFILE = '/tmp/site.log'
    )
    updated_config = site_config.update_from_args(args)
    assert isinstance(updated_config.server, HttpConfig)
    assert updated_config.logfile == '/tmp/site.log'

  def test_chain(self, site_config: SiteConfig):
    env = {
      'EXAMPLE_SERVER_CONNECTION'  : 'http',
      'EXAMPLE_LOGFILE'            : '/tmp/site-env.log'
    }
    args = Namespace(
      EXAMPLE_LOGFILE = '/tmp/site-args.log'
    )

    sc_env  = site_config.update_from_env(env)
    sc_args = sc_env.update_from_args(args)
    


