from pydantic import (
  ValidationError
)
import pytest
import textwrap
from yaml import safe_load

from easycli.configuration_builder import ConfigurationBuilder
from easycli.exceptions import (
  AmbiguousAssignmentError,
  UnassignableError
)
from tests.simple_config import SimpleConfig, Imperial, Metric

@pytest.fixture
def builder() -> ConfigurationBuilder[SimpleConfig]:
  return ConfigurationBuilder.build(SimpleConfig)

@pytest.fixture
def model_instance():
  yamldata = textwrap.dedent(
    """
    a1: 2
    a2:
      b1: 3
      b2: 4
    a2_b1: 7
    a3:
      system: FPS
      time: 60
    """
  ).strip()

  yamlobj = safe_load(yamldata)
  return SimpleConfig(**yamlobj)

#
# > TestConfigurationBuilder
#
class TestConfigurationBuilder:
  def test_build(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):     
    assert builder.trie.root.children.keys() == set(['A1', 'A2', 'A3'])

  def test_raises_ambiguous_assignment_error(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):
    with pytest.raises(AmbiguousAssignmentError):
      builder.generate_assignment('A2_B1', None)

  def test_raises_unassignable_error(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):
    with pytest.raises(UnassignableError):
      builder.generate_assignment('A2_B4', None)

  def test_generate_assignment(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):
    assignment = builder.generate_assignment('A2_B2', None)
    assert assignment['a2']['b2'] == None

  def test_generate_assignment_in_type_union(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):
    assignment = builder.generate_assignment('A3_SYSTEM', 'FPS')
    assert assignment['a3']['system'] == 'FPS'

  def test_compile_assignments(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):           
    assignment_set = {
      'A2_B2': None,
      'A3_SYSTEM': 'FPS',
    }
    partial_config = builder.compile_assignments(assignment_set)
    assert partial_config == {'a2': {'b2': None}, 'a3': {'system': 'FPS'}}

  def test_compile_assignments_raises_value_error(
      self,
      builder: ConfigurationBuilder[SimpleConfig]
    ):           
    assignment_set = {
      'A2': None,
      'A2_B2': 0,
    }
    with pytest.raises(ValueError):
      builder.compile_assignments(assignment_set)

  def test_apply_assignments(
      self,
      builder: ConfigurationBuilder[SimpleConfig],
      model_instance: SimpleConfig
    ):           
    assignment_set = {
      'A2_B2': 0,
      'A3_TIME': 10
    }
    updated_model = builder.apply_assignments(model_instance, assignment_set, discard = False, fallback = False)

    assert updated_model.a2.b2 == 0
    assert isinstance(updated_model.a3, Imperial)
    assert updated_model.a3.time == 10

  def test_apply_assignments_for_type_union(
      self,
      builder: ConfigurationBuilder[SimpleConfig],
      model_instance: SimpleConfig
    ):           
    assert isinstance(model_instance.a3, Imperial)

    assignment_set = {
      'A3_SYSTEM': 'MKS',
      'A3_SPAN_LENGTH': 5,
      'A3_SPAN_WIDTH': 6
    }
    
    updated_model = builder.apply_assignments(model_instance, assignment_set, discard = False, fallback = False)
    assert isinstance(updated_model.a3, Metric)
    assert updated_model.a3.span.length == 5
    assert updated_model.a3.span.width == 6

  def test_apply_assignments_for_type_union_raises_validation_error(
      self,
      builder: ConfigurationBuilder[SimpleConfig],
      model_instance: SimpleConfig
    ):           
    assignment_set = {
      'A3_SYSTEM': 'MKS'
    }
    with pytest.raises(ValidationError):
      updated_model = builder.apply_assignments(model_instance, assignment_set, discard = False, fallback = False)

  def test_apply_assignments_dict(
      self,
      builder: ConfigurationBuilder[SimpleConfig],
      model_instance: SimpleConfig
    ):
    assignment_set = {
      'A3': {
        'system': 'MKS',
        'span' : {
          'length': 5,
          'width': 6
        }
      }
    }  
    updated_model = builder.apply_assignments(model_instance, assignment_set, discard = False, fallback = False)
    assert isinstance(updated_model.a3, Metric)
    assert updated_model.a3.span.length == 5
    assert updated_model.a3.span.width == 6

  def test_apply_assignments_json(
      self,
      builder: ConfigurationBuilder[SimpleConfig],
      model_instance: SimpleConfig
    ):      
    assignment_set = {
      'A3': '{"system":"MKS","time":60.0,"span":{"length":5,"width":6}}'
    }
    updated_model = builder.apply_assignments(model_instance, assignment_set, discard = False, fallback = False)
    assert isinstance(updated_model.a3, Metric)
    assert updated_model.a3.span.length == 5
    assert updated_model.a3.span.width == 6

  def test_assign_with_model_type(self):
    assignment_set = {
      'A2_B2': None,
      'A3_SYSTEM': 'FPS',
    }

    partial_config = ConfigurationBuilder.assign(SimpleConfig, assignment_set)
    assert partial_config == {'a2': {'b2': None}, 'a3': {'system': 'FPS'}}

  def test_assign_with_model_instance(
      self,
      model_instance: SimpleConfig
    ):
    assignment_set = {
      'A2_B2': 42,
      'A3_SYSTEM': 'FPS',
    }

    updated_model = ConfigurationBuilder.assign(model_instance, assignment_set)
    assert updated_model.a2.b2 == 42
    assert updated_model.a3.system == 'FPS'
    assert isinstance(updated_model.a3, Imperial)

  def test_assign(
      self,
      model_instance: SimpleConfig
    ):
    assignment_set = {
      'config': './dev/config.yaml',
      'A2_B2': 42,
    }

    with pytest.raises(UnassignableError):
      ConfigurationBuilder.assign(model_instance, assignment_set)

