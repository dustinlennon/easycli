from collections import defaultdict
import itertools
import json
from pydantic import (
  BaseModel
)
import pytest
import textwrap
from typing import ClassVar

from easycli.configurable.model import ConfigurableModel
from easycli.configurable.exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)
from easycli.configurable.ambiguity_tree import AmbiguityTree
from easycli.utils.json_encoder import TypenameJSONEncoder

#
# > Test models
#
class Stem(BaseModel):
  one             : int
  three           : int

class Mix(ConfigurableModel, BaseModel):
  env_prefix      : ClassVar[str] = "TKAP_MIX_"
  stem            : Stem
  stem_one        : int
  stem_two        : int


#
# fixtures
#
@pytest.fixture
def mix_config():
  mix_config = textwrap.dedent(
    """
    stem:
      one: 1
      three: 3
    stem_one: 1
    stem_two: 2
    """
  ).strip()
  return mix_config


# class TestEnvFieldPairs:

#   #
#   # > test_stem_one
#   #
#   def test_stem_one(self):
#     env = dict(TKAP_MIX_STEM_ONE = 1)
#     efp = list(Mix.env_field_pairs(env = env))

#     assert efp[0][0][0] == 'TKAP_MIX_STEM_ONE'
#     assert efp[0][0][1] == 1
#     assert efp[0][1]    == 'stem'

#     assert efp[1][0][0] == 'TKAP_MIX_STEM_ONE'
#     assert efp[1][0][1] == 1
#     assert efp[1][1]    == 'stem_one'

#   #
#   # > test_stem_two
#   #

#   def test_stem_two(self):
#     env = dict(TKAP_MIX_STEM_TWO = 2)
#     efp = list(Mix.env_field_pairs(env = env))

#     assert efp[0][0][0] == 'TKAP_MIX_STEM_TWO'
#     assert efp[0][0][1] == 2
#     assert efp[0][1]    == 'stem'

#     assert efp[1][0][0] == 'TKAP_MIX_STEM_TWO'
#     assert efp[1][0][1] == 2
#     assert efp[1][1]    == 'stem_two'

#   #
#   # > test_stem_three
#   #

#   def test_stem_three(self):
#     env = dict(TKAP_MIX_STEM_THREE = 3)
#     efp = list(Mix.env_field_pairs(env = env))

#     assert efp[0][0][0] == 'TKAP_MIX_STEM_THREE'
#     assert efp[0][0][1] == 3
#     assert efp[0][1]    == 'stem'

#   #
#   # > test_stem_four
#   #
#   def test_stem_four(self):
#     env = dict(TKAP_MIX_STEM_FOUR = 4)
#     efp = list(Mix.env_field_pairs(env = env))

#     assert efp[0][0][0] == 'TKAP_MIX_STEM_FOUR'
#     assert efp[0][0][1] == 4
#     assert efp[0][1]    == 'stem'


class TestAmbiguityTree:

  def print_rtree(self, rtree):
    print(
      "\nrtree: {json}".format(
        json = json.dumps(rtree , cls = TypenameJSONEncoder, indent = 2)
      )
    )

  #
  # > test_build_stem_one
  #
  def test_build_stem_one(self):
    atree = AmbiguityTree._build(Mix, "STEM_ONE")
    assert atree[Mix]['stem'][Stem]['one'] is None
    assert atree[Mix]['stem_one'] is None

  #
  # > test_build_stem_two
  #
  def test_build_stem_two(self):
    atree = AmbiguityTree._build(Mix, "STEM_TWO")
    assert 'stem' not in atree[Mix]
    assert atree[Mix]['stem_two'] is None

  #
  # > test_build_stem_three
  #
  def test_build_stem_three(self):
    atree = AmbiguityTree._build(Mix, "STEM_THREE")
    assert atree[Mix]['stem'][Stem]['three'] is None

  #
  # > test_build_stem_four
  #
  def test_build_stem_four(self):
    with pytest.raises(UnassignableError):
      AmbiguityTree._build(Mix, "STEM_FOUR")

  #
  # > test_resolve_stem_one
  #
  def test_resolve_stem_one(self):
    atree = AmbiguityTree._build(Mix, 'STEM_ONE')

    with pytest.raises(AmbiguousAssignmentError):
      rtree = atree._resolve()

  #
  # > test_resolve_stem_two
  #
  def test_resolve_stem_two(self):
    atree = AmbiguityTree._build(Mix, 'STEM_TWO')
    rtree = atree._resolve()

    assert 'stem' not in rtree
    assert rtree['stem_two'] is None

  #
  # > test_resolve_stem_three
  #
  def test_resolve_stem_three(self):
    atree = AmbiguityTree._build(Mix, 'STEM_THREE')
    rtree = atree._resolve()
    
    assert rtree['stem']['three'] is None
    assert 'stem_three' not in rtree

  #
  # > test_assign
  #
  def test_assign(self):
    merged_config = AmbiguityTree.assign(Mix, {'STEM_TWO' : 2, 'STEM_THREE' : 3})

    assert merged_config['stem_two'] == 2
    assert merged_config['stem']['three'] == 3
 

# class TestUpdateFromEnv:
#   #
#   # > test_ambiguous_assignment_error
#   #
#   def test_ambiguous_assignment_error(self, mix_config):
#     env = dict(TKAP_MIX_STEM_ONE = 1)
#     mc = Mix.from_buffer(mix_config)

#     with pytest.RaisesGroup(configurable_exceptions.AmbiguousAssignmentError):
#       mc.update_from_env(env = env)

#   #
#   # > test_unassignable_error
#   #
#   def test_unassignable_error(self, mix_config):
#     env = dict(TKAP_MIX_STEM_FOUR = 4)
#     mc = Mix.from_buffer(mix_config)

#     with pytest.RaisesGroup(configurable_exceptions.UnassignableError):
#       mc.update_from_env(env = env)
