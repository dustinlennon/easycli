def recursive_update(a: dict, b: dict, *, discard = False, path=[]):
  """
  In-place recursive update:

  'a' will be modified, in general
  None values in 'b' will remove corresponding keys in 'a' if discard == True

  """
  for key in b:
    if key in a:
      if isinstance(a[key], dict) and isinstance(b[key], dict):
        recursive_update(
          a[key], b[key],
          discard = discard,
          path = path + [str(key)]
        )

      elif a[key] != b[key] and b[key] is None and discard == True:
        a.pop(key, None)

      elif a[key] != b[key]:
        a[key] = b[key]
        
    elif b[key] is None and discard == True:
      a.pop(key, None)

    else:
      a[key] = b[key]

  return a
