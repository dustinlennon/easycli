import pytest

from easycli.utils.recursive_update import recursive_update

@pytest.fixture
def dest():
  return {'a1': 2, 'a2': {'b1': 3, 'b2': 4}, 'a3': {'system': 'FPS', 'time': 60.0, 'span': None}, 'a2_b1': 7}

@pytest.fixture
def src():
  return {'a2': {'b2': 0}, 'a3': {'time': 10}}


def test_recursive_update(dest, src):
  recursive_update(dest, src, discard = False, fallback = False)
  assert dest == {'a1': 2, 'a2': {'b1': 3, 'b2': 0}, 'a3': {'system': 'FPS', 'time': 10, 'span': None}, 'a2_b1': 7}