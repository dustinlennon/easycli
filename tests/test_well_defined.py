import json
import pytest
import textwrap
import yaml

from easycli.ambiguity_tree import AmbiguityTree

from .site_config import *

#
# fixtures
#

@pytest.fixture
def site_config() -> SiteConfig:
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

  def test_from_model_type(self):
    incremental_config = AmbiguityTree.assign(SiteConfig, {})

    assert isinstance(incremental_config, dict)
    assert not incremental_config

  def test_from_model_instance(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(site_config, {})

    assert isinstance(updated_config, SiteConfig)
    assert updated_config == site_config

  def test_scalar_assign(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'PIDFILE' : '/tmp/site.pid'
      }
    )
    assert isinstance(updated_config, SiteConfig)
    assert updated_config.pidfile == '/tmp/site.pid'

  def test_union_assign(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'SERVER_CONNECTION' : 'http'
      }
    )
    assert isinstance(updated_config, SiteConfig)
    assert isinstance(site_config.server, SslConfig)
    assert isinstance(updated_config.server, HttpConfig)
    assert updated_config.server.connection == 'http'

  def test_logpath_assign_none(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'LOGFILE' : None
      }
    )

    assert isinstance(updated_config.logfile, TemporaryLogfile)
    assert updated_config.logfile.path.startswith("/tmp/EasyCliExample")

  def test_logpath_assign_int(self, site_config: SiteConfig):
    with pytest.raises(ValidationError):
      AmbiguityTree.assign(
        site_config,
        {
          'LOGFILE' : 42
        }
      )

  def test_logpath_assign_str(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'LOGFILE' : '/tmp/EasycliExample.log'
      }
    )

    assert isinstance(updated_config.logfile, PermanentLogfile)

  def test_logpath_assign_perm(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'LOGFILE_PERMANENT': True,
        'LOGFILE_PATH': '/tmp/EasycliExample.log'
      }
    )

    assert isinstance(updated_config.logfile, PermanentLogfile)
    assert updated_config.logfile.path == '/tmp/EasycliExample.log'

  def test_logpath_assign_json(self, site_config: SiteConfig):
    updated_config = AmbiguityTree.assign(
      site_config,
      {
        'LOGFILE' : json.dumps({
          'permanent': True,
          'path': '/tmp/EasycliExample.log'
        })
      }
    )

    assert isinstance(updated_config.logfile, PermanentLogfile)
    assert updated_config.logfile.path == '/tmp/EasycliExample.log'    
