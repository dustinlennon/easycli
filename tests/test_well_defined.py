from collections import defaultdict
import json
import pytest
import textwrap
import yaml

from easycli.configurable.ambiguity_tree import AmbiguityTree

from .config_models import *

#
# fixtures
#

@pytest.fixture
def site_config():
  obj = yaml.safe_load(
    textwrap.dedent(
      """
      logging: /tmp/site.log
      pidfile: ./run/site.pid
      server:
        connection: ssl
        private_key: ./certificates/ssl/key.pem
        cert_key: ./certificates/ssl/site.crt
        extra_cert_chain: ./pki/intermediate_ca.crt
        port: 4443
      """
      ).strip()
  )

  return SiteConfig(**obj)

#
# > TestAmbiguityTree
#
class TestAmbiguityTree:

  def test_assign_on_model_type(self):
    incremental_config = AmbiguityTree.assign(
      SiteConfig,
      {
        'SERVER_CONNECTION' : 'http'
      }
    )
    assert incremental_config['server']['connection'] == 'http'

  def test_assign_on_model_instance(self, site_config: SiteConfig):
    assert isinstance(site_config.server, SslConfig)

    site = AmbiguityTree.assign(
      site_config,
      {
        'SERVER_CONNECTION' : 'http'
      }
    )

    assert isinstance(site, SiteConfig)
    assert isinstance(site.server, HttpConfig)
    # assert isinstance(site.logging, TemporaryLogging)
    # assert site.logging.path.startswith("/tmp/tkap.")

  # def test_resolvable_union(self):
  #   atree = AmbiguityTree(SiteConfig, "SERVER_CONNECTION", AmbiguityTree._INIT_TOKEN)
  #   print(atree)