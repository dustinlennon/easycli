import erdantic as erd
from tests.simple_config import SimpleConfig

erd.draw(
  SimpleConfig,
  out="dev/schema.png",
  graph_attr = {"label" :""}
)
