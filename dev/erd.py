import erdantic as erd
from tests.simple_config import SimpleConfig
from tests.site_config import SiteConfig

erd.draw(
  SimpleConfig,
  out="dev/simple_config.png",
  graph_attr = {"label" :""}
)

erd.draw(
  SiteConfig,
  out="dev/site_config.png",
  graph_attr = {"label" :""}
)
