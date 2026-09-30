class ConfigurableException(Exception):
  pass

class UnassignableError(ConfigurableException):
  pass

class AmbiguousAssignmentError(ConfigurableException):
  pass